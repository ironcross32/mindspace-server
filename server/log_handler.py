"""Provides the LogHandler class."""

from logging import Handler
from .db import session, CommunicationChannel, ServerOptions


class LogHandler(Handler):
    """Log messages inside the game."""

    def emit(self, record):
        """Send the record in game."""
        name = record.levelname
        with session() as s:
            channel = CommunicationChannel.query(name=name, admin=True).first()
            if channel is None:
                channel = CommunicationChannel(
                    description=f'Log messages from the {name} category.',
                    name=name, admin=True
                )
                s.add(channel)
                s.commit()
            sender = ServerOptions.get().transmit_as
            assert sender is not None
            channel.transmit(
                sender, f'{record.name}: {record.getMessage()}', strict=False
            )
