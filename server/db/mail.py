"""Provides mail-related classes."""

import os.path
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, TextMixin, OwnerMixin, CreatedMixin
from ..sound import get_sound
from ..protocol import interface_sound


class MailMessage(Base, NameMixin, TextMixin, OwnerMixin, CreatedMixin):
    """An out of character mail message."""

    __tablename__ = 'mail_messages'
    read = Column(Boolean, nullable=False, default=False)
    to_id = Column(
        Integer,
        ForeignKey('objects.id'),
        nullable=False
    )
    to = relationship(
        'Object', backref='received_mail', foreign_keys=[to_id]
    )
    parent_id = Column(
        Integer,
        ForeignKey(__tablename__ + '.id'),
        nullable=True
    )
    parent = relationship(
        'MailMessage',
        backref='replies',
        remote_side='MailMessage.id'
    )

    def get_name(self, *args, **kwargs):
        """Get a sensible name."""
        if self.name is None:
            if self.parent is None:
                return '(No Subject)'
            else:
                name = self.parent.get_name(*args, **kwargs)
                prefix = 'RE:'
                if not name.startswith(prefix):
                    name = f'{prefix} {name}'
                return name
        else:
            return super().get_name(*args, **kwargs)

    @classmethod
    def send(cls, sender, to, subject, body):
        """Send a mail to a player."""
        m = cls(owner=sender, to=to, name=subject, text=body)
        if to.is_player and to.player.mail_notifications:
            con = to.get_connection()
            if con is not None:
                interface_sound(
                    con, get_sound(os.path.join('notifications', 'mail.wav'))
                )
        return m
