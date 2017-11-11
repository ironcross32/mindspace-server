"""Provides the LoggedCommand class."""

import sys
from msgpack import loads
from sqlalchemy import Column, String, DateTime, func
from .base import Base, OwnerMixin


class LoggedCommand(Base, OwnerMixin):
    """A logged string from a connection."""

    __tablename__ = 'logged_commands'
    string = Column(String(1000000), nullable=False)
    sent = Column(DateTime(timezone=True), nullable=False, default=func.now())

    def get_data(self):
        return loads(self.string, encoding=sys.getdefaultencoding())
