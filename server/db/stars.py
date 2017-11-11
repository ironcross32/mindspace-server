"""Provides the Star class."""

from sqlalchemy import Column, String
from .base import Base


class Star(Base):
    """Make a Zone a star."""

    __tablename__ = 'stars'
    type = Column(String(1), nullable=False, default='M')
