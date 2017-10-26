"""Provides the Rule class."""

from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, NameMixin, DescriptionMixin


@attrs_sqlalchemy
class Rule(Base, NameMixin, DescriptionMixin):
    """A rule."""

    __tablename__ = 'rules'
