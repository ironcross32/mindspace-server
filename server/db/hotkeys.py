"""Provides the Hotkey class."""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import (
    Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin, OwnerMixin
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


class RemappedHotkey(Base, OwnerMixin):
    """Key convertions for people who need them."""

    __tablename__ = 'remapped_hotkeys'
    from_key = Column(String(20), nullable=False)
    from_ctrl = Column(Boolean, nullable=False, default=False)
    from_shift = Column(Boolean, nullable=False, default=False)
    from_alt = Column(Boolean, nullable=False, default=False)
    to_key = Column(String(20), nullable=False)
    to_ctrl = Column(Boolean, nullable=False, default=False)
    to_shift = Column(Boolean, nullable=False, default=False)
    to_alt = Column(Boolean, nullable=False, default=False)

    @classmethod
    def from_raw(cls, player, name, modifiers):
        """Return a key that matches the given name and modifiers and is owned
        by player. None is returned if no results are found."""
        kwargs = dict(owner_id=player.id, from_key=name)
        for mod in ('ctrl', 'shift', 'alt'):
            kwargs[f'from_{mod}'] = mod in modifiers
        return cls.query(**kwargs).first()

    def get_modifiers(self, ctrl, shift, alt):
        """Convert boolean values into a list of strings."""
        modifiers = []
        if ctrl:
            modifiers.append('ctrl')
        if shift:
            modifiers.append('shift')
        if alt:
            modifiers.append('alt')
        return modifiers

    @property
    def from_modifiers(self):
        """Return from modifiers as a list of strings."""
        return self.get_modifiers(
            self.from_ctrl, self.from_shift, self.from_alt
        )

    @property
    def to_modifiers(self):
        """Get to modifiers as a list of strings."""
        return self.get_modifiers(self.to_ctrl, self.to_shift, self.to_alt)
