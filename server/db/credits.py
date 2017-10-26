"""Provides the Credit class."""

from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin, DescriptionMixin


@attrs_sqlalchemy
class Credit(Base, NameMixin, DescriptionMixin):
    """Someone who has helped out with the game."""

    __tablename__ = 'credits'
