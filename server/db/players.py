"""Provides the Player class."""

from sqlalchemy import (Column, String, Float, Boolean, Interval, DateTime)
from .base import Base, PermissionsMixin, PasswordMixin, LockedMixin
from ..protocol import options


class Player(Base, PermissionsMixin, PasswordMixin, LockedMixin):
    """Player options."""

    __tablename__ = 'players'
    help_mode = Column(Boolean, nullable=False, default=False)
    donator = Column(Boolean, nullable=False, default=False)
    connected_time = Column(Interval, nullable=True)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    last_host = Column(String(15), nullable=True)
    last_disconnected = Column(DateTime(timezone=True), nullable=True)
    email = Column(String(150), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    sound_volume = Column(Float, nullable=False, default=1.0)
    ambience_volume = Column(Float, nullable=False, default=0.2)
    music_volume = Column(Float, nullable=False, default=1.0)
    connect_notifications = Column(Boolean, nullable=False, default=True)
    disconnect_notifications = Column(Boolean, nullable=False, default=True)
    mail_notifications = Column(Boolean, nullable=False, default=True)
    idea_notifications = Column(Boolean, nullable=False, default=True)
    changelog_notifications = Column(Boolean, nullable=False, default=True)

    def send_options(self, connection):
        """Send player options over connection."""
        return options(connection, self)
