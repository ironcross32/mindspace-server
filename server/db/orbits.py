"""Provides the Orbit class."""

from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base
from ..distance import au


class Orbit(Base):
    """Set an object orbiting around a point."""

    __tablename__ = 'orbits'
    orbiting_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    orbiting = relationship(
        'Zone', backref='orbiting', foreign_keys=[orbiting_id]
    )
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    zone = relationship(
        'Zone', backref=backref('orbit', uselist=False), foreign_keys=[zone_id]
    )
    distance = Column(Float, nullable=False, default=au)
    offset = Column(Float, nullable=False, default=0.004)
