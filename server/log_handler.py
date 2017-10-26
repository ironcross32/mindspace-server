"""Provides the LogHandler class."""

from logging import Handler
from .db import Session, CommunicationChannel, Player


class LogHandler(Handler):
    """Log messages inside the game."""

    def emit(self, record):
        """Send the record in game."""
        name = record.levelname
        obj = Session.query(Player).filter_by(admin=True).limit(1).first()
        if obj is None:
            return  # No admins yet.
        obj = obj.object
        channel = Session.query(
            CommunicationChannel
        ).filter_by(name=name, admin=True).first()
        if channel is None:
            channel = CommunicationChannel(
                name=name,
                description=f'Log messages from the {name} category.',
                admin=True
            )
            Session.add(channel)
            Session.commit()
        channel.transmit(
            obj, f'{record.name}: {record.getMessage()}', strict=False,
            store=False
        )
