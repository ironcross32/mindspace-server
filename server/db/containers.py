"""Provides the Container class."""

from sqlalchemy import Column, Integer
from .base import Base, message, Sound
from ..sound import get_sound


class Container(Base):
    """Make objects contain stuff."""

    __tablename__ = 'containers'
    max_contents = Column(Integer, nullable=False, default=0)
    no_room_msg = message('There is not more room in there.')
    store_msg = message('%1n|normal put%1s %2n in %3n.')
    store_sound = Column(Sound, nullable=True)
    retrieve_msg = message('%1n|normal retrieve%1s %2n from %3n.')
    retrieve_sound = Column(Sound, nullable=True)

    def store(self, player, thing):
        """Store thing inside this object as player."""
        if self.max_contents and len(self.contents) >= self.max_contents:
            return player.message(self.no_room_msg)
        thing.location = None
        thing.holder = None
        self.contents.append(thing)
        player.do_social(self.store_msg, _others=[thing, self.object])
        if self.store_sound is not None:
            player.sound(get_sound(self.store_sound))

    def retrieve(self, player, thing):
        """Move thing from this object to player."""
        self.contents.remove(thing)
        player.holding.append(thing)
        player.do_social(self.retrieve_msg, _others=[thing, self.object])
        if self.retrieve_sound is not None:
            player.sound(get_sound(self.retrieve_sound))
