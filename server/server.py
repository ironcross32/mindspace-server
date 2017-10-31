"""Provides the Server class."""

import logging
import os.path
from time import time
from datetime import datetime
from random import choice, randint
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, protocol, endpoints, task
from twisted.web.server import Site
from .protocol import interface_sound, message
from .sound import get_sound
from .parsers import login_parser, transmition_parser
from .db import (
    Session, session, Object, Player, Advert, ServerOptions, BannedIP,
    LoggedCommand
)
from .web.app import app
from .web import routes  # noqa

logger = logging.getLogger(__name__)


@transmition_parser.command
def transmit(udp, host, port, type, id, data):
    """Send data out to players."""
    with session() as s:
        player = s.query(Player).filter_by(transmition_id=id).first()
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
        for obj in player_obj.location.objects:
            if obj is not player_obj or player_obj.monitor_transmitions:
                obj_con = obj.get_connection()
                if obj_con is not None:
                    udp.transport.write(
                        login_parser.prepare_data(type, player_obj.id, data),
                        (obj_con.host, server.udp_port)
                    )


class Server:
    def __init__(self):
        """Leave everything in one place."""
        self.started = None
        self.tasks = []
        self.connections = []
        self.tcp_factory = ServerFactory()
        self.udp_factory = UDPProtocol()
        self.last_advert = None

    def show_advert(self):
        """Show an advert."""
        with session() as s:
            q = s.query(Advert)
            if self.last_advert is not None:
                q = q.filter(Advert.id.isnot(self.last_advert))
            c = q.count()
            self.last_advert = None
            if c and self.connections:
                ad = choice(q.all())
                self.last_advert = ad.id
                logger.info('Showing advert %r.', ad)
                for con in self.connections:
                    interface_sound(
                        con,
                        get_sound(os.path.join('notifications', 'advert.wav'))
                    )
                    message(con, ad.text)
                    message(con, 'For more information, press the A key.')
        reactor.callLater(randint(120, 900), self.show_advert)

    def start_listening(self):
        """Start everything listening."""
        self.started = datetime.utcnow()
        self.show_advert()
        o = ServerOptions.get()
        self.udp_port = o.udp_port
        self.tcp_listener = reactor.listenTCP(
            o.port, self.tcp_factory, interface=o.interface
        )
        logger.info(
            'Now listening on %s:%d.',
            self.tcp_listener.interface, self.tcp_listener.port
        )
        self.web_endpoint = endpoints.TCP4ServerEndpoint(
            reactor, o.web_port, interface=o.interface
        )
        self.site = Site(app.resource())
        d = self.web_endpoint.listen(self.site)
        d.addErrback(logger.warning)
        d.addCallback(
            lambda value: logger.info(
                'Web server listening on %s:%d.', value.interface, value.port
            )
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

    def task(self, func=None, interval=1.0):
        """Decorator to create a task."""

        def inner(func):
            t = task.LoopingCall(func)
            t.start(interval, now=False).addBoth(self.callback(t))
            self.tasks.append(t)
            return t
        if func is None:
            return inner
        else:
            return inner(func)

    def callback(self, task):
        """task has had a problem."""

        def inner(err):
            logger.warning(
                'Task %r threw an error: %s', task, err.getErrorMessage()
            )
            logger.exception(err.getTraceback())
        return inner


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
        transmition_parser.handle_string(data, self, *source)


class MindspaceProtocol(NetstringReceiver):
    """Handle connections."""

    def handle_command(self, *args, **kwargs):
        """Handle a command as this connection."""
        name = args[0]
        args = args[1:]
        return self.parser.handle_command(name, self, *args, **kwargs)

    def connectionMade(self):
        self.last_active = 0
        self.locked = False
        self.transport.setTcpNoDelay(True)
        self.shell = None
        self.scan_index = 0
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

    def connectionLost(self, reason):
        self.shell = None
        if self.walk_task is not None:
            try:
                self.walk_task.stop()
            except AssertionError:
                pass  # Not running.
        if self in server.connections:
            server.connections.remove(self)
        self.logger.info(reason.getErrorMessage())
        if self.player_id is not None:
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
            return s.query(Object).get(self.player_id)

    def stringReceived(self, string):
        self.last_active = time()
        if self.player_id is not None:
            Session.add(LoggedCommand(string=string, owner_id=self.player_id))
            Session.commit()
        if self.locked:
            message(self, 'Your connection has been locked.')
        else:
            try:
                self.parser.handle_string(string, self)
            except Exception as e:
                logger.exception(e)
                message(self, 'There was an error with your command.')

    def send(self, name, *args, **kwargs):
        """Prepare data and send it via self.sendString."""
        data = self.parser.prepare_data(name, *args, **kwargs)
        self.sendString(data)


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
