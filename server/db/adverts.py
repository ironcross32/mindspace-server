"""Provides the Advert class."""

from .base import Base, OwnerMixin, TextMixin, message


class Advert(Base, OwnerMixin, TextMixin):
    """An advertisement."""

    __tablename__ = 'adverts'
    url = message(None, nullable=True)
