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
            cmd = s.query(Command).filter_by(name=name).first()
            if cmd is None:
                return super().huh(name, *args, **kwargs)
            # Save these in case of an error to prevent DetachedInstanceError.
            friendly = cmd.get_name(True)
            try:
                run_program(
                    connection, s, cmd, a=args, kw=kwargs, __name__=name
                )
            except OK:
                pass  # Return from command.
            except Exception as e:
                logger.warning('%s threw an error:', friendly)
                raise e


login_parser = MindspaceParser()
main_parser = MainParser()
transmition_parser = MindspaceParser()
transmition_parser.loads_kwargs['encoding'] = None


@login_parser.command
def key(con, *args, **kwargs):
    """Player isn't logged in but they're sending keys anyways."""
    message(con, 'You are not logged in.')


@login_parser.command
def login(con, username, password):
    """Login or create a player."""
    with session() as s:
        q = s.query(Player).filter_by(username=username)
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
            if not s.query(Player).count():
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
        obj.register_connection(con)
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
