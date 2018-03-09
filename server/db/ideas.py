"""Provides classes relating to ideas."""

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from .base import Base, NameMixin, OwnerMixin, CreatedMixin


class IdeaVote(Base):
    """A vote for an idea."""

    __tablename__ = 'idea_votes'
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    voter_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


class Idea(Base, NameMixin, OwnerMixin, CreatedMixin):
    """An idea."""

    __tablename__ = 'ideas'
    __owner_cascade__ = 'all'
    body = Column(String(10000), nullable=False)
    votes = relationship(
        'Object', secondary=IdeaVote.__table__, backref='idea_votes',
        cascade='all'
    )


class IdeaComment(Base, OwnerMixin, CreatedMixin):
    """A comment on an idea."""

    __tablename__ = 'idea_comments'
    __owner_cascade__ = 'all'
    text = Column(String(10000), nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    idea = relationship('Idea', backref=backref('comments', cascade='all'))
