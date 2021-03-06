"""Provides routines for running programs."""

import os
import re
import sys
from traceback import format_exception
import datetime
import logging
import random
from time import time, ctime, strftime
from platform import platform, architecture, python_implementation
from contextlib import redirect_stdout, redirect_stderr
from code import InteractiveConsole
import sqlalchemy
from random_password import random_password
from humanize import naturalsize
from psutil import Process, boot_time, virtual_memory
from sqlalchemy import exc
from twisted.internet import reactor
from emote_utils import SocialsError
from . import db, server, protocol, menus, util, forms, sound, distance
from .db import (
    base, Object, ServerOptions, CommunicationChannel, ATM, Session as s
)
from .socials import factory
from .mail import Message

logger = logging.getLogger(__name__)

coordinates_re = re.compile(
    r'^[[(]?(\d+[.]?\d*)[, ]+(\d+[.]?\d*)[, ]+(\d+[.]?\d*)[])]?$'
)


class PermissionError(Exception):
    """Someone did something naughty."""


def get_coordinates(player, string):
    m = coordinates_re.match(string)
    if m is None:
        player.message(f'Invalid coordinates: {string}.')
        end()
    x, y, z = m.groups()
    return (float(x), float(y), float(z))


def check_in_space(player, starship=None):
    """Ensure the provided starship is in space. If starship is None use the
    starship the player is aboard."""
    if starship is None:
        starship = player.location.zone.starship
    if starship.object.location_id is not None:
        player.message('You are not in space.')
        end()


def check_location(player, obj, coordinates=True):
    """Ensure player is at obj.location. If coordinates is True ensure they are
    also at the same coordinates."""
    if (
        player.location_id != obj.location_id or
        (coordinates and obj.coordinates != player.coordinates)
    ) and obj.holder_id != player.id:
        player.message(
            f'{obj.get_name(player.is_staff).title()} is nowhere to be seen.'
        )
        end()


def valid_sensors(player):
    """Return (zone, starship) or exit."""
    zone = player.location.zone
    ship = zone.starship
    if ship is None or ship.sensors is None:
        player.message('No sensors found.')
        end()
    else:
        return (zone, ship)


def valid_engine(player):
    """Return (zone, starship) or exit."""
    zone = player.location.zone
    ship = zone.starship
    if ship is None or ship.engine is None:
        player.message('No engines found.')
        end()
    else:
        return (zone, ship)


def valid_object(player, obj, message='Invalid object.'):
    """Check an object is valid."""
    if obj is None:
        player.message(message)
        end()


def check_perms(player, builder=None, admin=None, message=None):
    """Check the permissions of the provided player."""
    if message is None:
        message = '{} is not a {}.'
    name = player.get_name(True)
    if builder is not None and builder is not player.is_builder:
        raise PermissionError(message.format(name, 'builder'))
    if admin is not None and admin is not player.is_admin:
        raise PermissionError(message.format(name, 'admin'))


def check_builder(player):
    ret = check_perms(player, builder=True)
    if player.location.zone.owner is not player and not player.is_admin:
        raise PermissionError('You do not own this zone.')
    return ret


def check_admin(player):
    return check_perms(player, admin=True)


def check_staff(player):
    if not player.is_staff:
        name = player.get_name(True)
        raise PermissionError(f'{name} is not staff.')


def check_bank(player, bank):
    """Ensure player can actually access the bank they're trying to access. If
    they can, return a suitable Object instance bound to an ATM instance
    registered with that bank."""
    valid_object(player, bank)
    obj = Object.join(Object.atm).filter(
        Object.location_id == player.location_id, *player.same_coordinates(),
        ATM.bank_id == bank.id
    ).first()
    if obj is None:
        player.message('You cannot access that bank from here.')
        end()
    return obj


def server_info():
    """Return server statistics."""
    started = time()
    proc = Process()
    process_size = proc.memory_info()
    stats = []
    memory = virtual_memory()
    stats.append(
        'Memory: {used} used of {total} ({percent}%)'.format(
            used=naturalsize(memory.used),
            total=naturalsize(memory.total),
            percent=memory.percent
        )
    )
    bt = boot_time()
    uptime = time() - bt
    stats.append(
        'Server Uptime: {delta} since {booted}'.format(
            delta=util.format_timedelta(datetime.timedelta(seconds=uptime)),
            booted=ctime(bt)
        )
    )
    if server.server.started is not None:
        stats.append(
            'Process Uptime: {} since {}'.format(
                util.format_timedelta(
                    datetime.datetime.utcnow() - server.server.started
                ),
                server.server.started.ctime()
            )
        )
    stats.append(
        'OS Version: {} ({})'.format(
            platform(),
            architecture()[0]
        )
    )
    stats.append(
        '{type} : {version}'.format(
            type=python_implementation(),
            version=sys.version
        )
    )
    stats.append('Number Of Threads: %d' % proc.num_threads())
    stats.append('Process Memory:')
    stats.append('Real: %s' % naturalsize(process_size.rss))
    stats.append('Virtual: %s' % naturalsize(process_size.vms))
    stats.append('Percent: %.2f' % proc.memory_percent())
    stats.append('Lines of code in server: %d' % db.Base.code_lines())
    stats.append('Objects in server: %d' % db.Base.number_of_objects())
    stats.append('Statistics generated in %.2f seconds.' % (time() - started))
    return stats


class PythonShell(InteractiveConsole):
    """A shell bound to a connection instance."""

    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        super().__init__(*args, **kwargs)
        self.locals.update(
            shell=self,
            con=self.connection,
            logger=logging.getLogger('Python Shell'),
            **ctx
        )

    def write(self, data):
        protocol.message(self.connection, data)


class OK(Exception):
    """Use instead of return."""


def end():
    """Use instead of return."""
    raise OK()


def handle_traceback(e, program_name, player_name, location_name):
    logger.warning(
        '%s (called by %s at %s) threw an error:', program_name, player_name,
        location_name
    )
    logger.exception(e)
    tb = ''.join(format_exception(e.__class__, e, e.__traceback__))
    name = 'Traceback'
    channel = CommunicationChannel.query(name=name, admin=True).first()
    if channel is None:
        channel = CommunicationChannel(
            description='Tracebacks from game systems', name=name, admin=True,
            transmit_format='[{channel_name}] %1N transmit%1s:\n{message}',
            transmit_sound=os.path.join('communication', 'traceback.wav')
        )
        s.add(channel)
        s.commit()
    sender = ServerOptions.instance().system_object
    assert sender is not None
    channel.transmit(sender, tb, strict=False)


codes = {}
ctx = dict(
    util=util,
    handle_traceback=handle_traceback,
    random_password=random_password,
    OK=OK,
    end=end,
    valid_object=valid_object,
    valid_sensors=valid_sensors,
    valid_engine=valid_engine,
    check_in_space=check_in_space,
    check_location=check_location,
    check_perms=check_perms,
    check_admin=check_admin,
    check_builder=check_builder,
    check_staff=check_staff,
    check_bank=check_bank,
    get_coordinates=get_coordinates,
    exc=exc,
    PythonShell=PythonShell,
    redirect_stdout=redirect_stdout,
    redirect_stderr=redirect_stderr,
    os=os,
    sys=sys,
    datetime=datetime,
    re=re,
    sqlalchemy=sqlalchemy,
    server_info=server_info,
    server_options=db.ServerOptions.instance,
    SocialsError=SocialsError,
    socials=factory,
    time=time,
    ctime=ctime,
    strftime=strftime,
    base=base,
    Message=Message
)


def run_program(con, s, prog, **context):
    """Run a program with a sensible context."""
    context['s'] = s
    if 'player' not in context:
        if con is None:
            player = None
        else:
            player = con.get_player(s)
        context['player'] = player
    else:
        player = context['player']
    context['con'] = con
    context.update(ctx)
    context['logger'] = logging.getLogger(
        f'{prog}{" (%s)" % player.get_name(True) if player else ""}'
    )
    context['self'] = prog
    if prog.code not in codes:
        codes[prog.code] = compile(prog.code, prog.name, 'exec')
    exec(codes[prog.code], {}, context)


def build_context():
    for name in dir(distance):
        value = getattr(distance, name)
        if isinstance(value, float):
            ctx[name] = value
    for module in (db, protocol, menus, forms, sound, random):
        for name in dir(module):
            member = getattr(module, name)
            if callable(member) or isinstance(
                member, (list, dict, sound.Sound)
            ):
                ctx[name] = member
    ctx.update(
        floor_types_dir=db.floor_types_dir,
        server=server.server,
        reactor=reactor,
        run_program=run_program
    )
