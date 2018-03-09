"""Provides classes related to finances."""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, message, Sound, NameMixin, CurrencyMixin


class Currency(Base, NameMixin):
    """A currency. Each currency has a value which is relative to a baseline of
    1.0."""

    __tablename__ = 'currencies'
    value = Column(Float, nullable=False, default=1.0)


class Shop(Base, CurrencyMixin):
    """A shop which can be attached to an object."""

    __tablename__ = 'shops'
    buy_msg = message('%1n|normal buy%1s %2n from %3n.')
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
