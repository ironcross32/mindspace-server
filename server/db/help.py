"""Provides classes for working with help topics."""

from sqlalchemy import Column, Integer, ForeignKey, or_, func
from sqlalchemy.orm import relationship
from .base import Base, NameMixin, TextMixin, PermissionsMixin


class HelpTopicKeyword(Base):
    """Connect help topics to keywords."""

    __tablename__ = 'help_topics_keywords'
    keyword_id = Column(Integer, ForeignKey('help_keywords.id'))
    help_topic_id = Column(Integer, ForeignKey('help_topics.id'))


class HelpKeyword(Base, NameMixin):
    """A keyword that can be applied to 0 or more topics."""

    __tablename__ = 'help_keywords'
    help_topics = relationship(
        'HelpTopic', secondary=HelpTopicKeyword.__table__, backref='keywords'
    )

    @classmethod
    def create(cls, word):
        return cls(name=word)


class HelpTopic(Base, NameMixin, TextMixin, PermissionsMixin):
    """A help topic."""

    __tablename__ = 'help_topics'

    @property
    def url(self):
        return f'/help/{self.id}'

    @classmethod
    def from_string(cls, name, string):
        """Instantiate this class with a string."""
        return cls(name=name, text=string)

    @classmethod
    def from_filename(cls, name, filename, flags='r'):
        """Instantiates this class with a filename."""
        with open(filename, flags) as f:
            return cls.from_fp(name, f)

    @classmethod
    def from_fp(cls, name, fp):
        """Inttantiates this class from a file-like object."""
        return cls(name=name, text=fp.read())

    @classmethod
    def search(cls, term, player=None):
        """Split term into words and search HelpKeyword. If who is not None
        then their permissions will be used."""
        if player is None:
            builder = False
            admin = False
        else:
            builder = player.is_builder
            admin = player.is_admin
        words = term.lower().replace('+', ' ').split(' ')
        results = []
        args = []
        for word in words:
            args.append(
                func.lower(HelpKeyword.name).like(f'%{word}%')
            )
            kwargs = {}
            if not builder:
                kwargs['builder'] = False
            if not admin:
                kwargs['admin'] = False
            results.extend(
                cls.query(
                    or_(
                        func.lower(cls.name).like(f'%{word}%'),
                        func.lower(cls.text).like(f'%{word}%')
                    ), **kwargs
                )
            )
        for keyword in HelpKeyword.query(or_(*args)):
            for topic in keyword.help_topics:
                if builder >= topic.builder and admin >= topic.admin:
                    results.append(topic)
        topics = []
        for result in results:
            if result not in topics:
                topics.append(result)
        return topics

    @property
    def related_topics(self):
        topics = []
        for keyword in self.keywords:
            for topic in keyword.help_topics:
                if topic not in topics and topic is not self:
                    topics.append(topic)
        return topics
