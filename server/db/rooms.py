"""Provides the Room class."""

import sys
import os
import os.path
from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, SizeMixin, NameMixin, DescriptionMixin, AmbienceMixin,
    RandomSoundMixin, RandomSoundContainerMixin, CoordinatesMixin, ZoneMixin,
    BoardMixin, LeaveMixin, Sound, message
)
from ..protocol import hidden_sound
from ..sound import get_sound, sounds_dir
from ..socials import factory

floor_types_dir = os.path.join(sounds_dir, 'footsteps')
music_dir = os.path.join(sounds_dir, 'music')
impulses_dir = os.path.join(sounds_dir, 'impulses')


class RoomRandomSound(RandomSoundMixin, Base):
    """A random sound for rooms."""

    __tablename__ = 'room_random_sounds'
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship('Room', backref='random_sounds')


class RoomFloorTile(Base, NameMixin):
    """An altered floor type for a room."""

    __tablename__ = 'room_floor_tiles'
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship('Room', backref='tiles')
    start_x = Column(Float, nullable=False)
    start_y = Column(Float, nullable=False)
    start_z = Column(Float, nullable=False)
    end_x = Column(Float, nullable=False)
    end_y = Column(Float, nullable=False)
    end_z = Column(Float, nullable=False)
    floor_type = message(None)
    step_on_msg = message('%1N step%1s onto %2n.')
    step_off_msg = message('%1N step%1s off %2n.')

    @property
    def start_coordinates(self):
        """Return start coordinates."""
        return (self.start_x, self.start_y, self.start_z)

    @start_coordinates.setter
    def start_coordinates(self, value):
        self.start_x, self.start_y, self.start_z = value

    @property
    def end_coordinates(self):
        """Return end coordinates."""
        return (self.end_x, self.end_y, self.end_z)

    @end_coordinates.setter
    def end_coordinates(self, value):
        self.end_x, self.end_y, self.end_z = value

    def covers(self, x, y, z):
        """Returns True if this tile covers the given coordinates, and False
        otherwise."""
        if self.start_x <= x and self.end_x >= x and self.end_z >= z:
            # Passed the x check, now let's check y.
            return self.start_y <= y and self.end_y >= y and self.end_z >= z
        return False

    def step_on(self, obj):
        """Object obj has stepped onto this tile."""
        self.tell_object(obj, self.step_on_msg)

    def step_off(self, obj):
        """Object obj has stepped off this tile."""
        self.tell_object(obj, self.step_off_msg)

    def tell_object(self, obj, msg):
        """Tell message msg to Object obj."""
        string = factory.get_strings(msg, [obj, self])[0]
        obj.message(string)


class RoomAirlock(Base, CoordinatesMixin, BoardMixin, LeaveMixin):
    """An airlock for a room."""

    __tablename__ = 'room_airlocks'


class Room(
    Base, NameMixin, DescriptionMixin, SizeMixin, AmbienceMixin,
    RandomSoundContainerMixin, ZoneMixin
):
    """A room."""

    __tablename__ = 'rooms'
    cant_go_sound = Column(
        Sound, nullable=False, default=os.path.join('cantgo', 'default')
    )
    cant_go_msg = message('You cannot go that way.')
    airlock_id = Column(Integer, ForeignKey('room_airlocks.id'), nullable=True)
    airlock = relationship(
        'RoomAirlock', backref=backref('room', uselist=False)
    )
    music = Column(Sound, nullable=True)
    convolver = Column(Sound, nullable=True)
    convolver_volume = Column(Float, nullable=False, default=1.0)
    max_distance = Column(Float, nullable=False, default=100.0)
    visibility = Column(Float, nullable=False, default=1500.0)
    floor_type = Column(
        Sound, nullable=True, default=os.path.join(floor_types_dir, 'grass')
    )

    def tile_at(self, x, y, z):
        """Return the tile that spans the given coordinates."""
        return RoomFloorTile.query(
            RoomFloorTile.start_x <= x, RoomFloorTile.start_y <= y,
            RoomFloorTile.start_z <= z, RoomFloorTile.end_x >= x,
            RoomFloorTile.end_y >= y, RoomFloorTile.end_z >= z,
            RoomFloorTile.room_id == self.id
        ).order_by(RoomFloorTile.id.desc()).first()

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

    def get_walk_sound(self, coordinates=None, covering=None):
        """Return a suitable footstep sound for this room. If coordinates is
        None then this room's overall walk sound will be returned, otherwise a
        tile will be searched for. If covering is not None then it will be used
        instead of querying for a tile."""
        name = None
        if coordinates is not None:
            x, y, z = coordinates
            if covering is None:
                covering = self.tile_at(x, y, z)
            if covering is not None:
                name = covering.floor_type
        else:
            covering = None
        if self.floor_type is not None and covering is None:
            name = self.floor_type
        if name is not None:
            return get_sound(name)

    def make_random_sound(self, name):
        """Make an instance of RoomRandomSound."""
        return RoomRandomSound(room=self, name=name)
