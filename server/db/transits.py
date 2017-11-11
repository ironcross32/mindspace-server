"""Classes to make trains and the like work."""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, CoordinatesMixin, LocationMixin


class TransitStop(Base, LocationMixin, CoordinatesMixin):
    """A stop on a transit route."""

    __tablename__ = 'transit_stops'
    before_departure = Column(Float, nullable=False, default=10.0)
    after_departure = Column(Float, nullable=False, default=30.0)
    transit_route_id = Column(
        Integer, ForeignKey('transit_routes.id'), nullable=False
    )
    transit_route = relationship('TransitRoute', backref='stops')


class TransitRoute(Base, NameMixin):
    """Holds 0 or more transit stops."""

    __tablename__ = 'transit_routes'
