"""Provides the Task class."""

from sqlalchemy import Column, Float
from .base import Base, NameMixin, DescriptionMixin, CodeMixin, PauseMixin


class Task(Base, NameMixin, DescriptionMixin, CodeMixin, PauseMixin):
    """A task to be run every so often."""

    __tablename__ = 'tasks'
    interval = Column(Float, nullable=False, default=3600)
    next_run = Column(Float, nullable=True)
