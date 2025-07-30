# co_optimal/models/base.py
"""Base model class for SQLAlchemy models."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# This will be used for creating database sessions
# The actual engine will be configured elsewhere
Session = sessionmaker()
