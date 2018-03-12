"""Provides the Command class."""

from .base import Base, NameMixin, CodeMixin, PermissionsMixin


class Command(Base, NameMixin, CodeMixin, PermissionsMixin):
    """Respond to network connections."""

    __tablename__ = 'commands'
