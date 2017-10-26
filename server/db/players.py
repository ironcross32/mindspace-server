"""Provides the Player class."""

from random import randint
from passlib.hash import sha256_crypt as crypt
from sqlalchemy import Column, Integer, Float, String, Boolean
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, PermissionsMixin
from ..protocol import options
from ..forms import Label

rounds = 10000


@attrs_sqlalchemy
class Player(Base, PermissionsMixin):
    """Player options."""
    __tablename__ = 'players'
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(80), nullable=True)
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

    @property
    def reset_password(self):
        return ''

    @reset_password.setter
    def reset_password(self, value):
        if value:  # Don't clear passwords.
            self.set_password(value)

    def get_all_fields(self):
        fields = [Label('Account')]
        for name in ('username', 'reset_password'):
            fields.append(self.make_field(name))
        fields.extend(
            [
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

    def check_password(self, secret):
        """Check that secret matches self.password."""
        return self.password is not None and crypt.verify(
            secret, self.password
        )

    def set_password(self, value):
        """Set self.password."""
        self.password = crypt.encrypt(value, rounds=rounds)

    def clear_password(self):
        """Effectively lock the account."""
        self.password = None

    def send_options(self, connection):
        """Send player options over connection."""
        self.transmition_id = randint(0, 5000000)
        return options(connection, self)
