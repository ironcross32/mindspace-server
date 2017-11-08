"""Provides the Window class."""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base


@attrs_sqlalchemy
class Window(Base):
    """A wiindow to be added to an object."""

    __tablename__ = 'windows'
    open = Column(Boolean, nullable=False, default=False)
    overlooking_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    overlooking = relationship('Room', backref='windows')
    open_msg = Column(String(100), nullable=False, default='%1n|normal open%1s %2n.')
    close_msg = Column(
        String(100), nullable=False, default='%1n|normal close%1s %2n.'
    )
    open_sound = Column(String(200), nullable=True)
    close_sound = Column(String(200), nullable=True)

    def get_all_fields(self):
        fields = [
            self.make_field(
                'overlooking_id', type={
                    x.id: x.get_name(
                        True
                    ) for x in self.object.location.zone.rooms
                }
            ),
            self.make_field('opened', type=bool)
        ]
        for name in ('open_msg', 'close_msg', 'open_sound', 'close_sound'):
            fields.append(self.make_field(name))
        return fields

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
