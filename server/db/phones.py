"""Provides classes related to phones."""

from enum import Enum as _Enum
from string import digits
from random_password import random_password
from sqlalchemy import Column, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, Sound, message, NameMixin, PhoneAddressMixin, PhoneMixin
)
from .server_options import ServerOptions


class PhoneStates(_Enum):
    """The possible states for phones."""

    idle = 0
    calling = 1
    ringing = 2
    connected = 3


class BlockedPhoneAddress(Base, PhoneAddressMixin, PhoneMixin):
    """A number which has been blocked by a particular phone."""

    __tablename__ = 'blocked_phone_addresses'


class PhoneContact(Base, NameMixin, PhoneAddressMixin, PhoneMixin):
    """An entry in a phone directory."""

    __tablename__ = 'phone_contacts'


class Phone(Base, PhoneAddressMixin):
    """Make an object a phone."""

    __tablename__ = 'phones'
    dial_msg = message('%1N make%1s a call on %2n.')
    dial_sound = Column(Sound, nullable=True)
    hangup_msg = message('%1N disconnect%1s %2n.')
    hangup_sound = Column(Sound, nullable=True)
    answer_msg = message('%1N answer%1s %2n.')
    answer_sound = Column(Sound, nullable=True)
    ring_msg = message('The call light on %1N flash%1e.')
    ring_sound = Column(Sound, nullable=True)
    ring_every = Column(Float, nullable=False, default=2.0)
    next_ring = Column(Float, nullable=True)
    state = Column(Enum(PhoneStates), nullable=False, default=PhoneStates.idle)
    call_to_id = Column(Integer, ForeignKey('phones.id'), nullable=True)
    call_to = relationship(
        'Phone', backref=backref('call_from', uselist=False),
        remote_side='Phone.id'
    )

    def set_address(self):
        """Set this address to a random and unique address."""
        self.address = self.unique_address()

    def add_contact(self, name, address):
        """Add a contact to this phone's contacts list."""
        self.phone_contacts.append(PhoneContact(name=name, address=address))

    def block_address(self, address):
        """Add an address to this phone's blocked list."""
        self.blocked_phone_addresses.append(
            BlockedPhoneAddress(address=address)
        )

    @classmethod
    def random_address(cls):
        """Generate a random (but possibly not unique) address."""
        return random_password(
            length=ServerOptions.get().max_phone_address_length,
            characters=digits
        )

    @classmethod
    def address_is_unique(cls, address):
        """Check the given address is unique."""
        return not cls.query(address=address).count()

    @classmethod
    def unique_address(cls):
        """Generate a random and unique address."""
        while True:
            address = cls.random_address()
            if cls.address_is_unique(address):
                return address

    @classmethod
    def by_address(cls, address):
        """Get a phone by it's unique address."""
        return cls.query(address=address).first()
