"""Provides the Credit class."""

from .base import Base, NameMixin, DescriptionMixin


class Credit(Base, NameMixin, DescriptionMixin):
    """Someone who has helped out with the game."""

    __tablename__ = 'credits'
