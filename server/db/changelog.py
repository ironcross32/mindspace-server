"""Provides the ChangelogEntry class."""

from sqlalchemy import Column, String, DateTime, func
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, OwnerMixin


@attrs_sqlalchemy
class ChangelogEntry(Base, OwnerMixin):
    """A changelog entry."""

    __tablename__ = 'changelogs'
    text = Column(String(150), nullable=False)
    posted = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )
