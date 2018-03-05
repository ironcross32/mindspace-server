"""Provides the Player class."""

from random import randint
from sqlalchemy import (Column, String, Float, Boolean, Interval, DateTime)
from .base import Base, PermissionsMixin, PasswordMixin
from ..protocol import options


class Player(Base, PermissionsMixin, PasswordMixin):
    """Player options."""

    __tablename__ = 'players'
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
    locked = Column(Boolean, nullable=False, default=False)
    connect_notifications = Column(Boolean, nullable=False, default=True)
    disconnect_notifications = Column(Boolean, nullable=False, default=True)
    mail_notifications = Column(Boolean, nullable=False, default=True)
    idea_notifications = Column(Boolean, nullable=False, default=True)
    changelog_notifications = Column(Boolean, nullable=False, default=True)

    def send_options(self, connection):
        """Send player options over connection."""
        self.transmition_id = randint(0, 5000000)
        return options(connection, self)
