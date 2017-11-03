"""Provides the Star class."""

from sqlalchemy import Column, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base


@attrs_sqlalchemy
class Star(Base):
    """Make a Zone a star."""

    __tablename__ = 'stars'
    type = Column(String(1), nullable=False, default='M')
