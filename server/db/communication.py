"""Provides classes to do with communication channels."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, NameMixin, DescriptionMixin, OwnerMixin, CommunicationChannelMixin,
    PermissionsMixin, CreatedMixin, TextMixin, Sound, message
)
from .session import Session as s
from ..sound import get_sound
from ..socials import factory


class TransmitionError(Exception):
    """There was an error transmitting."""


class CommunicationChannelListener(Base, CommunicationChannelMixin):
    """Connects objects to channels."""

    __tablename__ = 'communication_channel_listeners'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    channel_id = Column(
        Integer, ForeignKey('communication_channels.id'), nullable=False
        )


class CommunicationChannelBan(Base, CommunicationChannelMixin):
    """Ban someone from a channel."""

    __tablename__ = 'communication_channel_ban'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


class CommunicationChannel(
    Base, NameMixin, DescriptionMixin, PermissionsMixin
):
    """A communications channel."""

    __tablename__ = 'communication_channels'
    transmit_format = message('[{channel_name}] %1N transmit%1s: "{message}"')
    transmit_sound = Column(Sound, nullable=True)
    listeners = relationship(
        'Object', secondary=CommunicationChannelListener.__table__,
        backref='communication_channels'
    )
    banned = relationship(
        'Object', secondary=CommunicationChannelBan.__table__,
        backref='banned_channels'
    )

    def transmit(self, who, message, format=None, strict=True):
        """Send a message on this channel. If strict then perform permission
        checks."""
        if strict:
            if who in self.banned:
                raise TransmitionError(
                    'You have been banned from this channel.'
                )
            if self.builder and not who.is_builder:
                raise TransmitionError(
                    'Only builders can transmit on this channel.'
                )
            if self.admin and not who.is_admin:
                raise TransmitionError(
                    'Only administrators can transmit on this channel.'
                )
        if format is None:
            format = self.transmit_format
        m = CommunicationChannelMessage(
            channel=self, owner=who, text=message
        )
        s.add(m)
        strings = factory.get_strings(
            format, [who], channel_name=self.name, message=m.text
        )
        first, second = strings
        if self.transmit_sound is None:
            sound = None
        else:
            sound = get_sound(self.transmit_sound)
        for l in self.listeners:
            if l is who:
                string = first
            else:
                string = second
            l.message(string, channel=self.name)
            if sound is not None:
                l.sound(sound, private=True)
        return m


class CommunicationChannelMessage(
    Base, OwnerMixin, CommunicationChannelMixin, CreatedMixin, TextMixin
):
    """A message to a channel."""

    __tablename__ = 'communication_channel_messages'
    channel = relationship(
        'CommunicationChannel',
        backref=backref('messages', cascade='all, delete-orphan')
    )
