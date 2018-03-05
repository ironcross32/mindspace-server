"""Provides the Star class."""

from .base import Base, message


class Star(Base):
    """Make a Zone a star."""

    __tablename__ = 'stars'
    type = message('M')
