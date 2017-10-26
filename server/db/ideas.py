"""Provides classes relating to ideas."""

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import Base, OwnerMixin


@attrs_sqlalchemy
class IdeaVote(Base):
    """A vote for an idea."""

    __tablename__ = 'idea_votes'
    idea_id = Column(
        Integer,
        ForeignKey('ideas.id'),
        nullable=False
    )
    voter_id = Column(
        Integer,
        ForeignKey('objects.id'),
        nullable=False
    )


@attrs_sqlalchemy
class Idea(Base, OwnerMixin):
    """An idea."""

    __tablename__ = 'ideas'
    title = Column(String(50), nullable=False, unique=True)
    body = Column(String(10000), nullable=False)
    created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )
    votes = relationship(
        'Object',
        secondary=IdeaVote.__table__,
        backref='idea_votes'
    )

    def __str__(self):
        return '{0.title} (#{0.id})'.format(self)

    def add_comment(self, obj, text, parent=None):
        """Add a comment containing text as obj. If parent is not None then the
        new comment is considered in reply to parent."""
        return IdeaComment(text=text, idea=self, owner=obj, parent=parent)


@attrs_sqlalchemy
class IdeaComment(Base, OwnerMixin):
    """A comment on an idea."""

    __tablename__ = 'idea_comments'
    text = Column(String(10000), nullable=False)
    idea_id = Column(
        Integer,
        ForeignKey('ideas.id'),
        nullable=False
    )
    idea = relationship('Idea', backref='comments')
    parent_id = Column(
        Integer,
        ForeignKey(__tablename__ + '.id'),
        nullable=True
    )
    parent = relationship(
        'IdeaComment',
        backref='replies',
        remote_side='IdeaComment.id'
    )
    created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )
