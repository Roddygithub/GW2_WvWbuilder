"""Database module for GW2 WvW Builder.

This module provides database session management and initialization.
"""

from .base import Base
from .session import engine, async_engine, init_db
from .factories import SessionLocal, AsyncSessionLocal
from .dependencies import get_db, get_async_db

__all__ = [
    # SQLAlchemy Base
    "Base",
    # Session factories
    "SessionLocal",
    "AsyncSessionLocal",
    # Engines
    "engine",
    "async_engine",
    # Session getters
    "get_db",
    "get_async_db",
    # Initialization
    "init_db",
]
