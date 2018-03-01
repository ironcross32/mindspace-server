"""Provides routines for running programs."""

import os
import sys
import datetime
import logging
import re
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
from .db import base
from .socials import factory
from .mail import Message


class PermissionError(Exception):
    """Someone did something naughty."""


def check_in_space(player, starship=None):
    """Ensure the provided starship is in space. If starship is None use the
    starship the player is aboard."""
    if starship is None:
        starship = player.location.zone.starship
    if starship.object.location_id is not None:
        player.message('You are not in space.')
        end()


def check_location(player, obj):
    """Ensure player is at obj.location."""
    if player.location_id != obj.location_id:
        player.message(
            f'{obj.get_name(player.is_staff)} is nowhere to be seen.'
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
    return check_perms(player, builder=True)


def check_admin(player):
    return check_perms(player, admin=True)


def check_staff(player):
    if not player.is_staff:
        name = player.get_name(True)
        raise PermissionError(f'{name} is not staff.')


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


codes = {}
ctx = dict(
    util=util,
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
    server_options=db.ServerOptions.get,
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
    if con is None:
        player = None
    else:
        context['con'] = con
        player = con.get_player(s)
        context['player'] = player
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
            if callable(member) or isinstance(member, sound.Sound):
                ctx[name] = member
    ctx.update(
        server=server.server,
        reactor=reactor,
        run_program=run_program
    )
