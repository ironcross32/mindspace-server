"""Provides the ServerOptions class."""

from socket import getfqdn
from datetime import timedelta
from sqlalchemy import Column, Integer, Interval, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, message
from .session import Session


class ServerOptions(Base, NameMixin):
    """Server options."""

    __tablename__ = 'server_options'
    instance_id = 1
    connect_msg = message('Welcome to Mindspace.')
    disconnect_msg = message('Goodbye.')
    interface = message('0.0.0.0')
    http_port = Column(Integer, nullable=False, default=6464)
    websocket_port = Column(Integer, nullable=False, default=6465)
    https_port = Column(Integer, nullable=False, default=6466)
    udp_port = Column(Integer, nullable=False, default=9000)
    name_change_interval = Column(
        Interval, nullable=False, default=timedelta(days=30)
    )
    first_room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    first_room = relationship('Room', backref='first_room_options')
    purge_after = Column(Interval, nullable=False, default=timedelta(days=30))
    mail_from_name = message('Mindspace Webmaster')
    mail_from_address = message(f'webmaster@{getfqdn()}')
    time_difference = Column(
        Interval, nullable=False, default=timedelta(days=2000 * 365)
    )
    max_speak_length = Column(Integer, nullable=False, default=1000000)
    max_phone_address_length = Column(Integer, nullable=False, default=8)
    system_object_id = Column(
        Integer, ForeignKey('objects.id'), nullable=False, default=0
    )
    system_object = relationship('Object', backref='transmit_as_for_options')
    command_error_msg = message(
        'There was an error with your command. The staff have been notified.'
    )

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
