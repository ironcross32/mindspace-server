"""Classes to make trains and the like work."""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, NameMixin, CoordinatesMixin, LocationMixin


class TransitStop(Base, LocationMixin, CoordinatesMixin):
    """A stop on a transit route."""

    __tablename__ = 'transit_stops'
    before_departure = Column(Float, nullable=False, default=10.0)
    after_departure = Column(Float, nullable=False, default=30.0)
    transit_id = Column(Integer, ForeignKey('transits.id'), nullable=False)
    transit = relationship('Transit', backref='stops')


class Transit(Base, NameMixin):
    """Holds 0 or more transit stops."""

    __tablename__ = 'transits'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref=backref('transit', uselist=False))
