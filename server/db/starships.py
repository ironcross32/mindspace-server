"""Provides the StarshipEngine class."""

import os.path
from sqlalchemy import Column, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, LandMixin, LaunchMixin
from ..distance import km, ly
from ..sound import get_sound, NoSuchSound
from ..protocol import hidden_sound


class StarshipEngine(Base, NameMixin):
    """An engine for a starship."""

    __tablename__ = 'starship_engines'
    max_acceleration = Column(Float, nullable=False, default=km)
    launch_speed = Column(Float, nullable=False, default=0.1)
    land_speed = Column(Float, nullable=False, default=1.0)


class StarshipSensors(Base, NameMixin):
    """A sensor array for starships."""

    __tablename__ = 'starship_sensors'
    distance = Column(Float, nullable=False, default=ly)


class Starship(Base, LandMixin, LaunchMixin):
    """Make a Zone a starship."""

    __tablename__ = 'starships'
    # Null means in space, False means ascending, and True means landing.
    landing = Column(Boolean, nullable=True)
    engine_id = Column(
        Integer, ForeignKey('starship_engines.id'), nullable=True
    )
    engine = relationship('StarshipEngine', backref='starships')
    sensors_id = Column(
        Integer, ForeignKey('starship_sensors.id'), nullable=True
    )
    sensors = relationship('StarshipSensors', backref='starships')
    last_scanned_id = Column(Integer, ForeignKey('zones.id'), nullable=True)
    last_scanned = relationship(
        'Zone', backref='scanned_by', foreign_keys=[last_scanned_id]
    )
    filter_star = Column(Boolean, nullable=False, default=False)
    filter_starship = Column(Boolean, nullable=False, default=False)
    filter_blackhole = Column(Boolean, nullable=False, default=False)
    target_object_id = Column(Integer, ForeignKey('zones.id'), nullable=True)
    target_object = relationship(
        'Zone', backref='converging', foreign_keys=[target_object_id]
    )
    target_x = Column(Float, nullable=True)
    target_y = Column(Float, nullable=True)
    target_z = Column(Float, nullable=True)

    @property
    def target_coordinates(self):
        coords = (self.target_x, self.target_y, self.target_z)
        if all(c is not None for c in coords):
            return coords

    @target_coordinates.setter
    def target_coordinates(self, value):
        (self.target_x, self.target_y, self.target_z) = value

    def get_sound_coordinates(self, obj, player):
        """Return the coordinates where relative sounds should be played,
        taking into account object and player coordinates, as well as
        player.location.max_distance."""
        zone = self.zone
        coordinates = []
        for name in ('x', 'y', 'z'):
            c = max(
                getattr(obj, name),
                getattr(zone, name)
            ) - min(
                getattr(obj, name),
                getattr(zone, name)
            )
            if getattr(zone, name) > getattr(obj, name):
                c *= -1
            c *= player.location.max_distance
            c /= self.sensors.distance
            c += getattr(player, name)
            coordinates.append(c)
        return coordinates

    def play_object_sound(self, obj, player):
        """Plays a sound representing obj to player."""
        try:
            sound = get_sound(os.path.join('sensors', obj.get_type() + '.wav'))
            hidden_sound(
                player.get_connection(), sound,
                self.get_sound_coordinates(obj, player), False
            )
            return True
        except NoSuchSound:
            return False

    def get_filters(self):
        """Return a list of everything this array is filtering."""
        filters = []
        for x in dir(self):
            if x.startswith('filter_') and getattr(self, x):
                filters.append(x[7:].title())
        return filters

    def set_acceleration(self, factor, accelerating=None):
        """Set how much this ship is accelerating by. Factor should be between
        0.0 (not accelerating) and 1.0 (full thrust). Can overload for fun. If
        accelerating is left at None then it will remain unchanged."""
        z = self.zone
        z.acceleration = self.engine.max_acceleration * factor
        if accelerating is not None:
            z.accelerating = accelerating
        z.ambience_rate = factor
        z.update_occupants()
