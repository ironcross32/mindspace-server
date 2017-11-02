"""Provides the Zone class."""

import os
import os.path
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, CoordinatesMixin, NameMixin, DescriptionMixin, OwnerMixin,
    DirectionMixin
)
from ..forms import Label
from ..protocol import zone
from ..sound import sounds_dir
from ..util import distance_between


@attrs_sqlalchemy
class Zone(
    Base, CoordinatesMixin, NameMixin, DescriptionMixin, OwnerMixin,
    DirectionMixin
):
    """A zone which contains 0 or more rooms."""

    __tablename__ = 'zones'
    speed = Column(Float, nullable=True)
    acceleration = Column(Float, nullable=True)
    accelerating = Column(Boolean, nullable=False, default=True)
    starship_id = Column(Integer, ForeignKey('starships.id'), nullable=True)
    starship = relationship(
        'Starship', backref=backref('object', uselist=False),
        foreign_keys=[starship_id]
    )
    last_turn = Column(Float, nullable=False, default=0.0)
    background_sound = Column(String(150), nullable=True)
    background_rate = Column(Float, nullable=False, default=1.0)
    background_volume = Column(Float, nullable=False, default=1.0)
    speed = Column(Float, nullable=True)

    @property
    def is_starship(self):
        return self.starship is not None

    def get_type(self):
        """Get an appropriate type."""
        if self.is_starship:
            return 'Starship'
        else:
            return 'Debris'

    def get_all_fields(self):
        fields = [Label(f'Configure {self.get_name(True)}')]
        fields.extend(NameMixin.get_fields(self))
        fields.extend(DescriptionMixin.get_fields(self))
        fields.extend(DirectionMixin.get_fields(self))
        fields.extend(CoordinatesMixin.get_fields(self))
        for name in ('speed',):
            fields.append(self.make_field(name, type=float))
        fields.extend(
            [
                self.make_field(
                    'background_sound', type=[None] + sorted(
                        os.listdir(
                            os.path.join(
                                sounds_dir, 'zones'
                            )
                        )
                    )
                ),
                self.make_field('background_rate'),
                self.make_field('background_volume')
            ]
        )
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
        return objects
