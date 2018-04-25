"""Provides classes related to finances."""

from enum import Enum as _Enum
from sqlalchemy import Column, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, message, Sound, NameMixin, DescriptionMixin, CurrencyMixin,
    PasswordMixin, CreatedMixin
)
from ..util import now


class TransferDirections(_Enum):
    """Possible directions for finantial transfers."""

    debit = 'debit'
    credit = 'credit'


class Currency(Base, NameMixin):
    """A currency. Each currency has a value which is relative to a baseline of
    1.0."""

    __tablename__ = 'currencies'
    value = Column(Float, nullable=False, default=1.0)

    def convert(self, other, value):
        """Convert this currency to other."""
        return (value / self.value) * other.value


class Shop(Base, CurrencyMixin):
    """A shop which can be attached to an object."""

    __tablename__ = 'shops'
    buy_msg = message('%1N buy%1s %2n from %3n.')
    buy_sound = Column(Sound, nullable=True)

    def add_item(self, obj, price):
        """Add an object to this shop with the given price."""
        assert obj.fertile, 'Object %r is not fertile.' % obj
        return ShopItem(shop=self, object=obj, price=price)


class ShopItem(Base):
    """An item for sale in a shop."""

    __tablename__ = 'shop_items'
    shop_id = Column(Integer, ForeignKey('shops.id'), nullable=False)
    shop = relationship('Shop', backref='items')
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref=backref('shops', cascade='all'))
    price = Column(Float, nullable=False, default=1000000.0)


class CreditCardError(Exception):
    """An error occurred with a credit card."""


class CreditCard(Base, CurrencyMixin, PasswordMixin):
    """Make any object a repository of money."""

    __tablename__ = 'credit_cards'
    value = Column(Float, nullable=False, default=0.0)
    insufficient_funds_msg = message(
        'You have insufficient funds for this transfer.'
    )
    incorrect_currency_msg = message('Currency mismatch.')
    correct_password_msg = message('Successful authentication.')
    incorrect_password_msg = message('Authentication failure.')
    incorrect_password_attempts = Column(Integer, nullable=False, default=0)
    max_password_attempts = Column(Integer, nullable=False, default=3)
    locked_msg = message('This card is locked.')

    def authenticate(self, player, password):
        """Authenticate with this card."""
        if self.locked:
            player.message(self.locked_msg)
        elif (
            not password and self.password is None
        ) or self.check_password(password):
            self.incorrect_password_attempts = 0
            player.message(self.correct_password_msg)
            return True
        else:
            self.incorrect_password_attempts += 1
            player.message(self.incorrect_password_msg)
            if self.locked:
                player.message(self.locked_msg)
        return False

    def transfer(self, amount, currency, description):
        """Transfer money to or from this card. If amount is negative then it
        is treated as a debit. If not then the transfer is treated as a
        credit. If currency does not match self.currency or there are
        insufficient funds then CreditCardError will be raised with an
        appropriate message."""
        if self.locked:
            raise CreditCardError(self.locked_msg)
        elif currency is not self.currency:
            raise CreditCardError(self.incorrect_currency_msg)
        elif amount < 0 and abs(amount) > self.value:
            raise CreditCardError(self.insufficient_funds_msg)
        else:
            self.value += amount
            if amount < 0:
                direction = TransferDirections.debit
            else:
                direction = TransferDirections.credit
        self.transfers.append(
            CreditCardTransfer(
                amount=abs(amount), direction=direction,
                description=description
            )
        )

    @property
    def locked(self):
        return self.incorrect_password_attempts >= self.max_password_attempts


class CreditCardTransfer(Base, DescriptionMixin, CreatedMixin):
    """A transfer to or from a credit card."""

    __tablename__ = 'credit_card_transfers'
    amount = Column(Float, nullable=False)
    direction = Column(Enum(TransferDirections), nullable=False)
    card_id = Column(Integer, ForeignKey('credit_cards.id'), nullable=False)
    card = relationship('CreditCard', backref='transfers')

    def as_string(self, verbose=False):
        """Return tis transfer as a string."""
        id = self.id
        direction = self.direction.value.upper()
        value = self.amount
        currency = self.card.currency.get_name(verbose)
        description = self.get_description()
        when = now(self.created).ctime()
        return f'#{id}: {direction} {value} {currency}: {description} [{when}]'
