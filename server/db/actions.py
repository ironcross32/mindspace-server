"""Provides the Action class."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin
)


@attrs_sqlalchemy
class ObjectAction(Base):
    """Link objects to actions."""

    __tablename__ = 'object_actions'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)


@attrs_sqlalchemy
class Action(Base, NameMixin, DescriptionMixin, CodeMixin, PermissionsMixin):
    """A custom action for an object."""

    __tablename__ = 'actions'
    objects = relationship(
        'Object', backref=__tablename__, secondary=ObjectAction.__table__
    )