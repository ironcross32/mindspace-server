"""Provides the StarshipEngine class."""

from sqlalchemy import Column, Float
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin
from ..distance import km


@attrs_sqlalchemy
class StarshipEngine(Base, NameMixin):
    """An engine for a starship."""

    __tablename__ = 'starship_engines'
    max_acceleration = Column(Float, nullable=False, default=km)

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in ('max_acceleration',):
            fields.append(self.make_field(name, type=float))
        return fields
