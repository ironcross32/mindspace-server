"""Provides the database engine."""

from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:')
