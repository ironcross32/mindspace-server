"""Provides the Room class."""

import os
import os.path
from sqlalchemy import Column, Float, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, SizeMixin, NameMixin, DescriptionMixin, AmbienceMixin,
    RandomSoundMixin, RandomSoundContainerMixin
)
from .session import Session
from ..protocol import hidden_sound, reverb_property_names
from ..sound import get_sound, sounds_dir
from ..forms import Label

floor_types_dir = os.path.join(sounds_dir, 'Footsteps')
music_dir = os.path.join(sounds_dir, 'music')


@attrs_sqlalchemy
class RoomRandomSound(RandomSoundMixin, Base):
    """A random sound for rooms."""

    __tablename__ = 'room_random_sounds'
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship('Room', backref='random_sounds')


@attrs_sqlalchemy
class Room(
    Base, NameMixin, DescriptionMixin, SizeMixin, AmbienceMixin,
    RandomSoundContainerMixin
):
    """A room."""

    __tablename__ = 'rooms'
    music = Column(String(100), nullable=True)
    mul = Column(Float, nullable=False, default=1.0)
    max_distance = Column(Float, nullable=False, default=100.0)
    visibility = Column(Float, nullable=False, default=1500.0)
    cutoff_frequency = Column(Integer, nullable=False, default=5000)
    delay_modulation_depth = Column(Float, nullable=False, default=0.0)
    delay_modulation_frequency = Column(Float, nullable=False, default=10.0)
    density = Column(Float, nullable=False, default=0.5)
    t60 = Column(Float, nullable=False, default=1.0)
    floor_type = Column(String(20), nullable=False, default='grass')
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=True)
    zone = relationship('Zone', backref='rooms', foreign_keys=[zone_id])

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.append(Label('Distances'))
        for name in ('visibility', 'max_distance'):
            fields.append(self.make_field(name), type=float)
        fields.extend(RandomSoundContainerMixin.get_all_fields(self))
        fields.append(Label('Background'))
        for name in ('music', 'floor_type'):
            fields.append(
                self.make_field(
                    name, type=getattr(
                        self, f'{name}_choices'
                    )()
                )
            )
        for name in reverb_property_names:
            fields.append(
                self.make_field(name, type=float)
            )
        return fields

    def music_choices(self):
        return [None] + sorted(os.listdir(music_dir))

    def floor_type_choices(self):
        return [None] + sorted(os.listdir(floor_types_dir))

    @property
    def exits(self):
        """Return all the objects in this room that are exits."""
        return [x for x in self.objects if x.edit is not None]

    def broadcast_command(self, command, *args, _who=None, **kwargs):
        """Send a command to everyone in the room. If _who is not None only
        objects within self.max_distance will hear about it."""
        if _who is None:
            objects = self.objects
        else:
            Object = _who.__class__
            md = self.max_distance
            query_args = [Object.location_id == self.id]
            for name in ('x', 'y', 'z'):
                query_args.append(
                    getattr(Object, name).between(
                        getattr(_who, name) - md,
                        getattr(_who, name) + md
                    )
                )
            objects = Session.query(Object).filter(*query_args)
        for obj in objects:
            con = obj.get_connection()
            if con is not None:
                command(con, *args, **kwargs)

    def broadcast_command_selective(self, func, command, *args, **kwargs):
        """Send a command to any object for whom func(object) evaluates to
        True."""
        for obj in self.objects:
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

    def get_walk_sound(self):
        """Return a suitable footstep sound for this room."""
        return get_sound(
            os.path.join('Footsteps', self.floor_type)
        )

    def make_random_sound(self, name):
        """Make an instance of RoomRandomSound."""
        return RoomRandomSound(room=self, name=name)
