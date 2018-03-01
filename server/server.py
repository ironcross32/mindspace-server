"""Provides the Server class."""

import logging
import os.path
from time import time
from datetime import datetime
from json import dumps, loads
from msgpack.exceptions import UnpackException
from autobahn.twisted.websocket import (
    WebSocketServerProtocol, WebSocketServerFactory
)
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, protocol, endpoints, task
from twisted.web.server import Site
from .protocol import interface_sound, message
from .sound import get_sound
from .parsers import login_parser, transmition_parser
from .db import (
    Session, session, Object, Player, ServerOptions, BannedIP, LoggedCommand
)
from .web.app import app
from .web import routes  # noqa

logger = logging.getLogger(__name__)


@transmition_parser.command
def transmit(udp, host, port, type, id, data):
    """Send data out to players."""
    player = Player.query(transmition_id=id).first()
    if player is None:
        return  # Just drop it.
    con = player.object.get_connection()
    if con is None or con.host != host:
        return logger.warning(
            '%s:%d attempted to transmit as %r.', host, port, player
        )
    player_obj = player.object
    if player.transmition_banned:
        return  # They've been naughty.
    args = [
        Object.connected.is_(True),
        Object.player_id.isnot(None)
    ]
    if not player_obj.monitor_transmitions:
        args.append(Object.id.isnot(player_obj.id))
    for obj in player_obj.get_visible(*args):
        obj_con = obj.get_connection()
        udp.transport.write(
            login_parser.prepare_data(type, player_obj.id, data),
            (obj_con.host, server.udp_port)
        )


class Server:
    def __init__(self):
        """Leave everything in one place."""
        self.started = None
        self.logged_players = set()
        self.connections = []
        self.tcp_factory = ServerFactory()
        self.udp_factory = UDPProtocol()

    def start_listening(self, private_key, certificate_key):
        """Start everything listening."""
        self.started = datetime.utcnow()
        o = ServerOptions.get()
        self.udp_port = o.udp_port
        self.tcp_listener = reactor.listenTCP(
            o.port, self.tcp_factory, interface=o.interface
        )
        logger.info(
            'Now listening on %s:%d.',
            self.tcp_listener.interface, self.tcp_listener.port
        )
        if private_key is None and certificate_key is None:
            self.web_endpoint = endpoints.TCP4ServerEndpoint(
                reactor, o.http_port, interface=o.interface
            )
        elif private_key is None or certificate_key is None:
            logger.critical(
                'Both private key file and certificate key file must be '
                'provided.'
            )
            raise SystemExit
        else:
            self.web_endpoint = endpoints.serverFromString(
                reactor, f'ssl:{o.http_port}:'
                f'interface={o.interface}:privateKey={private_key}:'
                f'certKey={certificate_key}'
            )
        self.site = Site(app.resource())
        d = self.web_endpoint.listen(self.site)
        d.addErrback(logger.warning)
        d.addCallback(
            lambda value: logger.info(
                'Web server listening on %s:%d.', value.interface, value.port
            )
        )
        self.websocket_factory = WebSocketServerFactory(
            f'ws://{o.interface}:{o.websocket_port}'
        )
        self.websocket_factory.protocol = MindspaceWebSocketProtocol
        self.websocket_listener = reactor.listenTCP(
            o.websocket_port, self.websocket_factory, interface=o.interface
        )
        logger.info(
            'Listening for web sockets on %s:%d.',
            self.websocket_listener.interface, self.websocket_listener.port
        )
        self.udp_factory = UDPProtocol()
        self.udp_listener = reactor.listenUDP(self.udp_port, self.udp_factory)
        logger.info('UDP listening on port %d.', self.udp_listener.port)
        self.clear_transferred = task.LoopingCall(self.clear_udp_transferred)
        self.clear_transferred.start(1.0, now=False)

    def clear_udp_transferred(self):
        """Clear transfer logs so that clients can resume sending."""
        if hasattr(self.udp_factory, 'transferred'):
            self.udp_factory.transferred.clear()


class UDPProtocol(protocol.DatagramProtocol):
    """Handles voice transmitions."""

    def startProtocol(self):
        self.transferred = {}

    def datagramReceived(self, data, source):
        """Decode the data."""
        if source not in self.transferred:
            self.transferred[source] = 0
        if self.transferred[source] > 200000:
            return  # Greedy connection.
        try:
            transmition_parser.handle_string(data, self, *source)
        except UnpackException as e:
            logger.warning('Failed to unpack data:')
            logger.exception(e)


class ProtocolBase:
    """Base class for mindspace protocol classes."""

    def handle_command(self, *args, **kwargs):
        """Handle a command as this connection."""
        name = args[0]
        args = args[1:]
        return self.parser.handle_command(name, self, *args, **kwargs)

    def on_connect(self):
        self.last_active = 0
        self.locked = False
        self.transport.setTcpNoDelay(True)
        self.shell = None
        self.walk_task = None
        self.player_id = None
        self.object_id = None
        self.search_string = ''
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = logging.getLogger('%s:%d' % (self.host, self.port))
        self.logger.info('Connected.')
        server.connections.append(self)
        self.parser = login_parser
        message(self, ServerOptions.get().connect_msg)

    def on_disconnect(self, reason):
        self.shell = None
        if getattr(self, 'walk_task', None) is not None:
            try:
                self.walk_task.stop()
            except AssertionError:
                pass  # Not running.
        if self in server.connections:
            server.connections.remove(self)
        getattr(self, 'logger', logger).info(reason)
        if getattr(self, 'player_id', None) is not None:
            with session() as s:
                player = self.get_player(s)
                player.connected = False
                for account in Player.query(disconnect_notifications=True):
                    obj = account.object
                    if obj is None:
                        continue
                    connection = obj.get_connection()
                    if connection is not None:
                        name = player.get_name(obj.is_staff)
                        msg = f'{name} has disconnected.'
                        account.object.message(msg, channel='Connection')
                        interface_sound(
                            connection, get_sound(
                                os.path.join('notifications', 'disconnect.wav')
                            )
                        )
                player.player.transmition_id = None
                player.register_connection(None)
                s.add_all([player, player.player])

    def set_locked(self, value):
        """Lock or unlock this connection."""
        self.locked = value
        state = 'locked' if self.locked else 'unlocked'
        message(self, f'Your connection has been {state}.')

    def disconnect(self, text=None):
        if text is not None:
            message(self, text)
        self.transport.loseConnection()

    def get_player(self, s=None):
        """Get the player object associated with this connection."""
        if s is None:
            s = Session
        if self.player_id is not None:
            return Object.get(self.player_id)

    def handle_string(self, string):
        self.last_active = time()
        if self.logged:
            Session.add(LoggedCommand(string=string, owner_id=self.player_id))
            Session.commit()
        if self.locked:
            message(self, 'Your connection has been locked.')
        else:
            try:
                self._handle_string(string)
            except Exception as e:
                logger.exception(e)
                message(self, 'There was an error with your command.')

    @property
    def logged(self):
        return self.player_id in server.logged_players

    @logged.setter
    def logged(self, value):
        if value:
            server.logged_players.add(self)
        else:
            if self in server.logged_players:
                server.logged_players.remove(self)


class MindspaceWebSocketProtocol(WebSocketServerProtocol, ProtocolBase):
    """A protocol to use with a web client."""

    def _handle_string(self, string):
        """Handle JSON string."""
        name, args, kwargs = loads(string)
        return self.parser.handle_command(name, self, *args, **kwargs)

    def send(self, name, *args, **kwargs):
        """Prepare data and send it via self.sendString."""
        data = dumps(dict(name=name, args=args, kwargs=kwargs))
        self.sendMessage(data.encode())

    def onOpen(self):
        self.on_connect()

    def onMessage(self, payload, is_binary):
        if not is_binary:
            self.handle_string(payload)
        else:
            print(f'<binary {payload}>')

    def onClose(self, wasClean, code, reason):
        self.on_disconnect(reason)


class MindspaceProtocol(NetstringReceiver, ProtocolBase):
    """Handle connections from TCP clients."""

    def _handle_string(self, string):
        """Protocol-specific string handling."""
        self.parser.handle_string(string, self)

    def send(self, name, *args, **kwargs):
        """Prepare data and send it via self.sendString."""
        data = self.parser.prepare_data(name, *args, **kwargs)
        self.sendString(data)

    def connectionMade(self):
        self.on_connect()

    def connectionLost(self, reason):
        self.on_disconnect(reason.getErrorMessage())

    def stringReceived(self, string):
        self.handle_string(string)


class ServerFactory(protocol.ServerFactory):

    def buildProtocol(self, addr):
        if BannedIP.query(ip=addr.host).count():
            logger.warning('Blocked connection from banned IP %s.', addr.host)
        else:
            logger.info(
                'Incoming connection from %s:%d.', addr.host, addr.port
            )
            return MindspaceProtocol()


server = Server()
