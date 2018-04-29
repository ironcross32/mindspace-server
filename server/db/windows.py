"""Provides the Window class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, message, Sound


class Window(Base):
    """A wiindow to be added to an object."""

    __tablename__ = 'windows'
    open = Column(Boolean, nullable=False, default=False)
    overlooking_id = Column(
        Integer, ForeignKey('rooms.id'), nullable=False,
        default=lambda: Base._decl_class_registry['Room'].first().id
    )
    overlooking = relationship(
        'Room', backref=backref('windows', cascade='all, delete-orphan')
    )
    open_msg = message('%1N open%1s %2n.')
    close_msg = message('%1N close%1s %2n.')
    open_sound = Column(Sound, nullable=True)
    close_sound = Column(Sound, nullable=True)

    @property
    def opened(self):
        """get self.open."""
        return self.open

    @opened.setter
    def opened(self, value):
        """Set self.open."""
        self.open = value
        if self.open:
            self.object.ambience = self.overlooking.ambience
        else:
            self.object.ambience = None
        self.object.update_neighbours()
