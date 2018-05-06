"""Provides the MapMarker class."""

from .base import Base, NameMixin, CoordinatesMixin, LocationMixin, OwnerMixin


class MapMarker(Base, NameMixin, CoordinatesMixin, LocationMixin, OwnerMixin):
    """Mark a position in a room."""

    __tablename__ = 'map_markers'
