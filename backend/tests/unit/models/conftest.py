"""
Test configuration and fixtures for model tests.
"""

import asyncio
import logging
from typing import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

# Import the Base metadata and all models to ensure they're registered with SQLAlchemy
from app.models import (
    Base,
    User,
    Role,
    Profession,
    EliteSpecialization,
    Composition,
    CompositionTag,
    Build,
)
from app.models.association_tables import composition_members, build_profession

# Make sure all models are imported and registered with SQLAlchemy
__all__ = [
    "User",
    "Role",
    "Profession",
    "EliteSpecialization",
    "Composition",
    "CompositionTag",
    "Build",
    "composition_members",
    "user_roles",
    "build_profession",
]

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# List of all tables in the correct order to avoid foreign key constraint issues
TABLES_ORDER = [
    "users",
    "roles",
    "user_roles",
    "professions",
    "elite_specializations",
    "builds",
    "build_profession",
    "tags",
    "compositions",
    "composition_tags",
    "composition_members",
]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    """Create a test database engine and set up tables."""
    # Create engine with echo=True for debugging
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
        poolclass=NullPool,  # Use NullPool for tests to ensure clean state
        connect_args={"check_same_thread": False},
    )

    # Create all tables in the correct order
    async with engine.begin() as conn:
        # Drop all tables first to ensure a clean state
        logger.info("\n=== DEBUG: Dropping all tables ===")
        await conn.run_sync(Base.metadata.drop_all)

        # Log all available tables in metadata
        logger.info("\n=== DEBUG: All tables in Base.metadata ===")
        for name, table in Base.metadata.tables.items():
            logger.info(f"- {name} (columns: {[c.name for c in table.columns]})")

        # Create all tables at once using metadata.create_all
        logger.info("\n=== DEBUG: Creating all tables ===")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Successfully created all tables")

    # Verify tables were created
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Created tables: {tables}")

        # Check for missing tables
        missing_tables = set(TABLES_ORDER) - set(tables)
        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")

    yield engine

    # Clean up
    async with engine.begin() as conn:
        # Drop tables in reverse order to respect foreign key constraints
        for table_name in reversed(TABLES_ORDER):
            table = Base.metadata.tables.get(table_name)
            if table is not None:
                logger.info(f"Dropping table: {table_name}")
                try:
                    await conn.run_sync(table.drop)
                except Exception as e:
                    logger.warning(f"Error dropping table {table_name}: {e}")

    await engine.dispose()


@pytest.fixture
def session_factory(engine):
    """Create a session factory for tests."""
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture(scope="function")
async def db(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for testing."""
    # Create a new session
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
    )

    # Create a new session for testing
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(autouse=True)
async def clean_db(db):
    """Clean all data from the database before and after each test."""
    # Get all table names that exist in the database
    result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    existing_tables = {row[0] for row in result.fetchall()}

    # Clean up all data before each test
    for table_name in reversed(TABLES_ORDER):
        if table_name in existing_tables:
            try:
                await db.execute(text(f"DELETE FROM {table_name}"))
                logger.debug(f"Cleaned data from {table_name}")
            except Exception as e:
                logger.warning(f"Could not clean table {table_name} before test: {e}")

    await db.commit()

    yield

    # Clean up after test
    for table_name in reversed(TABLES_ORDER):
        if table_name in existing_tables:
            try:
                await db.execute(text(f"DELETE FROM {table_name}"))
                logger.debug(f"Cleaned data from {table_name} after test")
            except Exception as e:
                logger.warning(f"Could not clean table {table_name} after test: {e}")

    # Commit the cleanup
    await db.commit()
