"""Provides the Gender class."""

from sqlalchemy import Column, String
from .base import Base, NameMixin


class Gender(Base, NameMixin):
    """
    Genders for objects.

    Standard Pronouns:
    Subjective: he, she, or it.
    Objective: him, her, or it.
    Possessive Adjective: his, her, or its.
    Possessive Noun: his, hers, or its.
    Reflexive: himself, herself, or itself.
    """

    __tablename__ = 'genders'
    subjective = Column(String(10), nullable=False, default='it')
    objective = Column(String(15), nullable=False, default='it')
    possessive_adjective = Column(String(15), nullable=False, default='its')
    possessive_noun = Column(String(15), nullable=False, default='its')
    reflexive = Column(String(15), nullable=False, default='itself')
