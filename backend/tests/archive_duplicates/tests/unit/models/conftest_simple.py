"""
Simple test configuration for model tests.
"""

import asyncio
import logging
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Import all models to ensure they're registered with SQLAlchemy
from app.models.base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    # Create engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
        poolclass=NullPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Log all tables for debugging
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Created tables: {tables}")

    yield engine

    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for testing."""
    # Create a new session
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # Create a new session for testing
    async with async_session() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db):
    """Clean all data from the database before each test."""
    # Clean up all data before each test
    for table in reversed(Base.metadata.sorted_tables):
        try:
            await db.execute(table.delete())
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.warning(f"Could not clean table {table.name}: {e}")

    # Yield control to the test
    yield

    # Clean up after test
    for table in reversed(Base.metadata.sorted_tables):
        try:
            await db.execute(table.delete())
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.warning(f"Could not clean table {table.name} after test: {e}")
