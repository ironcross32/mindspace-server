"""Provides the BannedIP class."""

from sqlalchemy import Column, String
from .base import Base, OwnerMixin


class BannedIP(Base, OwnerMixin):
    """Used to ban an IP address."""

    __tablename__ = 'banned_ips'
    ip = Column(String(15), nullable=False)
