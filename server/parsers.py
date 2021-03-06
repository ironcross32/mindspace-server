"""Provides MindspaceParser instances."""

import os.path
import logging
import re
from contextlib import redirect_stdout, redirect_stderr
from random import randint
from mindspace_protocol import MindspaceParser
from sqlalchemy import or_
from .program import (
    run_program, OK, handle_traceback, PythonShell, valid_object,
    check_location
)
from .protocol import (
    character_id, interface_sound, remember_quit, message, menu
)
from .sound import get_sound, connect_sound
from .db import (
    Command, session, Player, ServerOptions, Object, MailMessage, Hotkey,
    Action, RemappedHotkey
)
from .menus import Menu, LabelItem, Item
from .util import pluralise

logger = logging.getLogger(__name__)


class MainParser(MindspaceParser):
    def huh(self, *args, **kwargs):
        """Search the database for a command."""
        name = args[0]
        connection = args[1]
        args = args[2:]
        with session() as s:
            query_args = [Command.name == name]
            player = connection.get_player(s)
            for perm in ('builder', 'admin'):
                if not getattr(player.player, perm, False):
                    column = getattr(Command, perm)
                    query_args.append(column.is_(False))
            cmd = Command.query(*query_args).first()
            if cmd is None:
                return super().huh(name, *args, **kwargs)
            # Save these in case of an error to prevent DetachedInstanceError.
            friendly = cmd.get_name(True)
            player_name = player.get_name(True)
            if player.location is None:
                location_name = 'Nowhere'
            else:
                location_name = player.location.get_name(True)
            try:
                run_program(
                    connection, s, cmd, a=args, kw=kwargs, __name__=name,
                    player=player
                )
            except OK:
                pass  # Return from command.
            except Exception as e:
                handle_traceback(e, friendly, player_name, location_name)
                raise e


login_parser = MindspaceParser()
main_parser = MainParser()


@login_parser.command(name='key')
def unauthenticated_key(con, *args, **kwargs):
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
            obj.location = ServerOptions.instance().first_room
            s.add(obj)
        obj.message('Welcome back, %s.' % player.username)
        obj.connected = True
        s.commit()
        for character in Object.join(Object.player).filter(
            Object.connected.is_(True),
            Player.connect_notifications.is_(True)
        ):
            connection = character.get_connection()
            msg = f'{obj.get_name(character.is_staff)} has connected.'
            character.message(msg, channel='Connection')
            interface_sound(connection, connect_sound)
        obj.identify(con)
        character_id(con, obj.id)
        obj.identify_location()
        obj.player.send_options(con)
        s.add_all([obj, obj.player])
        c = MailMessage.query(to_id=obj.id, read=False).count()
        if c:
            obj.message(f'You have {c} unread {pluralise(c, "message")}.')
            interface_sound(
                con, get_sound(os.path.join('notifications', 'mail.wav'))
            )
        motd = ServerOptions.instance().motd
        if motd is not None:
            obj.message(motd, channel='motd')
        con.parser = main_parser


@main_parser.command
def speak(con, data):
    """Send out microphone data."""
    if len(data) > ServerOptions.instance().max_speak_length:
        message(con, 'Transmition too long.')
    else:
        con.get_player().speak(data)


@main_parser.command(name='key')
def authenticated_key(con, name, modifiers=None):
    """Handle hotkeys."""
    if modifiers is None:
        modifiers = []
    ESC = 'ESCAPE'
    possible_modifiers = ('ctrl', 'shift', 'alt')
    key_modifiers = ('META', 'CONTROL', 'SHIFT', 'ALT')

    def check_hotkey(hotkey):
        for mod in possible_modifiers:
            value = getattr(hotkey, mod)
            if value not in (None, mod in modifiers):
                return False
        return True

    with session() as s:
        player = con.get_player(s)
        remap = RemappedHotkey.from_raw(player, name, modifiers)
        if remap is not None:
            name = remap.to_key
            modifiers = remap.to_modifiers
        if con.object_id is None:
            obj = None
        else:
            obj = Object.get(con.object_id)
            if obj is None:
                con.object_id = None
        kwargs = dict(modifiers=modifiers)
        if player.player.help_mode:
            if name in key_modifiers:
                return  # Don't show just a modifier.
            string = ' + '.join(modifiers)
            if string:
                string += ' + '
            string += ('space' if name == ' ' else name)
            player.message(string.upper())
        if obj is None:
            if name == ESC and not modifiers and player.player.help_mode:
                player.player.help_mode = False
                player.message('Help mode disabled.')
                return
            query_args = [Hotkey.name == name]
            for perm in ('builder', 'admin'):
                if not getattr(player.player, perm):
                    column = getattr(Hotkey, perm)
                    query_args.append(column.isnot(True))
            for mod in possible_modifiers:
                column = getattr(Hotkey, mod)
                query_args.append(
                    or_(
                        column.is_(None),
                        column.is_(mod in modifiers)
                    )
                )
            keys = Hotkey.query(*query_args, reusable=False)
        elif name == ESC:
            con.object_id = None
            player.do_social(obj.stop_use_msg, _others=[obj])
            return
        elif name == 'F1':
            items = [LabelItem('Hotkeys')]
            for key in obj.get_hotkeys():
                modifiers = []
                args = [key.name, []]
                for name in ('ctrl', 'shift', 'alt'):
                    friendly_name = name.upper()
                    value = getattr(key, name)
                    if value is None:
                        modifiers.append(f'[{friendly_name}]')
                    elif value is True:
                        modifiers.append(friendly_name)
                        args[-1].append(name)
                modifiers = f'{" ".join(modifiers)}{" " if modifiers else ""}'
                name = key.get_name(player.is_staff)
                description = key.get_description()
                items.append(
                    Item(
                        f'{modifiers}{name}: {description}', 'key', args=args
                    )
                )
            menu(con, Menu('Hotkeys', items, escapable=True))
            return
        else:
            kwargs['obj'] = obj
            keys = []
            for hotkey in obj.get_hotkeys():
                if hotkey.name == name and check_hotkey(hotkey):
                    keys.append(hotkey)
        for key in keys:
            key_name = key.get_name(True)
            player_name = player.get_name(True)
            location_name = player.location.get_name(True)
            if player.player.help_mode:
                player.message(key.get_description())
            else:
                try:
                    run_program(con, s, key, **kwargs)
                except OK:
                    pass  # Command exited successfully.
                except Exception as e:
                    handle_traceback(e, key_name, player_name, location_name)
                    raise e


@main_parser.command
def python(con, code):
    """Execute Python code."""
    with session() as s:
        player = con.get_player()
        if not player.is_admin:
            return player.message('This command is for admins only.')
        for full, id in re.findall('(#([0-9]+))', code):
            code = code.replace(full, f's.query(Object).get({id})')
        if con.shell is None:
            con.shell = PythonShell(con)
        with redirect_stdout(con.shell), redirect_stderr(con.shell):
            con.shell.locals.update(
                player=player,
                here=player.location,
                s=s
            )
            if con.shell.push(code):
                msg = '...'
            else:
                msg = '>>>'
            player.message(msg)
        for name in ('s', 'player', 'here'):
            del con.shell.locals[name]


@main_parser.command
def action(con, object_id, action_id):
    """Call an action on an object."""
    with session() as s:
        player = con.get_player()
        obj = Object.get(object_id)
        action = Action.get(action_id)
        try:
            for thing in (obj, action):
                valid_object(player, thing)
            check_location(player, obj)
        except OK:
            return  # They're playing silly buggers.
        if action in obj.get_actions():
            friendly = action.get_name(True)
            player_name = player.get_name(True)
            if player.location is None:
                location_name = 'Nowhere'
            else:
                location_name = player.location.get_name(True)
            try:
                run_program(con, s, action, self=action, obj=obj)
            except OK:
                pass  # Return from command.
            except Exception as e:
                handle_traceback(e, friendly, player_name, location_name)
                raise e
        else:
            player.message('Invalid action or object ID.')
