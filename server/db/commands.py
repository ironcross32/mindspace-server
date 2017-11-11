"""Provides the Command class."""

from .base import Base, NameMixin, CodeMixin


class Command(Base, NameMixin, CodeMixin):
    """Respond to network connections."""

    __tablename__ = 'commands'
