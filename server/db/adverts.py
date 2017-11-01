"""Provides the Advert class."""

from sqlalchemy import Column, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, OwnerMixin
from ..forms import Label


@attrs_sqlalchemy
class Advert(Base, OwnerMixin):
    """An advertisement."""

    __tablename__ = 'adverts'
    text = Column(String(2000), nullable=False)
    url = Column(String(200), nullable=True)

    def get_all_fields(self):
        fields = [Label('Advert')]
        for name in ('text', 'url'):
            fields.append(self.make_field(name))
        return fields