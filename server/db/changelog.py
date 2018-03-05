"""Provides the ChangelogEntry class."""

from .base import Base, OwnerMixin, CreatedMixin, message


class ChangelogEntry(Base, OwnerMixin, CreatedMixin):
    """A changelog entry."""

    __tablename__ = 'changelogs'
    text = message(None)
