"""Provides the Social class."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, NameMixin, message


class Social(Base, NameMixin):
    """A social for a player to perform."""

    __tablename__ = 'socials'
    first = message(None)
    second = message(None)
    third = message(None)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref=backref('socials', cascade='all'))
