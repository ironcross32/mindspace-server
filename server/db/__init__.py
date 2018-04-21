"""Database."""

import os
import os.path
import logging
from glob import glob
from inspect import isclass
from sqlalchemy import inspect
from yaml import dump, load
from db_dumper import load as dumper_load, dump as dumper_dump
from .engine import engine
from .session import Session, session
from .base import Base, DataMixin
from .rooms import Room, RoomRandomSound, RoomFloorType, RoomAirlock
from .players import Player
from .objects import Object, ObjectRandomSound, RestingStates
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
from .stars import Star
from .tasks import Task
from .transits import TransitStop, TransitRoute
from .genders import Gender
from .chairs import Chair
from .containers import Container
from .commerce import Currency, Shop, ShopItem
from .phones import PhoneContact, Phone

logger = logging.getLogger(__name__)
db_file = 'world.yaml'
output_directory = 'world'


def get_classes():
    """Returns a list of all classes used in the database."""
    classes = []
    for cls in Base._decl_class_registry.values():
        if isclass(cls) and issubclass(cls, Base):
            classes.append(cls)
    return classes


def dump_object(obj):
    """Return object obj as a dictionary."""
    cls = obj.__class__
    if DataMixin in cls.__bases__:
        obj.save_data()
    columns = inspect(cls).columns
    d = {}
    for name, column in columns.items():
        value = getattr(obj, name)
        if (
            column.nullable is True and value is None
        ) or (
            column.default is not None and value == column.default.arg
        ):
            continue
        d[name] = value
    return d


def finalise_db():
    """Create skeleton objects."""
    with session() as s:
        if not s.query(Zone).count():
            s.add(Zone(name='The First Zone'))
            s.commit()
        if not s.query(Room).count():
            s.add(
                Room(name='The First Room', zone_id=1)
            )
        s.commit()
        if not s.query(Command).count():
            for path in glob(os.path.join('commands', '*.command')):
                fname = os.path.basename(path)
                name = os.path.splitext(fname)[0]
                with open(path, 'r') as f:
                    cmd = Command(name=name)
                    cmd.set_code(f.read())
                    logger.info('Loaded %s from %s.', cmd.name, path)
                    s.add(cmd)
        if not s.query(Hotkey).count():
            for path in glob(os.path.join('hotkeys', '*.command')):
                fname = os.path.basename(path)
                name = os.path.splitext(fname)[0].upper()
                with open(path, 'r') as f:
                    description, code = f.read().split('\n', 1)
                key = Hotkey(name=name, description=description)
                key.set_code(code)
                logger.info('Loaded %s from %s.', key.name, path)
                s.add(key)
        s.commit()
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
        if not Gender.count():
            s.add(Gender(name='Neutral'))
            s.add(
                Gender(
                    name='Male',
                    subjective='he',
                    objective='him',
                    possessive_adjective='his',
                    possessive_noun='his',
                    reflexive='himself'
                )
            )
            s.add(
                Gender(
                    name='Female',
                    subjective='she',
                    objective='her',
                    possessive_adjective='her',
                    possessive_noun='hers',
                    reflexive='herself'
                )
            )


def load_db():
    """Load the database from a single flat file."""
    logger.info('Creating database tables...')
    Base.metadata.create_all()
    if os.path.isfile(db_file):
        logger.info('Loading the database from %s.', db_file)
        with open(db_file, 'r') as f:
            y = load(f)
        with session() as s:
            objects = dumper_load(y, get_classes())
            s.add_all(objects)
    else:
        logger.info('Starting with blank database.')
    finalise_db()


def dump_db(where=None):
    """Dump the database to single files."""
    if where is None:
        where = db_file
    logger.info('Dumping the database to %s.', where)
    objects = []
    for cls in get_classes():
        objects.extend(Session.query(cls))
    y = dumper_dump(objects, dump_object)
    with open(where, 'w') as f:
        dump(y, stream=f)
    return len(objects)


__all__ = (
    'engine', 'Session', 'session', 'Base', 'dump_object', 'Room',
    'RoomRandomSound', 'Player', 'Object', 'Action', 'ObjectAction',
    'load_db', 'dump_db', 'Entrance', 'Zone', 'Direction', 'Advert', 'Command',
    'Hotkey', 'Action', 'Revision', 'HotkeySecondary', 'CommunicationChannel',
    'CommunicationChannelListener', 'CommunicationChannelMessage',
    'CommunicationChannelBan', 'TransmitionError', 'Rule', 'HelpTopicKeyword',
    'HelpTopic', 'HelpKeyword', 'ServerOptions', 'Mobile', 'Social',
    'ObjectRandomSound', 'output_directory', 'Window', 'IdeaVote', 'Idea',
    'IdeaComment', 'ChangelogEntry', 'MailMessage', 'LoggedCommand', 'Credit',
    'StarshipEngine', 'RoomFloorType', 'ObjectTypeActionSecondary',
    'ObjectTypeHotkeySecondary', 'ObjectTypeSecondary', 'ObjectType', 'Orbit',
    'Starship', 'StarshipSensors', 'Star', 'Task', 'TransitStop',
    'TransitRoute', 'get_classes', 'finalise_db', 'RoomAirlock', 'Gender',
    'Chair', 'RestingStates', 'Container', 'Currency', 'Shop', 'ShopItem',
    'PhoneContact', 'Phone'
)
