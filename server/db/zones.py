"""Provides the Zone class."""

from sqlalchemy import Column, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, CoordinatesMixin, NameMixin, DescriptionMixin, OwnerMixin,
    DirectionMixin, AmbienceMixin, StarshipMixin, HiddenMixin
)
from ..forms import Label
from ..protocol import zone
from ..util import distance_between


class Zone(
    Base, CoordinatesMixin, NameMixin, DescriptionMixin, OwnerMixin,
    DirectionMixin, AmbienceMixin, StarshipMixin, HiddenMixin
):
    """A zone which contains 0 or more rooms."""

    __tablename__ = 'zones'
    speed = Column(Float, nullable=True)
    acceleration = Column(Float, nullable=True)
    accelerating = Column(Boolean, nullable=False, default=True)
    star_id = Column(Integer, ForeignKey('stars.id'), nullable=True)
    star = relationship('Star', backref=backref('object', uselist=False))
    last_turn = Column(Float, nullable=False, default=0.0)
    ambience_rate = Column(Float, nullable=False, default=1.0)
    ambience_volume = Column(Float, nullable=False, default=1.0)
    speed = Column(Float, nullable=True)

    @property
    def is_starship(self):
        return self.starship is not None

    @property
    def is_star(self):
        return self.star is not None

    def get_type(self):
        """Get an appropriate type."""
        if self.is_starship:
            return 'Starship'
        elif self.is_star:
            return 'Star'
        else:
            return 'Debris'

    def get_all_fields(self):
        fields = [Label(f'Configure {self.get_name(True)}')]
        fields.extend(NameMixin.get_fields(self))
        fields.extend(DescriptionMixin.get_fields(self))
        fields.extend(DirectionMixin.get_fields(self))
        fields.extend(CoordinatesMixin.get_fields(self))
        for name in ('ambience_rate', 'ambience_volume', 'speed'):
            fields.append(self.make_field(name, type=float))
        return fields

    def update_occupants(self):
        """Tell everyone inside this zone it has changed."""
        for room in self.rooms:
            for obj in room.objects:
                con = obj.get_connection()
                if con is not None:
                    zone(con, self)

    def visible_objects(self, sort=True):
        """Get the objects in sensor range."""
        cls = self.__class__
        args = [cls.id != self.id]
        for name in ('x', 'y', 'z'):
            args.append(
                getattr(cls, name).between(
                    getattr(self, name) - self.starship.sensors.distance,
                    getattr(self, name) + self.starship.sensors.distance
                )
            )
        objects = cls.query(*args)
        if sort:
            objects = sorted(
                objects,
                key=lambda value: distance_between(
                    self.coordinates, value.coordinates
                )
            )
        for name in dir(self.starship):
            if name.startswith(
                'filter_'
            ) and getattr(
                self.starship, name
            ):
                type = name[7:].title()
                objects = [x for x in objects if x.get_type() != type]
        return objects
