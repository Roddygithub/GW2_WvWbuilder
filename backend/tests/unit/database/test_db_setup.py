"""Test database setup and table creation."""
import os
import asyncio
import pytest
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all models to ensure they're registered with SQLAlchemy
from app.models.base_models import Base
from app.models import (  # noqa: F401
    User, Role, Profession, EliteSpecialization,
    Composition, CompositionTag, Build, build_profession
)

# Test database URL - using file-based SQLite for better debugging
TEST_DB_URL = "sqlite+aiosqlite:///test_db_setup.db"

# Create test engine and session factory
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=True,
    connect_args={"check_same_thread": False, "timeout": 30}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

async def print_tables(conn):
    """Print all tables in the database."""
    result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = [row[0] for row in result.fetchall()]
    logger.info(f"Tables in database: {tables}")
    return tables

@pytest.mark.asyncio
async def test_database_initialization():
    """Test that the database can be initialized with all tables."""
    # Remove existing test database if it exists
    if os.path.exists("test_db_setup.db"):
        os.remove("test_db_setup.db")
    
    # Create a connection
    async with test_engine.connect() as conn:
        # Check tables before creation
        logger.info("Checking tables before creation...")
        tables_before = await print_tables(conn)
        assert len(tables_before) == 0, "Database is not empty at the start of the test"
        
        # Create all tables
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
        
        # Check tables after creation
        logger.info("Checking tables after creation...")
        tables_after = await print_tables(conn)
        
        # Verify expected tables exist
        expected_tables = [
            'users', 'roles', 'user_roles', 'professions', 
            'elite_specializations', 'compositions', 'composition_tags',
            'composition_members', 'builds', 'build_professions'
        ]
        
        for table in expected_tables:
            assert table in tables_after, f"Table {table} not found in database"
        
        # Verify we can insert and query data
        async with TestingSessionLocal() as session:
            try:
                # Insert a test role
                await session.execute(
                    text("""
                    INSERT INTO roles (name, description, is_default, permission_level) 
                    VALUES ('test_role', 'Test Role', 0, 1)
                    """)
                )
                await session.commit()
                
                # Query the role
                result = await session.execute(
                    text("SELECT name FROM roles WHERE name = 'test_role'")
                )
                role = result.scalar_one_or_none()
                assert role == 'test_role', "Failed to insert and query test role"
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error during test: {e}")
                raise
            finally:
                await session.close()
    
    # Clean up
    if os.path.exists("test_db_setup.db"):
        os.remove("test_db_setup.db")
