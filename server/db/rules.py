"""Provides the Rule class."""

from .base import Base, NameMixin, DescriptionMixin


class Rule(Base, NameMixin, DescriptionMixin):
    """A rule."""

    __tablename__ = 'rules'
