"""Classes to make trains and the like work."""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, NameMixin, CoordinatesMixin, LocationMixin


class TransitStop(Base, LocationMixin, CoordinatesMixin):
    """A stop on a transit route."""

    __tablename__ = 'transit_stops'
    before_departure = Column(Float, nullable=False, default=10.0)
    after_departure = Column(Float, nullable=False, default=30.0)
    transit_route_id = Column(
        Integer, ForeignKey('transit_routes.id'), nullable=False
    )
    transit_route = relationship(
        'TransitRoute', backref='stops', foreign_keys=[transit_route_id]
    )

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in ('before_departure', 'after_departure'):
            fields.append(self.make_field(name, type=int))
        return fields


class TransitRoute(Base, NameMixin):
    """Holds 0 or more transit stops."""

    __tablename__ = 'transit_routes'
    next_move = Column(Float, nullable=True)
    next_stop_id = Column(
        Integer, ForeignKey('transit_stops.id'), nullable=True
    )
    next_stop = relationship(
        'TransitStop', backref='arriving', foreign_keys=[next_stop_id]
    )
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    room = relationship(
        'Room', backref=backref('transit_route', uselist=False)
    )
