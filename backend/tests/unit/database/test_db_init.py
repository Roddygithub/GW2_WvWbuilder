"""Test database initialization."""
import os
import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Import all models to ensure they're registered with SQLAlchemy
from app.models.base_models import Base
from app.models import (  # noqa: F401
    User, Role, Profession, EliteSpecialization,
    Composition, CompositionTag, Build, build_profession
)

# Test database URL - using file-based SQLite for better debugging
TEST_DB_URL = "sqlite+aiosqlite:///test_db_init.db"

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

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Set up the test database with all tables."""
    # Remove existing test database if it exists
    if os.path.exists("test_db_init.db"):
        os.remove("test_db_init.db")
    
    # Create all tables using the application's Base metadata
    async with test_engine.begin() as conn:
        # First, verify no tables exist
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables before creation: {tables}")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables were created
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables after creation: {tables}")
        
        # Check if the roles table exists
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='roles';"))
        roles_table = result.fetchone()
        assert roles_table is not None, "Roles table was not created"
    
    yield
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()
    
    if os.path.exists("test_db_init.db"):
        os.remove("test_db_init.db")

@pytest.mark.asyncio
async def test_tables_created():
    """Test that all tables were created."""
    async with TestingSessionLocal() as session:
        # Check if the roles table exists
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables in test: {tables}")
        
        # Verify all expected tables exist
        expected_tables = [
            'users', 'roles', 'user_roles', 'professions', 
            'elite_specializations', 'compositions', 'composition_tags',
            'composition_members', 'builds', 'build_professions'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
        
        # Verify we can query the roles table
        result = await session.execute(text("SELECT COUNT(*) FROM roles"))
        count = result.scalar_one()
        print(f"Number of roles: {count}")
        
        # Verify we can insert a role
        await session.execute(
            text("INSERT INTO roles (name, description, is_default, permission_level) VALUES ('test_role', 'Test Role', 0, 1)")
        )
        await session.commit()
        
        # Verify the role was inserted
        result = await session.execute(text("SELECT COUNT(*) FROM roles WHERE name = 'test_role'"))
        count = result.scalar_one()
        assert count == 1, "Failed to insert role"
