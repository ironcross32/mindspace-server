"""Classes to make trains and the like work."""

from sqlalchemy import Column, Integer, Float, ForeignKey, String
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

    def total_time(self):
        """The total time taken up by this stop."""
        return sum([self.before_departure, self.after_departure])


class TransitRoute(Base, NameMixin, CoordinatesMixin):
    """Holds 0 or more transit stops."""

    __tablename__ = 'transit_routes'
    cant_peer_msg = Column(
        String(100), nullable=False,
        default="You can't see anything during transit."
    )
    board_msg = Column(
        String(100), nullable=False, default='%1n board%1s %2n.'
    )
    board_follow_msg = Column(
        String(100), nullable=False, default='%1n|normal follow%1s %2n.'
    )
    board_sound = Column(String(100), nullable=True)
    board_other_msg = Column(
        String(100), nullable=False, default='{} arrives.'
    )
    board_other_sound = Column(String(100), nullable=True)
    leave_msg = Column(
        String(100), nullable=False, default='%1n disembark%1s from %2n.'
    )
    leave_follow_msg = Column(
        String(100), nullable=False, default='%1n|normal follow%1s %2n.'
    )
    leave_sound = Column(String(100), nullable=True)
    leave_other_msg = Column(
        String(100), nullable=False, default='{} disembarks.'
    )
    leave_other_sound = Column(String(100), nullable=True)
    arrive_msg = Column(
        String(100), nullable=False, default='%1n arrive%1s abruptly.'
    )
    arrive_sound = Column(String(100), nullable=True)
    arrive_other_msg = Column(
        String(100), nullable=False,
        default='Now arriving into {}. Our next stop will be {} in '
        'approximately {}.'
    )
    arrive_other_sound = Column(String(100), nullable=True)
    depart_msg = Column(
        String(100), nullable=False, default='%1n depart%1s.'
    )
    depart_sound = Column(String(100), nullable=True)
    depart_other_msg = Column(
        String(100), nullable=False,
        default='Now departing {}. Our next stop will be {} in approximately '
        '{}.'
    )
    depart_other_sound = Column(String(100), nullable=True)
    cant_leave_msg = Column(
        String(100), nullable=False,
        default='%1n|normal tr%1y %2n only to find it locked during transit.'
    )
    cant_leave_sound = Column(String(100), nullable=True)
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

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in dir(self):
            if name.endswith('_msg') or name.endswith('_sound'):
                fields.append(self.make_field(name))
        return fields
