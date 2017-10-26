"""Provides the Command class."""

from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin, CodeMixin


@attrs_sqlalchemy
class Command(Base, NameMixin, CodeMixin):
    """Respond to network connections."""

    __tablename__ = 'commands'
