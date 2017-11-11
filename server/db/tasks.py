"""Provides the Task class."""

from sqlalchemy import Column, Float, Boolean
from .base import Base, NameMixin, DescriptionMixin, CodeMixin


class Task(Base, NameMixin, DescriptionMixin, CodeMixin):
    """A task to be run every so often."""

    __tablename__ = 'tasks'
    disabled = Column(Boolean, nullable=False, default=False)
    run_interval = Column(Float, nullable=False, default=3600)
    next_run = Column(Float, nullable=True)

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.extend(
            [
                self.make_field('disabled', type=bool),
                self.make_field('run_interval', type=float)
            ]
        )
        return fields
