"""Provides the ChangelogEntry class."""

from sqlalchemy import Column, String
from .base import Base, OwnerMixin, CreatedMixin


class ChangelogEntry(Base, OwnerMixin, CreatedMixin):
    """A changelog entry."""

    __tablename__ = 'changelogs'
    text = Column(String(150), nullable=False)
