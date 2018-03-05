"""Provides the Hotkey class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import (
    Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin
)


class HotkeySecondary(Base):
    """Link keys to object commands."""

    __tablename__ = 'hotkeys_secondary'
    hotkey_id = Column(Integer, ForeignKey('hotkeys.id'), nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


class Hotkey(Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin):
    """Respond to a hotkey."""

    __tablename__ = 'hotkeys'
    ctrl = Column(Boolean, nullable=True)
    shift = Column(Boolean, nullable=True)
    alt = Column(Boolean, nullable=True)
    reusable = Column(Boolean, nullable=False, default=False)
    objects = relationship(
        'Object', backref='hotkeys', secondary=HotkeySecondary.__table__
    )
