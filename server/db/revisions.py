"""Provides the Revision class."""

from sqlalchemy import Column, Integer, String, DateTime, func
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base
from .session import Session


@attrs_sqlalchemy
class Revision(Base):
    """Old code."""

    __tablename__ = 'revisions'
    object_id = Column(Integer, nullable=False)
    object_class_name = Column(String(20), nullable=False)
    created = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    code = Column(String(1000000), nullable=False)

    @property
    def object_class(self):
        """Get the actual class that this object refers to."""
        return Base._decl_class_registry[self.object_class_name]

    @property
    def object(self):
        """Get the object this table refers to."""
        return Session.query(self.object_class).get(self.object_id)
