"""Provides MindspaceParser instances."""

import os.path
import logging
from random import randint
from mindspace_protocol import MindspaceParser
from .program import run_program, OK
from .protocol import character_id, interface_sound, remember_quit, message
from .sound import get_sound
from .db import Command, session, Player, ServerOptions, Object, MailMessage

logger = logging.getLogger(__name__)


class MainParser(MindspaceParser):
    def huh(self, *args, **kwargs):
        """Search the database for a command."""
        name = args[0]
        connection = args[1]
        args = args[2:]
        with session() as s:
            query_args = [Command.name == name]
            if connection is not None:
                player = connection.get_player(s)
            else:
                player = None
            if player is not None:
                for perm in ('builder', 'admin'):
                    if not getattr(player, f'is_{perm}'):
                        column = getattr(Command, perm)
                        query_args.append(column.is_(False))
            cmd = Command.query(*query_args).first()
            if cmd is None:
                return super().huh(name, *args, **kwargs)
            # Save these in case of an error to prevent DetachedInstanceError.
            friendly = cmd.get_name(True)
            try:
                run_program(
                    connection, s, cmd, a=args, kw=kwargs, __name__=name,
                    player=player
                )
            except OK:
                pass  # Return from command.
            except Exception as e:
                logger.warning('%s threw an error:', friendly)
                raise e


login_parser = MindspaceParser()
main_parser = MainParser()


@login_parser.command
def key(con, *args, **kwargs):
    """Player isn't logged in but they're sending keys anyways."""
    message(con, 'You are not logged in.')


@login_parser.command
def login(con, username, password):
    """Login or create a player."""
    with session() as s:
        q = Player.query(username=username)
        if q.count():
            player = q.first()
            if player.check_password(password):
                obj = player.object
                con.logger.info('Authenticated as %r.', obj)
            else:
                con.logger.info('Incorrect password.')
                remember_quit(con)
                return con.disconnect('Incorrect password.')
        else:
            player = Player(username=username)
            player.set_password(password)
            if not Player.count():
                player.builder = True
                player.admin = True
            obj = Object(
                player=player, name=f'Passenger {randint(1000, 10000)}'
            )
            con.logger.info('Created %r.', obj)
            s.add_all((obj, player))
            s.commit()
        if player.locked:
            remember_quit(con)
            con.logger.info('Blocked authentication to %r.', player)
            return con.disconnect('Your account has been locked.')
        if obj.player.last_disconnected is None:
            msg = 'This is your first time connected.'
        else:
            msg = 'Last connected: %s from %s.' % (
                player.last_connected.ctime(), player.last_host
            )
        obj.register_connection(con)
        obj.message(msg)
        if obj.location is None:
            obj.location = ServerOptions.get().first_room
            s.add(obj)
        obj.message('Welcome back, %s.' % player.username)
        for account in Player.query(disconnect_notifications=True):
            character = account.object
            if character is None:
                continue
            connection = character.get_connection()
            if connection is not None:
                msg = f'{obj.get_name(character.is_staff)} has connected.'
                character.message(msg, channel='Connection')
                interface_sound(
                    connection,
                    get_sound(os.path.join('notifications', 'connect.wav'))
                )
        obj.identify(con)
        character_id(con, obj.id)
        obj.identify_location()
        obj.player.send_options(con)
        obj.connected = True
        s.add_all([obj, obj.player])
        if MailMessage.query(to_id=obj.id, read=False).count():
            obj.message('You have unread mail.')
            interface_sound(
                con, get_sound(os.path.join('notifications', 'mail.wav'))
            )
        con.parser = main_parser


@main_parser.command
def speak(con, data):
    """Send out microphone data."""
    data = data[:ServerOptions.get().max_speak_length]
    con.get_player().speak(data)
