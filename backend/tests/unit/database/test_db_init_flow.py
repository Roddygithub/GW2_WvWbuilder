"""Test database initialization flow."""
import os
import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the application's database initialization
from app.db.session import init_db, async_engine, Base

# Test database path - using absolute path to avoid any path resolution issues
TEST_DB_PATH = os.path.abspath("test_init_flow.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Create a new engine for testing
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=True,
    connect_args={"check_same_thread": False, "timeout": 30}
)

# Create a test session factory
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test module."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def db_setup():
    """Set up the test database."""
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Initialize the database
    await init_db()
    
    # Verify the database file was created
    assert os.path.exists(TEST_DB_PATH), f"Database file was not created at {TEST_DB_PATH}"
    logger.info(f"Database file created at: {TEST_DB_PATH}")
    
    # Check the file size to ensure it's not empty
    size = os.path.getsize(TEST_DB_PATH)
    logger.info(f"Database file size: {size} bytes")
    assert size > 0, "Database file is empty"
    
    yield
    
    # Clean up (comment out to inspect the database after tests)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_database_initialization(db_setup):
    """Test that the database can be initialized with all tables."""
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models import (  # noqa: F401
        User, Role, Profession, EliteSpecialization,
        Composition, CompositionTag, Build, BuildProfession
    )
    
    # Create all tables
    async with test_engine.begin() as conn:
        # Check if tables exist
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        
        # Filter out SQLite system tables
        tables = [t for t in tables if not t.startswith('sqlite_')]
        logger.info(f"Tables in database: {tables}")
        
        # Check for expected tables
        expected_tables = [
            'users', 'roles', 'user_roles', 'professions', 
            'elite_specializations', 'compositions', 'composition_tags',
            'composition_members', 'builds', 'build_professions'
        ]
        
        # Verify all expected tables exist
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"

@pytest.mark.asyncio
async def test_database_operations():
    """Test basic CRUD operations on the database."""
    # Import models to ensure they're registered
    from app.models import User, Role, Profession
    
    async with TestingSessionLocal() as session:
        try:
            # Create a role
            role = Role(name="test_role", description="Test Role", is_default=False, permission_level=1)
            session.add(role)
            await session.commit()
            await session.refresh(role)
            
            # Verify the role was created
            result = await session.execute(text("SELECT name FROM roles WHERE name = 'test_role'"))
            role_name = result.scalar_one_or_none()
            assert role_name == 'test_role', "Failed to create role"
            
            # Create a user
            user = User(
                email="test@example.com",
                hashed_password="hashed_password",
                is_active=True,
                is_superuser=False,
                full_name="Test User"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Verify the user was created
            result = await session.execute(text("SELECT email FROM users WHERE email = 'test@example.com'"))
            user_email = result.scalar_one_or_none()
            assert user_email == 'test@example.com', "Failed to create user"
            
            # Create a profession
            profession = Profession(name="Test Profession", description="A test profession")
            session.add(profession)
            await session.commit()
            await session.refresh(profession)
            
            # Verify the profession was created
            result = await session.execute(text("SELECT name FROM professions WHERE name = 'Test Profession'"))
            prof_name = result.scalar_one_or_none()
            assert prof_name == 'Test Profession', "Failed to create profession"
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during database operations: {e}")
            raise
        finally:
            await session.close()
