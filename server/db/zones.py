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
from .starship_engines import StarshipEngine
from ..forms import Label
from ..protocol import zone
from ..sound import sounds_dir


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
    starship_engine_id = Column(
        Integer, ForeignKey('starship_engines.id'), nullable=True
    )
    starship_engine = relationship(
        'StarshipEngine', backref=backref('object', uselist=False)
    )
    last_turn = Column(Float, nullable=False, default=0.0)
    background_sound = Column(String(150), nullable=True)
    background_rate = Column(Float, nullable=False, default=1.0)
    background_volume = Column(Float, nullable=False, default=1.0)
    speed = Column(Float, nullable=True)

    def get_all_fields(self):
        d = {None: 'None'}
        for engine in StarshipEngine.query():
            d[engine.id] = engine.name
        fields = [Label(f'Configure {self.get_name(True)}')]
        fields.extend(NameMixin.get_fields(self))
        fields.extend(DescriptionMixin.get_fields(self))
        fields.extend(DirectionMixin.get_fields(self))
        fields.append(self.make_field('starship_engine_id', type=d))
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
