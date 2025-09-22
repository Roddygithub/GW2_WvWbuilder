"""Database module for GW2 WvW Builder.

This module provides database session management and initialization.
"""

from .base import Base
from .session import (
    SessionLocal,
    AsyncSessionLocal,
    engine,
    async_engine,
    get_db,
    get_async_db,
    init_db,
)

__all__ = [
    # SQLAlchemy Base
    "Base",
    # Session factories
    "SessionLocal",
    "AsyncSessionLocal",
    # Engines
    "engine",
    "async_engine",
    # DB utilities
    "get_db",
    "get_async_db",
    "init_db",
]
