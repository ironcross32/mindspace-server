"""Provides classes relating to ideas."""

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, OwnerMixin


class IdeaVote(Base):
    """A vote for an idea."""

    __tablename__ = 'idea_votes'
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    voter_id = Column(Integer, ForeignKey('objects.id'), nullable=False)


class Idea(Base, NameMixin, OwnerMixin):
    """An idea."""

    __tablename__ = 'ideas'
    body = Column(String(10000), nullable=False)
    created = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    votes = relationship(
        'Object', secondary=IdeaVote.__table__, backref='idea_votes'
    )


class IdeaComment(Base, OwnerMixin):
    """A comment on an idea."""

    __tablename__ = 'idea_comments'
    text = Column(String(10000), nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    idea = relationship('Idea', backref='comments')
    created = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
