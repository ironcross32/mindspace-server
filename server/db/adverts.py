"""Provides the Advert class."""

from sqlalchemy import Column, DateTime
from .base import Base, OwnerMixin, TextMixin, message, CreatedMixin


class Advert(Base, OwnerMixin, TextMixin, CreatedMixin):
    """An advertisement."""

    __tablename__ = 'adverts'
    __owner_cascade__ = 'all'
    url = message(None, nullable=True)
    last_shown = Column(DateTime(timezone=True), nullable=True)
