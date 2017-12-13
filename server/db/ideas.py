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

    def add_comment(self, obj, text, parent=None):
        """Add a comment containing text with owner obj. If parent is not None
        then the new comment is considered in reply to parent."""
        return IdeaComment(
            text=text, idea_id=self.id, owner_id=obj.id,
            parent_id=None if parent is None else parent.id
        )


class IdeaComment(Base, OwnerMixin):
    """A comment on an idea."""

    __tablename__ = 'idea_comments'
    text = Column(String(10000), nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    idea = relationship('Idea', backref='comments')
    parent_id = Column(
        Integer, ForeignKey(__tablename__ + '.id'), nullable=True
    )
    parent = relationship(
        'IdeaComment', backref='replies', remote_side='IdeaComment.id'
    )
    created = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
