"""Provides server tasks."""

import logging
from datetime import datetime
from inspect import isclass
from time import time, strftime
from sqlalchemy import and_, or_
from .util import angle_between, point_pos, directions
from .db import (
    session, dump_db, Object, Zone, Mobile, Base, ServerOptions, LoggedCommand,
    CommunicationChannelMessage, Player, Entrance, Orbit
)
from .db.base import RandomSoundContainerMixin
from .server import server

logger = logging.getLogger(__name__)


@server.task
def do_space():
    """Do space stuff."""
    with session() as s:
        for obj in Zone.query(
            and_(
                Zone.direction_id.isnot(None),
                or_(Zone.speed.isnot(None), Zone.acceleration.isnot(None))
            )
        ):
            if obj.speed is None:
                # Let's set speed.
                obj.speed = 0.0
            if obj.acceleration:
                if obj.accelerating:
                    obj.speed += obj.acceleration
                else:
                    obj.speed -= obj.acceleration
                    if obj.speed < 0.0:
                        obj.speed = None
                        obj.acceleration = None
                        obj.accelerating = True
                        obj.background_rate = 0.0
                        obj.update_occupants()
                        continue
            for name in ('x', 'y', 'z'):
                value = getattr(obj, name)
                value += (obj.speed * getattr(obj.direction, name))
                setattr(obj, name, value)
            s.add(obj)
        for o in Orbit.query():
            logger.info(
                'Before: %s.',
                directions(o.zone.coordinates, o.orbiting.coordinates)
            )
            angle = angle_between(o.orbiting.coordinates, o.zone.coordinates)
            angle += o.offset
            o.zone.coordinates = point_pos(
                o.orbiting.coordinates, o.distance, angle
            )
            logger.info(
                'After: %s.',
                directions(o.zone.coordinates, o.orbiting.coordinates)
            )
            s.add(o.zone)


@server.task
def do_random_sound():
    """Play random sounds for rooms who need it."""
    with session() as s:
        now = time()
        for cls in Base._decl_class_registry.values():
            if not isclass(
                cls
            ) or RandomSoundContainerMixin not in cls.__bases__:
                continue
            for obj in cls.query(
                cls.next_random_sound.isnot(None),
                cls.next_random_sound < now
            ):
                if obj.random_sounds:
                    obj.play_random_sound()
                else:
                    obj.next_random_sound = 0.0
                s.add(obj)


@server.task
def do_move_mobile():
    """Move mobiles around."""
    with session():
        for obj in Object.join(Object.mobile).filter(
            Object.location_id.isnot(None), Object.mobile_id.isnot(None),
            Mobile.next_move < time()
        ):
            obj.mobile.move()


@server.task(interval=ServerOptions.get().dump_interval)
def do_dump():
    """Dump the database to disk."""
    started = time()
    logger.info('Dumping database to disk...')
    # I got the below filename from the first answer at:
    # http://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
    output = 'world.dump %s' % strftime("%Y-%m-%d %H-%M-%S")
    res = dump_db(output)
    logger.info(
        'Objects dumped: %d (%.2f seconds).', res, time() - started
    )


@server.task(interval=3600 * 24)
def do_purge():
    """Purge unneeded objects."""
    started = time()
    logger.info('Purging old objects...')
    with session() as s:
        oldest = datetime.utcnow() - ServerOptions.get().purge_after
        for obj in LoggedCommand.query(
            LoggedCommand.sent < oldest
        ).all() + CommunicationChannelMessage.query(
            CommunicationChannelMessage.sent < oldest
        ).all() + Player.query(object=None).all() + Entrance.query(
            object=None
        ).all() + Object.query(Object.player_id.isnot(None), steps=0).all():
            logger.info('Purging %r.', obj)
            s.delete(obj)
        logger.info('Purge completed in %.2f seconds.', time() - started)
