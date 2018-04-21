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
from ..sound import get_sound


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
    invalid_address_msg = message('Invalid address.')
    invalid_address_sound = Column(Sound, nullable=True)
    engaged_msg = message('The phone you are trying to reach is engaged.')
    engaged_sound = Column(Sound, nullable=True)
    dial_msg = message('%1N make%1s a call on %2n.')
    dial_sound = Column(Sound, nullable=True)
    hangup_msg = message('%1N disconnect%1s %2n.')
    hangup_sound = Column(Sound, nullable=True)
    hangup_other_msg = message('%1N show%1s "Call disconnected".')
    hangup_other_sound = Column(Sound, nullable=True)
    answer_msg = message('%1N answer%1s %2n.')
    answer_sound = Column(Sound, nullable=True)
    answer_other_msg = message('%1N show%1s "Call connected".')
    answer_other_sound = Column(Sound, nullable=True)
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

    def call(self, address, player):
        """Initiate a call using this phone."""
        obj = self.object
        target = self.__class__.by_address(address)
        if target is None:
            player.message(self.invalid_address_msg)
            if self.invalid_address_sound is not None:
                obj.sound(get_sound(self.invalid_address_sound))
        elif target.state is not PhoneStates.idle:
            player.message(self.engaged_msg)
            if self.engaged_sound is not None:
                obj.sound(self.engaged_sound)
        elif target.is_blocked(address):
            self.call_disconnected()
        else:
            target.state = PhoneStates.ringing
            self.state = PhoneStates.calling
            self.call_to = target

    def call_disconnected(self):
        """Called when the call is disconnected by the other side."""
        obj = self.object
        self.state = PhoneStates.idle
        obj.do_social(self.hangup_other_msg)
        if self.hangup_other_sound is not None:
            obj.sound(get_sound(self.hangup_other_sound))

    def disconnect_call(self, player):
        """Called when player disconnects an active phone call."""
        obj = self.object
        self.state = PhoneStates.idle
        self.call_to.call_disconnected()
        self.call_to_id = None
        player.do_social(self.hangup_msg, _others=[self])
        if self.hangup_sound is not None:
            obj.sound(get_sound(self.hangup_sound))

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

    def is_blocked(self, address):
        """Returns True if the given address is blocked by this phone."""
        return BlockedPhoneAddress(
            phone_id=self.id, address=address
        ).count()

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
