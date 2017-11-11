"""Provides the LogHandler class."""

from logging import Handler
from attr import attrs, attrib
from .db import Session, CommunicationChannel


@attrs
class PretendObject:
    """A pretend user."""
    name = attrib()
    id = attrib()

    def get_name(self, staff):
        if not staff:
            return self.name
        else:
            return f'{self.name} (#{self.id})'


obj = PretendObject('System', 0)


class LogHandler(Handler):
    """Log messages inside the game."""

    def emit(self, record):
        """Send the record in game."""
        name = record.levelname
        channel = CommunicationChannel.query(name=name, admin=True).first()
        if channel is None:
            channel = CommunicationChannel(
                description=f'Log messages from the {name} category.',
                name=name, admin=True
            )
            Session.add(channel)
            Session.commit()
        channel.transmit(
            obj, f'{record.name}: {record.getMessage()}', strict=False,
            store=False
        )
