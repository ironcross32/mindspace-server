"""Provides classes to do with communication channels."""

import os.path
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from attr import attrs, attrib, Factory
from .base import (
    Base, NameMixin, DescriptionMixin, OwnerMixin, CommunicationChannelMixin,
    PermissionsMixin
)
from ..sound import get_sound, sounds_dir


@attrs
class UnstoredCommunicationChannelMessage:
    """A pretend channel message."""

    channel = attrib(default=Factory(lambda: None))
    text = attrib(default=Factory(lambda: None))
    owner = attrib(default=Factory(lambda: None))


class TransmitionError(Exception):
    """There was an error transmitting."""


@attrs_sqlalchemy
class CommunicationChannelListener(Base, CommunicationChannelMixin):
    """Connects objects to channels."""

    __tablename__ = 'communication_channel_listeners'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    channel_id = Column(
        Integer, ForeignKey('communication_channels.id'), nullable=False
        )


@attrs_sqlalchemy
class CommunicationChannelBan(Base, CommunicationChannelMixin):
    """Ban someone from a channel."""

    __tablename__ = 'communication_channel_ban'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


@attrs_sqlalchemy
class CommunicationChannel(
    Base, NameMixin, DescriptionMixin, PermissionsMixin
):
    """A communications channel."""

    __tablename__ = 'communication_channels'
    listeners = relationship(
        'Object', secondary=CommunicationChannelListener.__table__,
        backref='communication_channels'
    )
    banned = relationship(
        'Object', secondary=CommunicationChannelBan.__table__,
        backref='banned_channels'
    )

    def transmit(
        self, who, message, format='{} transmits: "{}"', strict=True,
        store=True
    ):
        """Send a message on this channel. If strict then perform permission
        checks."""
        if strict:
            if who in self.banned:
                raise TransmitionError(
                    'You have been banned from this channel.'
                )
            if self.builder and not who.is_builder:
                raise TransmitionError(
                    'Only builders can transmit on tis channel.'
                )
            if self.admin and not who.is_admin:
                raise TransmitionError(
                    'Only administrators can transmit on tis channel.'
                )
        if store:
            cls = CommunicationChannelMessage
        else:
            cls = UnstoredCommunicationChannelMessage
        m = cls(
            channel=self, owner=who, text=message
        )
        path = os.path.join(
            sounds_dir, 'communication', f'{self.name.lower()}.wav'
        )
        if os.path.isfile(path):
            sound = get_sound(path)
        else:
            sound = None
        for l in self.listeners:
            l.message(
                format.format(
                    m.owner.get_name(l.is_builder or l.is_admin),
                    m.text
                ),
                channel=self.name
            )
            if sound:
                l.sound(sound, private=True)
        if m in self.messages and not store:
            self.messages.remove(m)
        return m


@attrs_sqlalchemy
class CommunicationChannelMessage(Base, OwnerMixin, CommunicationChannelMixin):
    """A message to a channel."""

    __tablename__ = 'communication_channel_messages'
    text = Column(String(10000), nullable=False)
    sent = Column(DateTime(timezone=True), nullable=False, default=func.now())
    channel = relationship('CommunicationChannel', backref='messages')
