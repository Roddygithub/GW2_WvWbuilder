"""
Minimal test file to verify database setup.
"""

import asyncio
import logging
import pytest
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all models to ensure they're registered with SQLAlchemy
from app.models import Base, User, Role

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a test engine
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True,
)

# Create a session factory
TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


# Create tables before tests
@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def setup_db():
    """Set up the database with all tables."""
    logger.info("Setting up test database...")

    # Import all models to ensure they're registered with SQLAlchemy
    logger.info("Importing models...")
    from app.models import (
        User,
        Role,
        Profession,
        EliteSpecialization,
        Composition,
        CompositionTag,
        Build,
    )
    from app.models.association_tables import composition_members, build_profession
    from app.models.user_role import UserRole as user_roles

    # Explicitly set table names to match the database schema
    User.__table__.name = "users"
    Role.__table__.name = "roles"
    Profession.__table__.name = "professions"
    EliteSpecialization.__table__.name = "elite_specializations"
    Composition.__table__.name = "compositions"
    CompositionTag.__table__.name = "composition_tags"
    Build.__table__.name = "builds"
    composition_members.name = "composition_members"
    user_roles.name = "user_roles"
    build_profession.name = "build_profession"

    # Create all tables
    logger.info("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Verify tables were created
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Created tables: {tables}")

        # Check if all expected tables exist
        expected_tables = [
            "users",
            "roles",
            "professions",
            "elite_specializations",
            "compositions",
            "composition_tags",
            "builds",
            "composition_members",
            "user_roles",
            "build_profession",
        ]

        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
        else:
            logger.info("All expected tables were created successfully")

    logger.info("Test database setup complete")

    # Yield control to the test
    yield

    # Clean up
    logger.info("Tearing down test database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Test database teardown complete")


@pytest.fixture
def db():
    """Create a new database session for testing."""
    return TestingSessionLocal()


@pytest.mark.asyncio
class TestMinimalDB:
    """Minimal test class to verify the database setup."""

    async def test_tables_exist(self, setup_db, db):
        """Verify that all expected tables exist."""
        # Get all tables in the database
        result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Tables in database: {tables}")

        # Check for some expected tables
        required_tables = [
            "users",
            "roles",
            "professions",
            "elite_specializations",
            "compositions",
            "composition_tags",
            "builds",
            "composition_members",
            "user_roles",
            "build_profession",
        ]

        # Log the metadata for debugging
        logger.info(f"Base metadata tables: {list(Base.metadata.tables.keys())}")

        for table in required_tables:
            assert table in tables, f"Required table {table} not found in database. Found tables: {tables}"

    async def test_create_user(self, setup_db, db):
        """Test creating a simple user."""
        try:
            # First, verify the roles table exists
            result = await db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")  # type: ignore
            )
            roles_table_exists = result.scalar_one_or_none() is not None
            logger.info(f"Roles table exists: {roles_table_exists}")

            if not roles_table_exists:
                # If roles table doesn't exist, create all tables again
                logger.info("Creating all tables...")
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

            # Create a role (required for the user)
            test_role = Role(
                name="test_role",
                description="Test Role",
                permission_level=1,
                is_default=True,
            )
            db.add(test_role)
            await db.flush()  # Flush to get the role ID
            logger.info(f"Created role with ID: {test_role.id}")

            # Create a test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password",
                full_name="Test User",
            )
            db.add(test_user)
            await db.flush()
            logger.info(f"Created user with ID: {test_user.id}")

            # Verify the user was created
            result = await db.execute(select(User).where(User.username == "testuser"))
            user = result.scalar_one_or_none()
            assert user is not None, "User was not created"
            assert user.username == "testuser", "Username does not match"
            assert user.email == "test@example.com", "Email does not match"

            # Commit the transaction
            await db.commit()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error in test_create_user: {e}")
            raise
        finally:
            await db.close()
