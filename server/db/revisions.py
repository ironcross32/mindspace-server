"""Provides the Revision class."""

from sqlalchemy import Column, Integer, String
from .base import Base, CreatedMixin, Code


class Revision(Base, CreatedMixin):
    """Old code."""

    __tablename__ = 'revisions'
    object_id = Column(Integer, nullable=False)
    object_class_name = Column(String(20), nullable=False)
    code = Column(Code, nullable=False)

    @property
    def object_class(self):
        """Get the actual class that this object refers to."""
        return Base._decl_class_registry[self.object_class_name]

    @property
    def object(self):
        """Get the object this table refers to."""
        return self.object_class.get(self.object_id)
