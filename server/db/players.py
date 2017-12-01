"""Provides the Player class."""

from random import randint
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, Interval, DateTime
)
from .base import Base, PermissionsMixin, PasswordMixin
from ..protocol import options
from ..forms import Label


class Player(Base, PermissionsMixin, PasswordMixin):
    """Player options."""

    __tablename__ = 'players'
    connected_time = Column(Interval, nullable=True)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    last_host = Column(String(15), nullable=True)
    last_disconnected = Column(DateTime(timezone=True), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    transmition_id = Column(Integer, nullable=True)
    transmition_banned = Column(Boolean, nullable=True, default=False)
    recording_threshold = Column(Integer, nullable=False, default=20)
    sound_volume = Column(Float, nullable=False, default=1.0)
    ambience_volume = Column(Float, nullable=False, default=0.2)
    music_volume = Column(Float, nullable=False, default=1.0)
    mic_muted = Column(Boolean, nullable=False, default=True)
    locked = Column(Boolean, nullable=False, default=False)
    connect_notifications = Column(Boolean, nullable=False, default=True)
    disconnect_notifications = Column(Boolean, nullable=False, default=True)
    mail_notifications = Column(Boolean, nullable=False, default=True)
    idea_notifications = Column(Boolean, nullable=False, default=True)

    def get_all_fields(self):
        fields = [
            Label('Account'),
            self.make_field('username')
        ]
        fields.extend(
            [
                *PasswordMixin.get_fields(self),
                Label('Voice Transmitions'),
                self.make_field('transmition_banned', type=bool),
                self.make_field('recording_threshold', type=int),
                Label('Sound')
            ]
        )
        for name in ('sound', 'ambience', 'music'):
            fields.append(self.make_field(f'{name}_volume', type=float))
        fields.append(Label('Admin'))
        for name in (
            'builder', 'admin', 'locked', 'connect_notifications',
            'disconnect_notifications', 'mail_notifications',
            'idea_notifications'
        ):
            fields.append(self.make_field(name, type=bool))
        return fields

    def send_options(self, connection):
        """Send player options over connection."""
        self.transmition_id = randint(0, 5000000)
        return options(connection, self)
