"""Tests for database session management."""
import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.db.session import (
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    get_db,
    init_db,
    DATABASE_URL,
    ASYNC_DATABASE_URL
)
from app.models.base import Base
from app.core.config import settings


def test_database_urls():
    """Test that database URLs are correctly constructed."""
    # Test sync URL
    assert DATABASE_URL.startswith("sqlite:///")
    
    # Test async URL
    assert ASYNC_DATABASE_URL.startswith("sqlite+aiosqlite:///")
    assert ASYNC_DATABASE_URL.endswith(DATABASE_URL.split("///")[1])


def test_sync_engine_creation():
    """Test that the synchronous engine is created correctly."""
    assert engine is not None
    assert str(engine.url) == DATABASE_URL
    assert engine.pool.pre_ping is True


def test_async_engine_creation():
    """Test that the asynchronous engine is created correctly."""
    assert async_engine is not None
    assert str(async_engine.url) == ASYNC_DATABASE_URL
    assert async_engine.pool.pre_ping is True


def test_sync_session_factory():
    """Test that the synchronous session factory is configured correctly."""
    # Test session factory configuration
    session = SessionLocal()
    try:
        assert isinstance(session, Session)
        assert session.bind == engine
        assert session.autocommit is False
        assert session.autoflush is False
        assert session.expire_on_commit is False
    finally:
        session.close()


def test_async_session_factory():
    """Test that the asynchronous session factory is configured correctly."""
    # Test async session factory configuration
    session = AsyncSessionLocal()
    try:
        assert isinstance(session, AsyncSession)
        assert session.bind == async_engine
        assert session.autocommit is False
        assert session.autoflush is False
        assert session.expire_on_commit is False
    finally:
        # Close the session in a non-async context
        import asyncio
        asyncio.get_event_loop().run_until_complete(session.close())


def test_get_db():
    """Test the get_db dependency generator."""
    # Create a test database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Test that we get a valid session
        assert isinstance(db, Session)
        
        # Test that the session is closed after use
        assert db.is_active is True
    finally:
        # Clean up by consuming the generator
        try:
            next(db_gen)
        except StopIteration:
            pass
    
    # Verify the session is closed
    assert db.is_active is False


def test_init_db():
    """Test database initialization."""
    # Create an in-memory SQLite database for testing
    test_engine = create_engine('sqlite:///:memory:')
    
    # Patch the engine in the session module
    with patch('app.db.session.engine', test_engine):
        # Mock the model imports to avoid circular imports
        with patch('app.db.session.User', create=True), \
             patch('app.db.session.Role', create=True), \
             patch('app.db.session.Profession', create=True), \
             patch('app.db.session.EliteSpecialization', create=True), \
             patch('app.db.session.Composition', create=True), \
             patch('app.db.session.CompositionTag', create=True), \
             patch('app.db.session.Build', create=True), \
             patch('app.db.session.BuildProfession', create=True):
            
            # Call init_db
            init_db()
            
            # Verify that create_all was called
            # We can check this by verifying that the tables exist
            with test_engine.connect() as conn:
                # This will raise an exception if the table doesn't exist
                conn.execute(text("SELECT * FROM users LIMIT 1"))
                conn.execute(text("SELECT * FROM roles LIMIT 1"))
                # Add more table checks as needed


@pytest.mark.asyncio
async def test_async_session_operations():
    """Test basic operations with an async session."""
    # Create an in-memory SQLite database for testing
    test_async_engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    
    # Create all tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a test session
    async with AsyncSession(bind=test_async_engine) as session:
        # Test a simple query
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    # Clean up
    await test_async_engine.dispose()


def test_sqlite_connect_args():
    """Test that SQLite connection args are set correctly."""
    # Test with SQLite URL
    with patch('app.core.config.settings.SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'):
        from app.db.session import engine as test_engine
        assert "check_same_thread" in test_engine.connect_args
        assert test_engine.connect_args["check_same_thread"] is False
    
    # Test with non-SQLite URL
    with patch('app.core.config.settings.SQLALCHEMY_DATABASE_URI', 'postgresql://user:pass@localhost/db'):
        from importlib import reload
        import app.db.session as session_module
        reload(session_module)
        assert not hasattr(session_module.engine.connect_args, "check_same_thread")
        
        # Clean up by reloading the original module
        reload(session_module)


if __name__ == "__main__":
    pytest.main([__file__])
