"""Provides the StarshipEngine class."""

from sqlalchemy import Column, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin
from ..distance import km, ly


@attrs_sqlalchemy
class StarshipEngine(Base, NameMixin):
    """An engine for a starship."""

    __tablename__ = 'starship_engines'
    max_acceleration = Column(Float, nullable=False, default=km)

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in ('max_acceleration',):
            fields.append(self.make_field(name, type=float))
        return fields


@attrs_sqlalchemy
class StarshipSensors(Base, NameMixin):
    """A sensor array for starships."""

    __tablename__ = 'starship_sensors'
    distance = Column(Float, nullable=False, default=ly)


@attrs_sqlalchemy
class Starship(Base):
    """Make a Zone a starship."""

    __tablename__ = 'starships'
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

    def get_filters(self):
        """Return a list of everything this array is filtering."""
        filters = []
        for x in dir(self):
            if x.startswith('filter_') and getattr(self, x):
                filters.append(x[7:].title())
        return filters
