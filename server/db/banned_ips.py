"""Provides the BannedIP class."""

from sqlalchemy import Column, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, OwnerMixin


@attrs_sqlalchemy
class BannedIP(Base, OwnerMixin):
    """Used to ban an IP address."""

    __tablename__ = 'banned_ips'
    ip = Column(String(15), nullable=False)
