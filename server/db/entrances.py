"""Provides the Entrance class."""

from sqlalchemy import Column, Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
)
from ..sound import get_sound


class Entrance(
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
):
    """An entrance to another room."""

    __tablename__ = 'entrances'
    transit_route_id = Column(
        Integer, ForeignKey('transit_routes.id'), nullable=True
    )
    transit_route = relationship(
        'TransitRoute', backref=backref('exit', uselist=False)
    )
    no_mobiles = Column(Boolean, nullable=False, default=False)
    cantuse_msg = Column(
        String(100), nullable=False, default='You cannot go that way.'
    )
    follow_msg = Column(
        String(100), nullable=False, default='%1n follow%1s %2n through %3n.'
    )
    leave_msg = Column(
        String(100), nullable=False, default='%1n|normal leave%1s through %2n.'
    )
    arrive_msg = Column(
        String(100), nullable=False, default='%1n|normal arrive%1s from %2n.'
    )
    locked = Column(Boolean, nullable=False, default=False)
    locked_msg = Column(
        String(100), nullable=False,
        default='%1n|normal tr%1y %2n only to find it locked.'
    )
    locked_sound = Column(String(100), nullable=True)
    lockable = Column(Boolean, nullable=False, default=False)
    other_locked_msg = Column(
        String(100), nullable=False,
        default='%1n|normal rattle%1s as someone on the other side tries to '
        'open it.'
    )
    other_locked_sound = Column(String(100), nullable=True)
    enter_code_msg = Column(
        String(100), nullable=False, default='%1n|normal step%1s up to %2n.'
    )
    enter_code_sound = Column(String(100), nullable=True)
    correct_code_msg = Column(
        String(100), nullable=False, default='%1n|normal fiddle%1s with %2n.'
    )
    correct_code_sound = Column(String(100), nullable=True)
    incorrect_code_msg = Column(
        String(100), nullable=False,
        default='%1n|normal fiddle%1s with %2n which beep%2s loudly.'
    )
    incorrect_code_sound = Column(String(100), nullable=True)
    unlock_msg = Column(
        String(100), nullable=False, default='%1n|normal unlock%1s %2n.'
    )
    unlock_sound = Column(String(100), nullable=True)
    lock_msg = Column(
        String(100), nullable=False, default='%1n|normal lock%1s %2n.'
    )
    lock_sound = Column(String(100), nullable=True)
    other_unlock_msg = Column(
        String(100), nullable=False,
        default='%1n|normal %1is unlocked from the other side.'
    )
    other_unlock_sound = Column(String(100), nullable=True)
    other_lock_msg = Column(
        String(100), nullable=False,
        default='%1n|normal %1is locked from the other side.'
    )
    other_lock_sound = Column(String(100), nullable=True)
    chime_msg = Column(
        String(100), nullable=False,
        default='%1n|normal ring%1s the chime on %2n.'
    )
    chime_sound = Column(
        String(100), nullable=False, default='ambiences/doorbell.wav'
    )
    has_chime = Column(Boolean, nullable=False, default=False)

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in ('no_mobiles', 'locked', 'lockable', 'has_chime'):
            fields.append(self.make_field(name, type=bool))
        for name in (
            'leave_msg', 'arrive_msg', 'follow_msg', 'enter_code_msg',
            'enter_code_sound', 'correct_code_msg', 'incorrect_code_msg',
            'correct_code_sound', 'incorrect_code_sound', 'lock_msg',
            'lock_sound', 'unlock_msg', 'unlock_sound', 'other_lock_msg',
            'other_lock_sound', 'other_unlock_msg', 'other_unlock_sound',
            'chime_msg', 'chime_sound', 'locked_msg', 'locked_sound',
            'other_locked_msg', 'other_locked_sound'
        ):
            fields.append(self.make_field(name))
        return fields

    def enter_code(self, player):
        """Play enter code sound and show enter code social."""
        player.do_social(self.enter_code_msg, _others=[self.object])
        if self.enter_code_sound is not None:
            sound = get_sound(self.enter_code_sound)
            self.object.sound(sound)

    def correct_code(self, player):
        """Play correct code sound and show correct code social."""
        player.do_social(self.correct_code_msg, _others=[self.object])
        if self.correct_code_sound is not None:
            sound = get_sound(self.correct_code_sound)
            self.object.sound(sound)

    def incorrect_code(self, player):
        """Play incorrect code sound and show incorrect code social."""
        player.do_social(self.incorrect_code_msg, _others=[self.object])
        if self.incorrect_code_sound is not None:
            sound = get_sound(self.incorrect_code_sound)
            self.object.sound(sound)

    def get_other_side(self):
        cls = self.object.__class__
        return cls.query(
            cls.exit_id.isnot(None), location_id=self.location_id, x=self.x,
            y=self.y, z=self.z
        ).first()
