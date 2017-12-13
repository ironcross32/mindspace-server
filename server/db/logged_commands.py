"""Provides the LoggedCommand class."""

import sys
from msgpack import loads
from sqlalchemy import Column, String
from .base import Base, OwnerMixin, CreatedMixin


class LoggedCommand(Base, OwnerMixin, CreatedMixin):
    """A logged string from a connection."""

    __tablename__ = 'logged_commands'
    string = Column(String(1000000), nullable=False)

    def get_data(self):
        return loads(self.string, encoding=sys.getdefaultencoding())
