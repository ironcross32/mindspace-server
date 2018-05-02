"""Provides the database engine."""

from sqlalchemy import create_engine
from .. import db_engine

engine = create_engine(*db_engine.engine_args, **db_engine.engine_kwargs)
