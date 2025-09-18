"""Simple test for database initialization."""
import os
import asyncio
import pytest
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the application's Base
from app.models.base_models import Base

# Test database URL - using file-based SQLite for better debugging
TEST_DB_PATH = "test_simple.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

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
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models import (  # noqa: F401
        User, Role, Profession, EliteSpecialization,
        Composition, CompositionTag, Build, BuildProfession
    )
    
    # Create a connection
    async with test_engine.connect() as conn:
        # Check tables before creation
        logger.info("Checking tables before creation...")
        tables_before = await print_tables(conn)
        
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
    
    # Don't remove the database file so we can inspect it
    logger.info(f"Test database file: {os.path.abspath(TEST_DB_PATH)}")
    assert os.path.exists(TEST_DB_PATH), "Database file was not created"
