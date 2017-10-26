"""Provides the Social class."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin
from ..forms import Label


@attrs_sqlalchemy
class Social(Base, NameMixin):
    """A social for a player to perform."""

    __tablename__ = 'socials'
    first = Column(String(200), nullable=False)
    second = Column(String(200), nullable=False)
    third = Column(String(200), nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref='socials')

    def get_all_fields(self):
        fields = [Label('Edit Social')]
        for name in ('name', 'first', 'second', 'third'):
            fields.append(self.make_field(name))
        return fields
