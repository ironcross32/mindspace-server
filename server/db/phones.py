"""Provides classes related to phones."""

import os.path
from enum import Enum as _Enum
from string import digits
from random_password import random_password
from sqlalchemy import Column, Integer, Float, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, Sound, message, NameMixin, PhoneAddressMixin, PhoneMixin
)
from .server_options import ServerOptions
from ..socials import factory


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
    transmit_msg = message('From %1n, {text}')
    transmit_sound = Column(
        Sound, nullable=False, default=os.path.join('players', 'say.wav')
    )
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
    reject_msg = message('%1n reject%1s the incoming call on %2n.')
    reject_sound = Column(Sound, nullable=True)
    ring_msg = message('The call light on %1N flash%1e.')
    ring_sound = Column(Sound, nullable=True)
    ring_every = Column(Float, nullable=False, default=2.0)
    next_ring = Column(Float, nullable=True)
    muted = Column(Boolean, nullable=False, default=False)
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
            obj.sound(self.invalid_address_sound)
        elif target.state is not PhoneStates.idle:
            player.message(self.engaged_msg)
            obj.sound(self.engaged_sound)
        elif target.is_blocked(address):
            self.call_disconnected()
        else:
            target.state = PhoneStates.ringing
            self.state = PhoneStates.calling
            self.call_to = target
            player.do_social(self.dial_msg, _others=[obj])
            obj.sound(self.dial_sound)

    def call_disconnected(self):
        """Called when the call is disconnected by the other side."""
        obj = self.object
        self.state = PhoneStates.idle
        obj.do_social(self.hangup_other_msg)
        obj.sound(self.hangup_other_sound)

    def disconnect_call(self, player):
        """Called when player disconnects an active phone call."""
        obj = self.object
        self.state = PhoneStates.idle
        player.do_social(self.hangup_msg, _others=[self.object])
        obj.sound(self.hangup_sound)
        if self.call_to is None:
            other = self.call_from
            self.call_from = None
        else:
            other = self.call_to
            self.call_to = None
        other.call_disconnected()

    def reject_call(self, player):
        """Used to reject an incoming call."""
        obj = self.object
        if self.state is not PhoneStates.ringing:
            player.message('This phone is not ringing.')
            return
        self.state = PhoneStates.idle
        player.do_social(self.reject_msg, _others=[obj])
        obj.sound(self.reject_sound)
        self.call_from.call_disconnected()
        self.call_from = None

    def answer_call(self, player):
        """Used when player answers this phone."""
        obj = self.object
        self.state = PhoneStates.connected
        player.do_social(self.answer_msg, _others=[obj])
        obj.sound(self.answer_sound)
        other_phone = self.call_from
        other_phone.state = PhoneStates.connected
        other_obj = other_phone.object
        other_obj.do_social(other_phone.answer_other_msg)
        other_obj.sound(other_phone.answer_other_sound)

    def transmit(self, text):
        """Send a transmition to this phone."""
        obj = self.other_side.object
        obj.do_social(self.transmit_msg, text=text, _channel='phone')
        obj.sound(self.transmit_sound)

    def emote(self, player, string, **kwargs):
        """Emote into this phone."""
        player.do_social(
            f'Putting %2n to %1his mouth, {string}', _others=[self.object],
            **kwargs
        )
        self.transmit(factory.get_strings(string, [player], **kwargs)[-1])

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

    @property
    def other_side(self):
        """Get the phone this phone is connected to if it is on a call."""
        return self.call_to or self.call_from

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
