"""Provides the BannedIP class."""

from .base import Base, OwnerMixin, message


class BannedIP(Base, OwnerMixin):
    """Used to ban an IP address."""

    __tablename__ = 'banned_ips'
    ip = message('123.456.789.012')
