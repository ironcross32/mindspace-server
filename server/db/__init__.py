"""Database."""

import os
import os.path
import logging
from glob import glob
from inspect import isclass
from yaml import dump, load
from .engine import engine
from .session import Session, session
from .base import Base, dump_object
from .rooms import Room, RoomRandomSound, RoomFloorType
from .players import Player
from .objects import Object, ObjectRandomSound
from .actions import Action, ObjectAction
from .entrances import Entrance
from .starships import Starship, StarshipSensors, StarshipEngine
from .zones import Zone
from .directions import Direction
from .adverts import Advert
from .commands import Command
from .hotkeys import Hotkey, HotkeySecondary
from .revisions import Revision
from .communication import (
    CommunicationChannel, CommunicationChannelListener,
    CommunicationChannelMessage, CommunicationChannelBan, TransmitionError
)
from .rules import Rule
from .help import HelpTopicKeyword, HelpTopic, HelpKeyword
from .server_options import ServerOptions
from .mobiles import Mobile
from .socials import Social
from .banned_ips import BannedIP
from .windows import Window
from .ideas import IdeaVote, Idea, IdeaComment
from .changelog import ChangelogEntry
from .mail import MailMessage
from .logged_commands import LoggedCommand
from .credits import Credit
from .object_types import (
    ObjectTypeActionSecondary, ObjectTypeHotkeySecondary, ObjectTypeSecondary,
    ObjectType
)
from .orbits import Orbit

logger = logging.getLogger(__name__)
output_directory = 'world'


def load_db():
    """Load the db from output_directory."""
    logger.info('Creating database tables...')
    Base.metadata.create_all()
    objects = []
    if not os.path.isdir(output_directory):
        logger.info('Starting with blank database.')
    else:
        logger.info('Loading database from directory %s.', output_directory)
        with session() as s:
            for cls in Base._decl_class_registry.values():
                if not isclass(cls) or not issubclass(cls, Base):
                    continue
                directory = os.path.join(output_directory, cls.__name__)
                if os.path.isdir(directory):
                    logger.info('Entering directory %s.', directory)
                    for fname in os.listdir(directory):
                        with open(os.path.join(directory, fname), 'r') as f:
                            y = f.read()
                            y = load(y)
                            objects.append(cls(**y))
                    logger.info('Leaving directory %s.', directory)
            s.add_all(objects)
    with session() as s:
        if not s.query(Zone).count():
            s.add(Zone(name='The First Zone'))
            s.commit()
        if not s.query(Room).count():
            objects.append(
                Room(name='The First Room', zone=s.query(Zone).first())
            )
        if not s.query(Command).count():
            for path in glob(os.path.join('commands', '*.command')):
                fname = os.path.basename(path)
                name = os.path.splitext(fname)[0]
                with open(path, 'r') as f:
                    cmd = Command(name=name)
                    cmd.set_code(f.read())
                    logger.info('Loaded %s from %s.', cmd.name, path)
                    objects.append(cmd)
        if not s.query(Hotkey).count():
            for path in glob(os.path.join('hotkeys', '*.command')):
                fname = os.path.basename(path)
                name = os.path.splitext(fname)[0].upper()
                with open(path, 'r') as f:
                    description, code = f.read().split('\n', 1)
                key = Hotkey(name=name, description=description)
                key.set_code(code)
                logger.info('Loaded %s from %s.', key.name, path)
                objects.append(key)
        s.add_all(objects)
        if not s.query(Direction).count():
            # Create default directions:
            Direction.create('north', y=1)
            Direction.create('northeast', x=1, y=1)
            Direction.create('east', x=1)
            Direction.create('southeast', x=1, y=-1)
            Direction.create('south', y=-1)
            Direction.create('southwest', x=-1, y=-1)
            Direction.create('west', x=-1)
            Direction.create('northwest', x=-1, y=1)
            s.commit()
            for d in Direction.query():
                Direction.create(f'{d.name} and down', x=d.x, y=d.y, z=-1)
                Direction.create(f'{d.name} and up', x=d.x, y=d.y, z=1)
            Direction.create('up', z=1)
            Direction.create('down', z=-1)
            s.commit()
            for d in s.query(Direction):
                d.opposite = s.query(Direction).filter_by(
                    x=d.x * -1,
                    y=d.y * -1,
                    z=d.z * -1
                ).first()
                s.add(d)
                s.commit()
        if not s.query(ServerOptions).count():
            s.add(
                ServerOptions(
                    name='Default', first_room=s.query(Room).first()
                )
            )
        s.query(Object).update({Object.connected: False})
    return sum(
        [
            s.query(
                cls
            ).count() for cls in Base._decl_class_registry.values() if isclass(
                cls
            )
        ]
    )


def dump_db(where=None):
    """Dump the database to single files."""
    if where is None:
        where = output_directory
    objects = 0
    if os.path.isdir(where):
        stat = os.stat(where)
        old_name = f'{where}.{stat.st_mtime}'
        try:
            os.rename(where, old_name)
            logger.info('Renamed %s to %s.', where, old_name)
        except OSError as e:
            logger.warning(
                'Failed to rename directory %s to %s:', where, old_name
            )
            logger.exception(e)
    logger.info('Dumping the database to directory %s.', where)
    os.makedirs(where)
    for cls in Base._decl_class_registry.values():
        if not isclass(cls) or not issubclass(cls, Base):
            continue
        directory = os.path.join(where, cls.__name__)
        q = Session.query(cls)
        if q.count():
            logger.info('Entering directory %s.', directory)
            if not os.path.isdir(directory):
                logger.info('Creating directory.')
                os.makedirs(directory)
            for obj in q:
                path = os.path.join(directory, f'{obj.id}.yaml')
                objects += 1
                y = dump_object(obj)
                with open(path, 'w') as f:
                    dump(y, stream=f)
            logger.info('Leaving directory %s.', directory)
        else:
            logger.info('Nothing to be done for directory %s.', directory)
    return objects


__all__ = (
    'engine', 'Session', 'session', 'Base', 'dump_object', 'Room',
    'RoomRandomSound', 'Player', 'Object', 'Action', 'ObjectAction',
    'load_db', 'dump_db', 'Entrance', 'Zone', 'Direction', 'Advert', 'Command',
    'Hotkey', 'Action', 'Revision', 'HotkeySecondary', 'CommunicationChannel',
    'CommunicationChannelListener', 'CommunicationChannelMessage',
    'CommunicationChannelBan', 'TransmitionError', 'Rule', 'HelpTopicKeyword',
    'HelpTopic', 'HelpKeyword', 'ServerOptions', 'Mobile', 'Social',
    'ObjectRandomSound', 'BannedIP', 'output_directory', 'Window', 'IdeaVote',
    'Idea', 'IdeaComment', 'ChangelogEntry', 'MailMessage', 'LoggedCommand',
    'Credit', 'StarshipEngine', 'RoomFloorType', 'ObjectTypeActionSecondary',
    'ObjectTypeHotkeySecondary', 'ObjectTypeSecondary', 'ObjectType', 'Orbit',
    'Starship', 'StarshipSensors'
)
