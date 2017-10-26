"""Provides the Hotkey class."""

from sqlalchemy import Column, Boolean
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin
)


@attrs_sqlalchemy
class Hotkey(Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin):
    """Respond to a hotkey."""

    __tablename__ = 'hotkeys'
    reusable = Column(Boolean, nullable=False, default=False)

    def get_all_fields(self):
        fields = [
            self.make_field('reusable', type=bool)
        ]
        return super().get_all_fields() + fields
