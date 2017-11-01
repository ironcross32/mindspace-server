"""Provides routines for running programs."""

import os
import sys
import datetime
import logging
from time import time, ctime
from platform import platform, architecture, python_implementation
from contextlib import redirect_stdout, redirect_stderr
from code import InteractiveConsole
import sqlalchemy
from humanize import naturalsize
from psutil import Process, boot_time, virtual_memory
from sqlalchemy import exc
from twisted.internet import reactor
from emote_utils import SocialsError
from . import db, server, protocol, menus, util, forms, sound, distance
from .socials import factory


class PermissionError(Exception):
    """Someone did something naughty."""


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
    OK=OK,
    end=end,
    valid_object=valid_object,
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
    sqlalchemy=sqlalchemy,
    server_info=server_info,
    server_options=db.ServerOptions.get,
    SocialsError=SocialsError,
    socials=factory,
    time=time, ctime=ctime
)


def run_program(con, s, prog, **context):
    """Run a program with a sensible context."""
    context['s'] = s
    context['con'] = con
    player = con.get_player(db.Session)
    context['player'] = player
    context.update(ctx)
    context['logger'] = logging.getLogger(
        f'Program {prog.name} ({player.get_name(True)}'
    )
    context.setdefault('self', prog)
    if prog.code not in codes:
        codes[prog.code] = compile(prog.code, prog.name, 'exec')
    exec(codes[prog.code], {}, context)


def build_context():
    for name in dir(distance):
        value = getattr(distance, name)
        if isinstance(value, float):
            ctx[name] = value
    for module in (db, protocol, menus, forms, sound):
        for name in dir(module):
            member = getattr(module, name)
            if callable(member) or isinstance(member, sound.Sound):
                ctx[name] = member
    ctx.update(
        server=server.server,
        reactor=reactor,
        run_program=run_program
    )