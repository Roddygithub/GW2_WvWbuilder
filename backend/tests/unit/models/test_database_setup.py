"""
Test database setup and table creation.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.models import Base, User

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# List of all tables in the correct order for creation and deletion
TABLES_ORDER = [
    "users",
    "roles",
    "user_roles",
    "professions",
    "elite_specializations",
    "builds",
    "build_professions",  # Updated from build_profession to match the actual table name
    "compositions",
    "composition_tags",
    "composition_members",
]


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def engine():
    """Create a test database engine and set up tables."""
    # Create engine with echo=True for debugging
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        # Drop all tables first to ensure a clean state
        await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db(engine):
    """Create a new database session for testing."""
    # Create a new session for testing
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_tables_created(engine):
    """Test that all required tables were created."""
    async with engine.connect() as conn:
        # Get list of tables
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = {row[0] for row in result.fetchall()}

        # Check for required tables
        required_tables = set(TABLES_ORDER)
        assert required_tables.issubset(
            tables
        ), f"Missing tables: {required_tables - tables}"


@pytest.mark.asyncio
async def test_create_user(db):
    """Test creating a user in the database."""
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Verify the user was created
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_superuser is False

    # Clean up
    await db.delete(user)
    await db.commit()
