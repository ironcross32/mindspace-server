"""Provides object types."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin, DescriptionMixin


@attrs_sqlalchemy
class ObjectTypeActionSecondary(Base):
    """Link actions to types."""

    __tablename__ = 'object_types_actions'
    type_id = Column(Integer, ForeignKey('object_types.id'), nullable=False)
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)


@attrs_sqlalchemy
class ObjectTypeHotkeySecondary(Base):
    """Link hotkeys to actions."""

    __tablename__ = 'object_types_hotkeys'
    type_id = Column(Integer, ForeignKey('object_types.id'), nullable=False)
    hotkey_id = Column(Integer, ForeignKey('hotkeys.id'), nullable=False)


@attrs_sqlalchemy
class ObjectTypeSecondary(Base):
    """Link objects to types."""

    __tablename__ = 'object_types_secondary'
    type_id = Column(Integer, ForeignKey('object_types.id'), nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


@attrs_sqlalchemy
class ObjectType(Base, NameMixin, DescriptionMixin):
    """A sort of parent for objects."""

    __tablename__ = 'object_types'
    objects = relationship(
        'Object', backref='types', secondary=ObjectTypeSecondary.__table__
    )
    actions = relationship(
        'Action', backref='types',
        secondary=ObjectTypeActionSecondary.__table__
    )
    hotkeys = relationship(
        'Hotkey', backref='types',
        secondary=ObjectTypeHotkeySecondary.__table__
    )
