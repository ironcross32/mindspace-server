"""Provides the Mobile class."""

from time import time
from random import uniform, choice
from sqlalchemy import Column, Float, Boolean
from .base import Base, Sound, PauseMixin
from .directions import Direction
from .objects import Object
from .entrances import Entrance
from .session import Session
from ..sound import get_sound
from ..util import walk


class Mobile(Base, PauseMixin):
    """Make an object mobile."""

    __tablename__ = 'mobiles'
    move_silently = Column(Boolean, nullable=False, default=False)
    move_sound = Column(Sound, nullable=True)
    next_move = Column(Float, nullable=False, default=0.0)
    min_move_interval = Column(Float, nullable=False, default=5.0)
    max_move_interval = Column(Float, nullable=False, default=15.0)
    follow_exits = Column(Boolean, nullable=False, default=False)

    def get_move_sound(self):
        """Get an appropriate movement sound for this object."""
        if self.move_silently:
            return
        elif self.move_sound is None:
            return self.object.location.get_walk_sound()
        else:
            return get_sound(self.move_sound)

    def move(self):
        """Move this object a bit."""
        obj = self.object
        loc = obj.location
        x, y, z = obj.coordinates
        self.next_move = time() + uniform(
            self.min_move_interval, self.max_move_interval
        )
        Session.add(self)
        if self.follow_exits:
            # Let's find us an exit.
            args = [
                Object.location_id == loc.id,
                Object.exit_id.isnot(None),
                Object.x == x,
                Object.y == y,
                Object.z == z,
                Entrance.no_mobiles.is_(False),
                Entrance.locked.is_(False)
            ]
            if obj.recent_exit_id is not None:
                args.append(Object.id != obj.recent_exit_id)
            exits = Object.join(Entrance).filter(*args).all()
            if exits:
                # We found one.
                exit = choice(exits)
                # Let's use the exit.
                return exit.use_exit(obj)
        # Let's find a random direction.
        args = []
        for name in ('x', 'y'):
            value = getattr(obj, name)
            if not value:
                args.append(getattr(Direction, name) != -1.0)
            elif value == getattr(loc, f'size_{name}'):
                args.append(getattr(Direction, name) != 1.0)
        if obj.recent_direction_id is not None:
            args.append(Direction.id != obj.recent_direction.opposite_id)
        obj.recent_direction_id = None
        directions = Direction.query(*args, z=0.0).all()
        if directions:
            # We're not stuck.
            direction = choice(directions)
            coordinates = direction.coordinates_from(obj.coordinates)
            if loc.coordinates_ok(coordinates):
                sound = self.get_move_sound()
                x, y, z = direction.coordinates
                walk(obj, x=x, y=y, z=z, sound=sound)
