"""Provides the Word class."""

from sqlalchemy import Column, String
from .base import Base, OwnerMixin


class Word(Base, OwnerMixin):
    """A word in a user's personal word list."""

    __tablename__ = 'words'
    word = Column(
        String(
            len('pneumonoultramicroscopicsilicovolcanoconiosis')
        ), nullable=False
    )
