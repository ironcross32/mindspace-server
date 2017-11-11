"""Provides the Direction class."""

import logging
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, CoordinatesMixin, NameMixin
from .session import Session


logger = logging.getLogger(__name__)


class Direction(Base, NameMixin, CoordinatesMixin):
    """A direction a player or vehicle can move in."""

    __tablename__ = 'directions'
    opposite_id = Column(
        Integer,
        ForeignKey(f'{__tablename__}.id'),
        nullable=True,  # Undesirable but prevents a chicken and egg situation.
        default=None
    )
    opposite = relationship(
        'Direction',
        backref='opposites',
        remote_side='Direction.id'
    )

    def coordinates_from(self, start):
        """Apply this direction to coordinates start and return the
        destination coordinates."""
        x, y, z = start
        return (
            x + self.x,
            y + self.y,
            z + self.z
        )

    @classmethod
    def create(cls, name, **kwargs):
        d = cls(name=name, **kwargs)
        logger.info('Created %r.', d)
        Session.add(d)
        return d

    @classmethod
    def key_to_name(cls, name):
        """Return a full name from a key. Simply append "and *" depending on
        modifiers."""
        names = {
            'I': 'north',
            'O': 'northeast',
            'L': 'east',
            '.': 'southeast',
            ',': 'south',
            'M': 'southwest',
            'J': 'west',
            'U': 'northwest'
        }
        return names[name]
