# co_optimal/models/user.py
"""User model for the application."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from base import Base


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    bio = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
