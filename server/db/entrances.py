"""Provides the Entrance class."""

from sqlalchemy import Column, Boolean, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
)
from ..sound import get_sound


@attrs_sqlalchemy
class Entrance(
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
):
    """An entrance to another room."""

    __tablename__ = 'entrances'
    no_mobiles = Column(Boolean, nullable=False, default=False)
    leave_msg = Column(
        String(100), nullable=False, default='%1N leave%1s through %2n.'
    )
    arrive_msg = Column(
        String(100), nullable=False, default='%1N arrive%1s from %2n.'
    )
    locked = Column(Boolean, nullable=False, default=False)
    locked_msg = Column(
        String(100), nullable=False,
        default='%1N tr%1y %2n only to find it locked.'
    )
    locked_sound = Column(String(100), nullable=True)
    lockable = Column(Boolean, nullable=False, default=False)
    correct_code_msg = Column(
        String(100), nullable=False, default='%1N fiddle%1s with %2n.'
    )
    correct_code_sound = Column(String(100), nullable=True)
    incorrect_code_msg = Column(
        String(100), nullable=False,
        default='%1N fiddle%1s with %2n which beep%2s loudly.'
    )
    incorrect_code_sound = Column(String(100), nullable=True)
    unlock_msg = Column(
        String(100), nullable=False, default='%1N unlock%1s %2n.'
    )
    unlock_sound = Column(String(100), nullable=True)
    lock_msg = Column(
        String(100), nullable=False, default='%1N lock%1s %2n.'
    )
    lock_sound = Column(String(100), nullable=True)
    chime_msg = Column(
        String(100), nullable=False, default='%1N ring%1s the chime on %2n.'
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
            'leave_msg', 'arrive_msg', 'correct_code_msg',
            'incorrect_code_msg', 'correct_code_sound', 'incorrect_code_sound',
            'lock_msg', 'lock_sound', 'unlock_msg', 'unlock_sound',
            'chime_msg', 'chime_sound', 'locked_msg', 'locked_sound'
        ):
            fields.append(self.make_field(name))
        return fields

    def incorrect_code(self, player):
        """Play incorrect code sound and show incorrect code social."""
        player.do_social(self.incorrect_code_msg, _others=[self])
        if self.incorrect_code_sound is not None:
            sound = get_sound(self.incorrect_code_sound)
            self.object.sound(sound)
