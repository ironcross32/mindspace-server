"""Provides the Chair class."""

from sqlalchemy import Column, Integer, Boolean
from .base import Base, message, Sound
from .objects import RestingStates
from ..sound import get_sound


class Chair(Base):
    """Make an object sittable."""

    __tablename__ = 'chairs'
    max_occupants = Column(Integer, nullable=False, default=0)
    sit_msg = message('%1n|normal sit%1s on %2n.')
    sit_sound = Column(Sound, nullable=False, default='chairs/sit.wav')
    lie_msg = message('%1n|normal lie%1s on %2n.')
    lie_sound = Column(Sound, nullable=False, default='chairs/sit.wav')
    stand_msg = message('%1n|normal get%1s up from %2n.')
    stand_sound = Column(Sound, nullable=False, default='chairs/stand.wav')
    sitting_msg = message('is sitting on {}')
    lying_msg = message('is lying on {}')
    no_room_msg = message('There is no more room on that.')
    no_sit_msg = message('You cannot sit on that.')
    no_lie_msg = message('You cannot lie on that.')
    can_sit = Column(Boolean, nullable=False, default=True)
    can_lie = Column(Boolean, nullable=False, default=True)

    def use(self, player, state):
        """Have the provided player sit or lie on this chair. State must be one
        of the members of RestingStates."""
        assert state in RestingStates
        if state is RestingStates.standing:
            action = 'stand'
        else:
            # The player wants to sit or lie or something.
            if player.resting_state is not RestingStates.standing:
                return player.message('You must be standing first.')
            elif self.max_occupants and len(
                self.occupants
            ) > self.max_occupants:
                return player.message(self.no_room_msg)
            else:
                if state is RestingStates.sitting:
                    if not self.can_sit:
                        return player.message(self.no_sit_msg)
                    action = 'sit'
                elif state is RestingStates.lying:
                    if not self.can_lie:
                        return player.message(self.no_lie_msg)
                    action = 'lie'
                else:
                    raise ValueError(f"Can't process state {repr(state)}.")
        if state is RestingStates.standing:
            self.occupants.remove(player)
        else:
            self.occupants.append(player)
        social = getattr(self, f'{action}_msg')
        sound = getattr(self, f'{action}_sound')
        player.do_social(social, _others=[self.object])
        player.sound(get_sound(sound))
        player.resting_state = state
