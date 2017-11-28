"""Provides the Room class."""

import sys
import os
import os.path
from sqlalchemy import Column, Float, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, SizeMixin, NameMixin, DescriptionMixin, AmbienceMixin,
    RandomSoundMixin, RandomSoundContainerMixin, CoordinatesMixin, ZoneMixin,
    message
)
from ..protocol import hidden_sound
from ..sound import get_sound, sounds_dir
from ..forms import Label

floor_types_dir = os.path.join(sounds_dir, 'Footsteps')
music_dir = os.path.join(sounds_dir, 'music')
impulses_dir = os.path.join(sounds_dir, 'impulses')


class RoomRandomSound(RandomSoundMixin, Base):
    """A random sound for rooms."""

    __tablename__ = 'room_random_sounds'
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship('Room', backref='random_sounds')


class RoomFloorType(Base, CoordinatesMixin, NameMixin):
    """An altered floor type for a room."""

    __tablename__ = 'room_floor_types'
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship('Room', backref='floor_types')


class RoomAirlock(Base):
    """An airlock for a room."""

    __tablename__ = 'room_airlocks'
    board_msg = message('%1n|normal board%1s %2n.')
    board_sound = message(nullable=True)
    leave_msg = message('%1n|normal disembark%1s from %2n.')
    leave_sound = message(nullable=True)


class Room(
    Base, NameMixin, DescriptionMixin, SizeMixin, AmbienceMixin,
    RandomSoundContainerMixin, ZoneMixin
):
    """A room."""

    __tablename__ = 'rooms'
    airlock_id = Column(Integer, ForeignKey('room_airlocks.id'), nullable=True)
    airlock = relationship(
        'RoomAirlock', backref=backref('room', uselist=False)
    )
    music = Column(String(100), nullable=True)
    convolver = Column(String(100), nullable=True)
    convolver_volume = Column(Float, nullable=False, default=1.0)
    max_distance = Column(Float, nullable=False, default=100.0)
    visibility = Column(Float, nullable=False, default=1500.0)
    floor_type = Column(String(20), nullable=True, default='grass')

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.append(Label('Distances'))
        for name in ('visibility', 'max_distance'):
            fields.append(self.make_field(name, type=float))
        fields.extend(RandomSoundContainerMixin.get_all_fields(self))
        fields.append(Label('Background'))
        for name in ('music', 'floor_type', 'convolver'):
            fields.append(
                self.make_field(
                    name, type=getattr(
                        self, f'{name}_choices'
                    )()
                )
            )
        fields.append(self.make_field('convolver_volume', type=float))
        for name in ('airlock',):
            fields.append(self.make_field(name, type=bool))
        return fields

    def music_choices(self):
        return [None] + sorted(os.listdir(music_dir))

    def convolver_choices(self):
        res = [None]
        for top, directories, filenames in os.walk(impulses_dir):
            for filename in filenames:
                full = os.path.join(top[len(impulses_dir) + 1:], filename)
                name, ext = os.path.splitext(filename)
                if ext in ('.wav', '.m4a'):
                    readme = os.path.join(
                        top, name + '.attribution.txt'
                    )
                    if os.path.isfile(readme):
                        with open(readme, 'rb') as f:
                            try:
                                lines = [
                                    x for x in f.readlines() if x.startswith(
                                        b'"'
                                    )
                                ]
                            except Exception as e:
                                err = f'Unable to read file {readme}: {e}."'
                                err = err.encode()
                                lines = [err]
                            description = b'. '.join(lines).decode(
                                sys.getdefaultencoding(), 'replace'
                            )
                    else:
                        description = 'No description available.'
                    res.append([full, f'{filename}: {description.strip()}'])
        return res

    def floor_type_choices(self):
        return [None] + sorted(os.listdir(floor_types_dir))

    @property
    def exits(self):
        """Return all the objects in this room that are exits."""
        return [x for x in self.objects if x.is_exit]

    def broadcast_command(self, *args, **kwargs):
        """Send a command to everyone in the room. If _who is not None only
        objects within self.max_distance will hear about it."""
        return self.broadcast_command_selective(
            lambda obj: True, *args, **kwargs
        )

    def broadcast_command_selective(
        self, func, command, *args, _who=None, **kwargs
    ):
        """Send a command to any object for whom func(object) evaluates to
        True. For further usage see the docstring for broadcast_command."""
        if _who is None:
            objects = self.objects
        else:
            Object = _who.__class__
            md = self.max_distance * _who.max_distance_multiplier
            query_args = [Object.location_id == self.id]
            for name in ('x', 'y', 'z'):
                query_args.append(
                    getattr(Object, name).between(
                        getattr(_who, name) - md,
                        getattr(_who, name) + md
                    )
                )
            objects = Object.query(*query_args)
        for obj in objects:
            con = obj.get_connection()
            if con is not None and func(obj):
                command(con, *args, **kwargs)

    def sound(self, sound, coordinates, is_dry=False, selector=None):
        """The provided sound will be heard at the specified coordinates by
        anyone in the room. If selector is not None, only objects for whom
        selector(object) evaluates to True will hear the sound."""
        args = (hidden_sound, sound, *coordinates, is_dry)
        if selector is None:
            func = self.broadcast_command
        else:
            args = (selector, *args)
            func = self.broadcast_command_selective
        return func(*args)

    def get_walk_sound(self, coordinates=None):
        """Return a suitable footstep sound for this room."""
        name = None
        if coordinates is not None:
            x, y, z = coordinates
            covering = RoomFloorType.query(
                room_id=self.id, x=x, y=y, z=z
            ).first()
            if covering is not None:
                name = covering.name
        if self.floor_type is not None and covering is None:
            name = self.floor_type
        if name is not None:
            return get_sound(
                os.path.join('Footsteps', name)
            )

    def make_random_sound(self, name):
        """Make an instance of RoomRandomSound."""
        return RoomRandomSound(room=self, name=name)
