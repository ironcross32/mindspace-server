"""Provides the ServerOptions class."""

from datetime import timedelta
from sqlalchemy import Column, Integer, Interval, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin
from .session import Session


@attrs_sqlalchemy
class ServerOptions(Base, NameMixin):
    """Server options."""

    __tablename__ = 'server_options'
    instance_id = 1
    connect_msg = Column(
        String(100), nullable=False, default='Welcome to Mindspace.'
    )
    disconnect_msg = Column(String(100), nullable=False, default='Goodbye.')
    interface = Column(String(25), nullable=False, default='0.0.0.0')
    port = Column(Integer, nullable=False, default=6463)
    web_port = Column(Integer, nullable=False, default=6464)
    udp_port = Column(Integer, nullable=False, default=9000)
    dump_interval = Column(Integer, nullable=False, default=3600)
    name_change_interval = Column(
        Interval, nullable=False, default=timedelta(days=30)
    )
    first_room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    first_room = relationship('Room', backref='first_room_options')
    purge_after = Column(Interval, nullable=False, default=timedelta(days=30))
    log_commands = Column(Boolean, nullable=False, default=False)

    @classmethod
    def get(cls):
        return Session.query(cls).get(cls.instance_id)

    @classmethod
    def set(cls, **options):
        """Set options on the current options."""
        instance = cls.get()
        for name, value in options.items():
            setattr(instance, name, value)
        Session.add(instance)
