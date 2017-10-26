"""Provides the Base class and various mixins."""

import os
import os.path
from time import time
from inspect import isclass
from random import choice, uniform
from functools import partial
from attr import asdict
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from .engine import engine
from .session import Session
from ..protocol import identify, random_sound
from ..sound import sounds_dir, get_sound
from ..util import now
from ..forms import Label, Field

ambiences_dir = os.path.join(sounds_dir, 'ambiences')
random_sounds_dir = os.path.join(sounds_dir, 'random')


def dump_object(obj):
    """Get this object as a dict."""

    def should_dump(self, attr, value):
        """Decide if the attribute should be dumped or not."""
        column = self.__table__.c[attr.name]
        default = column.default
        if default is not None:
            return not value == default.arg
        elif self.__table__.c[attr.name].nullable and value is None:
            return False
        else:
            return True

    return asdict(obj, filter=partial(should_dump, obj))


class _Base:
    """The base class for declarative."""

    id = Column(Integer, primary_key=True)

    def duplicate(self):
        """Return a new object that is just like this one."""
        cls = self.__class__
        kwargs = {
            x: y for x, y in asdict(self).items() if not x.endswith('_id')
        }
        del kwargs['id']
        return cls(**kwargs)

    @classmethod
    def count(cls):
        return Session.query(cls).count()

    @classmethod
    def query(cls, *args, **kwargs):
        """Perform a query against this class."""
        return Session.query(cls).filter(*args).filter_by(**kwargs)

    @classmethod
    def first(cls):
        return cls.query().first()

    @classmethod
    def join(cls, *args, **kwargs):
        """Return a query object with a join."""
        return Session.query(cls).join(*args, **kwargs)

    @classmethod
    def get(cls, id):
        """Return a row with the exact id."""
        return Session.query(cls).get(id)

    @classmethod
    def code_lines(cls):
        """Get the number of lines of code in the database."""
        lines = 0
        for base in cls._decl_class_registry.values():
            if hasattr(
                base, 'code'
            ) and base is not CodeMixin and base.__name__ != 'Revision':
                for obj in Session.query(base).filter(base.code.isnot(None)):
                    if obj.code is not None:
                        lines += len(obj.code.splitlines())
        return lines

    @classmethod
    def number_od_objects(cls):
        """Return the number of objects in the database."""
        n = 0
        for base in cls._decl_class_registry.values():
            if isclass(base):
                n += Session.query(base).count()
        return n

    def make_field(self, name, **kwargs):
        return Field(name, getattr(self, name), **kwargs)

    def get_all_fields(self):
        fields = []
        for base in self.__class__.__bases__:
            if not hasattr(base, 'get_fields'):
                continue
            fields.append(Label(base.__name__[:-len('Mixin')]))
            fields.extend(base.get_fields(self))
        return fields


Base = declarative_base(cls=_Base, bind=engine)


class NameMixin:
    name = Column(String(50), nullable=True)
    last_name_change = Column(DateTime(timezone=True), nullable=True)

    @classmethod
    def get_fields(cls, instance):
        return [instance.make_field('name')]

    def get_name(self, verbose=False):
        """Return a proper name for this object."""
        if self.name is None:
            name = self.get_type()
        else:
            name = self.name
        if verbose:
            return f'{name} (#{self.id})'
        else:
            return name

    def set_name(self, value):
        """Set self.name. No saving is performed."""
        self.name = value
        self.last_name_change = now()


class PermissionsMixin:
    builder = Column(Boolean, nullable=False, default=False)
    admin = Column(Boolean, nullable=False, default=False)

    @classmethod
    def get_fields(cls, instance):
        fields = []
        for name in ('builder', 'admin'):
            fields.append(instance.make_field(name, type=bool))
        return fields


class RandomSoundMixin(NameMixin):
    """A random sound."""

    min_volume = Column(Float, nullable=False, default=0.01)
    max_volume = Column(Float, nullable=False, default=1.0)

    def get_all_fields(self):
        fields = [
            Label('Edit'),
            self.make_field('name', type=sorted(os.listdir(random_sounds_dir)))
        ]
        for name in ('min_volume', 'max_volume'):
            fields.append(self.make_field(name, type=float))
        return fields


class DescriptionMixin:
    """Add a description."""
    description = Column(String(500), nullable=True)

    @classmethod
    def get_fields(cls, instance):
        return [instance.make_field('description')]

    def get_description(self):
        return self.description or 'You see nothing special.'

    def set_description(self, value):
        self.description = value or None


class CoordinatesMixin:
    x = Column(Float, nullable=False, default=0.0)
    y = Column(Float, nullable=False, default=0.0)
    z = Column(Float, nullable=False, default=0.0)

    @classmethod
    def get_fields(cls, instance):
        return [
            instance.make_field(name, type=float) for name in ('x', 'y', 'z')
        ]

    @property
    def coordinates(self):
        return (self.x, self.y, self.z)

    @coordinates.setter
    def coordinates(self, value):
        self.x, self.y, self.z = value


class SizeMixin:
    size_x = Column(Float, nullable=False, default=10.0)
    size_y = Column(Float, nullable=False, default=10.0)
    size_z = Column(Float, nullable=False, default=10.0)

    @classmethod
    def get_fields(cls, instance):
        return [
            instance.make_field(
                f'size_{name}', type=float
            ) for name in ('x', 'y', 'z')
        ]

    @property
    def size(self):
        return (self.size_x, self.size_y, self.size_z)

    @size.setter
    def size(self, value):
        self.size_x, self.size_y, self.size_z = value

    def coordinates_ok(self, coordinates):
        """Ensure coordinates are within the bounds of this object."""
        x, y, z = coordinates
        return (
            x >= 0 and x <= self.size_x
        ) and (
            y >= 0 and y <= self.size_y
        ) and (
            z >= 0 and z <= self.size_z
        )

    def random_coordinates(self):
        """Return a set of random coordinates."""
        return (
            uniform(0.0, self.size_x),
            uniform(0.0, self.size_y),
            uniform(0.0, self.size_z)
        )


class AmbienceMixin:
    ambience = Column(String(100), nullable=True)
    ambience_volume = Column(Float, nullable=False, default=1.0)

    @classmethod
    def get_fields(cls, instance):
        return [
            instance.make_field('ambience', type=instance.ambience_choices()),
            instance.make_field('ambience_volume', type=float)
        ]

    def ambience_choices(self):
        return [None] + sorted(os.listdir(ambiences_dir))


class LocationMixin:
    """Adds location information to objects."""
    @declared_attr
    def location_id(cls):
        return Column(
            Integer,
            ForeignKey('rooms.id'),
            nullable=True
        )

    @declared_attr
    def location(cls):
        return relationship(
            'Room', backref=cls.__tablename__, foreign_keys=[cls.location_id],
            remote_side='Room.id'
        )

    def update_neighbours(self):
        """Notify everyone in the current room that this object's state has
        changed."""
        return self.location.broadcast_command(identify, self)


class OwnerMixin:
    """Adds ownership information to objects."""
    @declared_attr
    def owner_id(cls):
        return Column(
            Integer,
            ForeignKey('objects.id'),
            nullable=True
        )

    @declared_attr
    def owner(cls):
        return relationship(
            'Object', backref=f'owned_{cls.__tablename__}',
            foreign_keys=[cls.owner_id],
            remote_side='Object.id'
        )


class CodeMixin:
    code = Column(String(1000000), default=False)

    def set_code(self, code):
        """Compile the code to ensure it's all going to work."""
        compile(code, self.name, 'exec')
        if self.id is not None and self.code is not None and \
           self.revision is None:
            self.backup()
        self.code = code

    @classmethod
    def get_fields(self, instance):
        return [instance.make_field('code')]

    def backup(self):
        """Backup the code in this object. Typically performed as part of a
        set_code call."""
        table = Base.metadata.tables['revisions']
        engine = Base.metadata.bind
        ins = table.insert()
        return engine.execute(
            ins, code=self.code, object_class_name=self.__class__.__name__,
            object_id=self.id
        )

    @property
    def revisions(self):
        """Return a list of revisions for this object."""
        revision_class = Base._decl_class_registry['Revision']
        return Session.query(revision_class).filter_by(
            object_id=self.id, object_class_name=self.__class__.__name__
        ).all()

    @property
    def revision(self):
        """Return the revision which holds the current version of the code (if
        any)."""
        return Session.query(Base._decl_class_registry['Revision']).filter_by(
            code=self.code, object_id=self.id,
            object_class_name=self.__class__.__name__
        ).first()


class DirectionMixin:

    @declared_attr
    def direction_id(cls):
        return Column(Integer, ForeignKey('directions.id'), nullable=True)

    @declared_attr
    def direction(cls):
        return relationship(
            'Direction', backref=f'traveling_{cls.__tablename__}'
        )

    @classmethod
    def get_fields(cls, instance):
        d = {None: 'None'}
        for direction in Base._decl_class_registry['Direction'].query():
            d[direction.id] = direction.get_name(True)
        return [instance.make_field('direction_id', type=d)]


class CommunicationChannelMixin:
    @declared_attr
    def channel_id(cls):
        return Column(
            Integer, ForeignKey('communication_channels.id'), nullable=False
        )


class RandomSoundContainerMixin:
    """Add random sound support to bases. Assumed this class has a list-like
    attribute called random_sounds."""

    next_random_sound = Column(Float, nullable=True)
    min_random_sound_interval = Column(Float, nullable=False, default=5.0)
    max_random_sound_interval = Column(Float, nullable=False, default=15.0)

    def add_random_sound(self, sound):
        """Add a sound to this object."""
        assert sound in os.listdir(random_sounds_dir)
        obj = self.make_random_sound(sound)
        self.random_sounds.append(obj)
        if self.next_random_sound is None:
            self.next_random_sound = 0.0
        return obj

    def remove_random_sound(self, sound):
        """Remove a random sound from this object."""
        self.random_sounds.remove(sound)
        if not self.random_sounds:
            self.next_random_sound = None

    def play_random_sound(self):
        """Play a random sound."""
        sound = choice(self.random_sounds)
        min_volume = sound.min_volume
        max_volume = sound.max_volume
        sound = get_sound(os.path.join(random_sounds_dir, sound.name))
        cls = self.__class__
        if cls.__name__ == 'Object':
            self.sound(sound)
        else:
            volume = uniform(min_volume, max_volume)
            if LocationMixin in cls.__bases__:
                location = self.location
            elif cls.__name__ == 'Room':
                location = self
            else:
                location = self.object.location
            coordinates = location.random_coordinates()
            location.broadcast_command(
                random_sound, sound, *coordinates, volume
            )
        self.next_random_sound = time() + uniform(
            self.min_random_sound_interval, self.max_random_sound_interval
        )

    def get_all_fields(self):
        fields = []
        fields.append(Label('Random Sounds'))
        for name in ('min_random_sound_interval', 'max_random_sound_interval'):
            fields.append(self.make_field(name))
        return fields


class TextMixin:
    text = Column(String(10000), nullable=False)

    @classmethod
    def get_fields(cls, instance):
        return [instance.make_field('text')]
