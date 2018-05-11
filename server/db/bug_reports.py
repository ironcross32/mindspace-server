"""Provides the Report class."""

from sqlalchemy import Column, Boolean
from .base import (
    Base, OwnerMixin, LocationMixin, CoordinatesMixin, Text, CreatedMixin
)


class BugReport(
    Base, OwnerMixin, LocationMixin, CoordinatesMixin, CreatedMixin
):
    """A bug report."""

    __tablename__ = 'bug_reports'
    read = Column(Boolean, nullable=False, default=False)
    text = Column(Text, nullable=False)
