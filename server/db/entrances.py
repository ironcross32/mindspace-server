"""Provides the Entrance class."""

from sqlalchemy import Column, Boolean, String
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
)


@attrs_sqlalchemy
class Entrance(
    Base, CoordinatesMixin, AmbienceMixin, LocationMixin, PasswordMixin
):
    """An entrance to another room."""

    __tablename__ = 'entrances'
    no_mobiles = Column(Boolean, nullable=False, default=False)
    leave_msg = Column(
        String(100), nullable=False, default='%1N leave%1s through %2n.'
    )
    arrive_msg = Column(
        String(100), nullable=False, default='%1N arrive%1s from %2n.'
    )
    locked = Column(Boolean, nullable=False, default=False)
    code_msg = Column(
        String(100), nullable=False, default='%1N fiddle%1s with %2n.'
    )
    code_sound = Column(String(100), nullable=True)
    unlock_msg = Column(
        String(100), nullable=False, default='%1N unlock%1s %2n.'
    )
    unlock_sound = Column(String(100), nullable=True)
    lock_msg = Column(
        String(100), nullable=False, default='%1N lock%1s %2n.'
    )
    lock_sound = Column(String(100), nullable=True)

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.append(self.make_field('no_mobiles', type=bool))
        for name in ('leave_msg', 'arrive_msg'):
            fields.append(self.make_field(name))
        return fields
