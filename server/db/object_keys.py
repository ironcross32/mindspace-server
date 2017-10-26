"""Provides the ObjectKey class."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base


@attrs_sqlalchemy
class ObjectKey(Base):
    """Link keys to object commands."""

    __tablename__ = 'object_keys'
    hotkey_id = Column(Integer, ForeignKey('hotkeys.id'), nullable=False)
    hotkey = relationship('Hotkey', backref=__tablename__)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref='keys')
