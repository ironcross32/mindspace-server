"""Provides the Hotkey class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin
)


@attrs_sqlalchemy
class HotkeySecondary(Base):
    """Link keys to object commands."""

    __tablename__ = 'hotkeys_secondary'
    hotkey_id = Column(Integer, ForeignKey('hotkeys.id'), nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


@attrs_sqlalchemy
class Hotkey(Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin):
    """Respond to a hotkey."""

    __tablename__ = 'hotkeys'
    reusable = Column(Boolean, nullable=False, default=False)
    objects = relationship(
        'Object', backref='hotkeys', secondary=HotkeySecondary.__table__
    )

    def get_all_fields(self):
        fields = [
            self.make_field('reusable', type=bool)
        ]
        return super().get_all_fields() + fields
