from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
def get_engine():
    """Create and return a SQLAlchemy engine."""
    db_url = settings.get_database_url()
    connect_args = {}
    
    if "sqlite" in db_url:
        connect_args["check_same_thread"] = False
    
    return create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args=connect_args
    )

# Create engine instance
engine = get_engine()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency function that yields db sessions.
    
    Yields:
        Session: A database session.
        
    Example:
        ```python
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Import models here to avoid circular imports
    from app.models import (  # noqa: F401
        user,
        role,
        profession,
        composition,
    )
    
    Base.metadata.create_all(bind=engine)
