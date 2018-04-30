"""Provides the Server class."""

import logging
import os.path
from time import time
from datetime import datetime
from json import dumps, loads
from socket import getfqdn
from urllib.parse import urljoin
from klein import Klein
from autobahn.twisted.websocket import (
    WebSocketServerProtocol, WebSocketServerFactory, listenWS
)
from autobahn.websocket.compress import (
    PerMessageDeflateOffer, PerMessageDeflateOfferAccept
)
from twisted.internet import reactor, ssl
from twisted.web.server import Site
from .protocol import interface_sound, message
from .sound import get_sound
from .parsers import login_parser
from .program import handle_traceback
from .db import (
    Session, session, Object, Player, ServerOptions, LoggedCommand
)
from .web.app import app
from .web import routes  # noqa

logger = logging.getLogger(__name__)
hostname = getfqdn().encode()
insecure_app = Klein()


@insecure_app.route('/', branch=True)
def redirect(request):
    return request.redirect(
        urljoin(
            b'https://%s:%d' % (hostname, ServerOptions.get().https_port),
            request.path
        )
    )


class Server:
    def __init__(self):
        """Leave everything in one place."""
        self.started = None
        self.logged_players = set()
        self.connections = []
        self.curses = []
        with open('curses.txt', 'r') as f:
            for curse in f.readlines():
                self.curses.append(curse.strip().lower())

    def valid_name(self, name):
        """Ensure a name is free of curses."""
        if '\r' in name or '\n' in name:
            return False
        for word in name.split(' '):
            word = word.lower()
            for curse in self.curses:
                if word.startswith(curse):
                    return False
        return True

    def accept(self, offers):
        """Accept offers from the browser."""
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)

    def start_listening(self, private_key, certificate_key):
        """Start everything listening."""
        self.started = datetime.utcnow()
        o = ServerOptions.get()
        web = Site(app.resource())
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            private_key, certificate_key
        )
        insecure_site = Site(insecure_app.resource())
        http_port = reactor.listenTCP(
            o.http_port, insecure_site, interface=o.interface
        )
        logger.info(
            'Redirecting HTTP traffic from %s:%d.', http_port.interface,
            http_port.port
        )
        https_port = reactor.listenSSL(
            o.https_port, web, ssl_context, interface=o.interface
        )
        logger.info(
            'Serving HTTPS from %s:%d.', https_port.interface, https_port.port
        )
        websocket_factory = WebSocketServerFactory(
            f'wss://{o.interface}:{o.websocket_port}'
        )
        websocket_factory.setProtocolOptions(
            perMessageCompressionAccept=self.accept
        )
        websocket_factory.protocol = MindspaceWebSocketProtocol
        websocket_port = listenWS(
            websocket_factory, ssl_context, interface=o.interface
        )
        logger.info(
            'Listening for web sockets on %s:%d.', websocket_port.interface,
            websocket_port.port
        )


class ProtocolBase:
    """Base class for mindspace protocol classes."""

    def on_connect(self):
        self.last_active = 0
        self.locked = False
        self.transport.setTcpNoDelay(True)
        self.shell = None
        self.walk_task = None
        self.player_id = None
        self.object_id = None
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = logging.getLogger(f'{self.host}:{self.port}')
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
        getattr(self, 'logger', logger).info(reason.getErrorMessage())
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
                player.register_connection(None)
                s.add_all([player, player.player])

    def set_locked(self, value):
        """Lock or unlock this connection."""
        self.locked = value
        state = 'locked' if self.locked else 'unlocked'
        message(self, f'Your connection has been {state}.')

    def disconnect(self, text=None):
        """Close this websocket, sending text as reason."""
        self.sendClose(code=self.CLOSE_STATUS_CODE_NORMAL, reason=text)

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
            self._handle_string(string)

    def handle_command(self, name, *args, **kwargs):
        """Handle a command. Used by commands in the database."""
        self.parser.handle_command(name, self, *args, **kwargs)

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
        player = self.get_player()
        if player is None:
            player_name = self.logger.name
        else:
            player_name = player.get_name(True)
        if player is None:
            location_name = 'Not Connected'
        elif player.location is None:
            location_name = 'Nowhere'
        else:
            location_name = player.location.get_name(True)
        del player
        try:
            self.parser.handle_command(name, self, *args, **kwargs)
        except Exception as e:
            message(self, ServerOptions.get().command_error_msg)
            handle_traceback(e, 'handle_string', player_name, location_name)

    def send(self, name, *args, **kwargs):
        """Prepare data and send it via self.sendString."""
        data = dumps(dict(name=name, args=args, kwargs=kwargs))
        self.sendMessage(data.encode())

    def connectionMade(self):
        super().connectionMade()
        self.on_connect()

    def onMessage(self, payload, is_binary):
        if not is_binary:
            self.handle_string(payload)

    def connectionLost(self, reason):
        super().connectionLost(reason)
        self.on_disconnect(reason)


server = Server()
