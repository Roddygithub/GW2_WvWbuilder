"""Test configuration and fixtures for CRUD tests."""

import pytest
import pytest_asyncio
from typing import Dict, Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models.base import Base as ModelBase

# Test database URLs
TEST_SYNC_DB_URL = "sqlite:///:memory:"
TEST_ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


# Synchronous test engine and session
@pytest.fixture(scope="module")
def sync_engine():
    """Create a synchronous SQLite in-memory database engine for testing."""
    engine = create_engine(TEST_SYNC_DB_URL, connect_args={"check_same_thread": False}, echo=True)

    # Create all tables
    ModelBase.metadata.create_all(bind=engine)

    yield engine

    # Clean up
    ModelBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(sync_engine):
    """Create a synchronous database session for testing with automatic rollback."""
    connection = sync_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    # Begin a nested transaction (using SAVEPOINT).
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    # Clean up
    session.close()
    transaction.rollback()
    connection.close()


# Asynchronous test engine and session
@pytest_asyncio.fixture(scope="module")
async def async_engine():
    """Create an asynchronous SQLite in-memory database engine for testing."""
    engine = create_async_engine(TEST_ASYNC_DB_URL, connect_args={"check_same_thread": False}, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(async_engine):
    """Create an async database session for testing with automatic rollback."""
    async with async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)() as session:
        # Begin a transaction
        await session.begin()

        # Begin a savepoint
        await session.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.expire_all()
                session.begin_nested()

        yield session

        # Clean up
        await session.rollback()
        await session.close()


# Test data fixtures
@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Return sample test data for CRUD operations."""
    return {"name": "Test Item", "description": "Test Description"}
