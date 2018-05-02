"""Database."""

import os
import os.path
import logging
from inspect import isclass
from sqlalchemy import inspect, event
from twisted.internet import reactor
from yaml import dump, load
from db_dumper import load as dumper_load, dump as dumper_dump
from .engine import engine
from .session import Session, session
from .base import Base, DataMixin
from .rooms import Room, RoomRandomSound, RoomFloorType, RoomAirlock
from .players import Player, TextStyle
from .objects import Object, ObjectRandomSound, RestingStates
from .actions import Action, ObjectAction
from .entrances import Entrance
from .starships import Starship, StarshipSensors, StarshipEngine
from .zones import Zone
from .directions import Direction
from .adverts import Advert
from .commands import Command
from .hotkeys import Hotkey, HotkeySecondary, RemappedHotkey
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
from .commerce import (
    Currency, Shop, ShopItem, CreditCard, CreditCardTransfer,
    TransferDirections, CreditCardError, Bank, BankAccountAccessor,
    BankAccount, ATM, ATMError, BankAccessError
)
from .phones import (
    PhoneContact, Phone, PhoneStates, BlockedPhoneAddress, TextMessage
)

logger = logging.getLogger(__name__)
db_file = 'world.yaml'
output_directory = 'world'


@event.listens_for(Session, 'before_flush')
def before_flush(s, ctx, instances):
    """Ensure everything goes with this object."""
    for obj in s.deleted:
        if isinstance(obj, Object):
            obj.delete_data()
            chair = obj.chair
            if chair is not None:
                for sitter in chair.occupants:
                    chair.use(sitter, RestingStates.standing)
                    s.add(sitter)
            for name in (
                'player', 'atm', 'phone', 'mobile', 'credit_card', 'exit',
                'window', 'chair', 'container', 'shop'
            ):
                related = getattr(obj, name)
                if related is not None:
                    s.delete(related)
        elif isinstance(obj, Shop):
            for item in obj.items:
                s.delete(item)


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
        if not ServerOptions.count():
            s.add(ServerOptions(name='Default'))
        options = ServerOptions.get()
        if Object.get(0) is None:
            s.add(Object(id=0, name='System', description='The System Object'))
        options.system_object_id = 0
        s.add(options)
        if not Zone.count():
            s.add(Zone(name='The First Zone'))
            s.commit()
        if not Room.count():
            s.add(
                Room(name='The First Room', zone_id=Zone.first().id)
            )
        options.first_room = Room.first()
        s.add(options)
        s.commit()
        if not Direction.count():
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
            for d in Direction.query():
                d.opposite = Direction.query(
                    x=d.x * -1, y=d.y * -1, z=d.z * -1
                ).first()
                s.add(d)
                s.commit()
        Player.query(connected=True).update({Player.connected: False})
        if not Gender.count():
            s.add(Gender(name='Neutral'))
            s.add(
                Gender(
                    name='Male', subjective='he', objective='him',
                    possessive_adjective='his', possessive_noun='his',
                    reflexive='himself'
                )
            )
            s.add(
                Gender(
                    name='Female', subjective='she', objective='her',
                    possessive_adjective='her', possessive_noun='hers',
                    reflexive='herself'
                )
            )


def load_db(filename=None):
    """Load the database from a single flat file. If filename is None use
    db_file."""
    if filename is None:
        filename = db_file
    if os.path.isfile(filename):
        logger.info('Loading the database from %s.', filename)
        with open(filename, 'r') as f:
            data = load(f)
        load_objects(data)
    else:
        logger.info('Starting with blank database.')
    finalise_db()


def load_objects(data):
    with session() as s:
        objects = dumper_load(data, get_classes())
        s.add_all(objects)


def objects_as_dicts():
    """Return all objects in the database as dictionaries suitable for
    dumping."""
    objects = []
    for cls in get_classes():
        objects.extend(Session.query(cls))
    return dumper_dump(objects, dump_object)


def dump_db(filename=None, thread=False):
    """Dump the database to single files."""
    if filename is None:
        filename = db_file
    logger.info('Dumping the database to %s.', filename)
    y = objects_as_dicts()
    args = (filename, y)
    if thread:
        reactor.callInThread(dump_objects, *args)
    else:
        dump_objects(*args)


def dump_objects(filename, d):
    """Dump dictionary d to the given filename."""
    with open(filename, 'w') as f:
        dump(d, stream=f)


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
    'PhoneContact', 'Phone', 'PhoneStates', 'BlockedPhoneAddress',
    'TextMessage', 'RemappedHotkey', 'CreditCard', 'CreditCardTransfer',
    'TransferDirections', 'CreditCardError', 'Bank', 'BankAccountAccessor',
    'BankAccount', 'ATM', 'ATMError', 'BankAccessError', 'TextStyle'
)
