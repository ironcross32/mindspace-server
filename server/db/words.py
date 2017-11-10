"""Provides the Word class."""

from sqlalchemy import Column, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, OwnerMixin


@attrs_sqlalchemy
class Word(Base, OwnerMixin):
    """A word in a user's personal word list."""

    __tablename__ = 'words'
    word = Column(
        String(
            len('pneumonoultramicroscopicsilicovolcanoconiosis'),
            nullable=False
        )
    )
