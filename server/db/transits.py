"""Classes to make trains and the like work."""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, NameMixin, CoordinatesMixin, LocationMixin, PauseMixin, BoardMixin,
    LeaveMixin, message, Sound
)


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

    def total_time(self):
        """The total time taken up by this stop."""
        return sum([self.before_departure, self.after_departure])


class TransitRoute(
    Base, NameMixin, CoordinatesMixin, PauseMixin, BoardMixin, LeaveMixin
):
    """Holds 0 or more transit stops."""

    __tablename__ = 'transit_routes'
    cant_peer_msg = message("You can't see anything during transit.")
    arrive_msg = message('%1N arrive%1s abruptly.')
    arrive_sound = Column(Sound, nullable=True)
    arrive_other_msg = message(
        'Now arriving into {}. Our next stop will be {} in approximately {}.'
    )
    arrive_other_sound = Column(Sound, nullable=True)
    depart_msg = message('%1N depart%1s.')
    depart_sound = Column(Sound, nullable=True)
    depart_other_msg = message(
        'Now departing {}. Our next stop will be {} in approximately {}.'
    )
    depart_other_sound = Column(Sound, nullable=True)
    cant_leave_msg = message(
        '%1N tr%1y %2n only to find it locked during transit.'
    )
    cant_leave_sound = Column(Sound, nullable=True)
    next_move = Column(Float, nullable=True)
    next_stop_id = Column(
        Integer, ForeignKey('transit_stops.id'), nullable=True
    )
    next_stop = relationship(
        'TransitStop', backref='arriving', foreign_keys=[next_stop_id]
    )
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    room = relationship(
        'Room', backref=backref('transit_route', uselist=False)
    )
