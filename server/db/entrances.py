"""Provides the Entrance class."""

from sqlalchemy import Column, Boolean
from .base import (
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin, Sound,
    message
)


class Entrance(
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
):
    """An entrance to another room."""

    __tablename__ = 'entrances'
    no_mobiles = Column(Boolean, nullable=False, default=False)
    cantuse_msg = message('You cannot go that way.')
    follow_msg = message('%1N follow%1s %2n through %3n.')
    leave_msg = message('%1N leave%1s through %2n.')
    arrive_msg = message('%1N arrive%1s from %2n.')
    locked = Column(Boolean, nullable=False, default=False)
    locked_msg = message('%1N tr%1y %2n only to find it locked.')
    locked_sound = Column(Sound, nullable=True)
    lockable = Column(Boolean, nullable=False, default=False)
    other_locked_msg = message(
        '%1N rattle%1s as someone on the other side tries to open it.'
    )
    other_locked_sound = Column(Sound, nullable=True)
    enter_code_msg = message('%1N step%1s up to %2n.')
    enter_code_sound = Column(Sound, nullable=True)
    correct_code_msg = message('%1N fiddle%1s with %2n.')
    correct_code_sound = Column(Sound, nullable=True)
    incorrect_code_msg = message(
        '%1N fiddle%1s with %2n which beep%2s loudly.'
    )
    incorrect_code_sound = Column(Sound, nullable=True)
    unlock_msg = message('%1N unlock%1s %2n.')
    unlock_sound = Column(Sound, nullable=True)
    lock_msg = message('%1N lock%1s %2n.')
    lock_sound = Column(Sound, nullable=True)
    other_unlock_msg = message('%1N %1is unlocked from the other side.')
    other_unlock_sound = Column(Sound, nullable=True)
    other_lock_msg = message('%1N %1is locked from the other side.')
    other_lock_sound = Column(Sound, nullable=True)
    chime_msg = message('%1N ring%1s the chime on %2n.')
    chime_sound = Column(
        Sound, nullable=False, default='exits/doorbell.wav'
    )
    has_chime = Column(Boolean, nullable=False, default=False)

    def enter_code(self, player):
        """Play enter code sound and show enter code social."""
        player.do_social(self.enter_code_msg, _others=[self.object])
        self.object.sound(self.enter_code_sound)

    def correct_code(self, player):
        """Play correct code sound and show correct code social."""
        player.do_social(self.correct_code_msg, _others=[self.object])
        self.object.sound(self.correct_code_sound)

    def incorrect_code(self, player):
        """Play incorrect code sound and show incorrect code social."""
        player.do_social(self.incorrect_code_msg, _others=[self.object])
        self.object.sound(self.incorrect_code_sound)

    def get_other_side(self):
        cls = self.object.__class__
        return cls.query(
            cls.exit_id.isnot(None), location_id=self.location_id, x=self.x,
            y=self.y, z=self.z
        ).first()
