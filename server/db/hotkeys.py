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
    ctrl = Column(Boolean, nullable=True)
    shift = Column(Boolean, nullable=True)
    alt = Column(Boolean, nullable=True)
    reusable = Column(Boolean, nullable=False, default=False)
    objects = relationship(
        'Object', backref='hotkeys', secondary=HotkeySecondary.__table__
    )

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.append(self.make_field('reusable', type=bool))
        for name in ('ctrl', 'shift', 'alt'):
            fields.append(
                self.make_field(
                    name, type={
                        None: 'Either',
                        True: 'Down',
                        False: 'Up'
                    }
                )
            )
        return fields
