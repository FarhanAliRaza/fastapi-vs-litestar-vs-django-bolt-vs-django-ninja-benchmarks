"""
Shared database models for benchmark tests.

Uses SQLAlchemy for FastAPI/Litestar and Django ORM for Django-based frameworks.
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """SQLAlchemy User model for FastAPI/Litestar."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False, default="")
    last_name = Column(String(50), nullable=False, default="")
    is_active = Column(Boolean, default=True)


class UserResponse(BaseModel):
    """Pydantic response model for User."""

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True
