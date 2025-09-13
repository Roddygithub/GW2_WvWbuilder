"""Integration test for database initialization and schema."""
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
from app.db.session import async_engine, init_db
from app.models.base_models import Base

# Test database path - using absolute path to avoid any path resolution issues
TEST_DB_PATH = os.path.abspath("test_integration.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Override the async_engine with our test database URL
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
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Verify the database file was created
    assert os.path.exists(TEST_DB_PATH), f"Database file was not created at {TEST_DB_PATH}"
    logger.info(f"Database file created at: {TEST_DB_PATH}")
    
    yield
    
    # Clean up (comment out to inspect the database after tests)
    # if os.path.exists(TEST_DB_PATH):
    #     os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_database_schema(db_setup):
    """Test that all expected tables are created with the correct schema."""
    # Get list of tables
    async with test_engine.connect() as conn:
        # Get list of tables
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
        
        # Verify the structure of a few key tables
        await verify_table_structure(conn, 'users', ['id', 'email', 'hashed_password', 'is_active', 'is_superuser'])
        await verify_table_structure(conn, 'roles', ['id', 'name', 'description', 'is_default', 'permission_level'])
        await verify_table_structure(conn, 'professions', ['id', 'name', 'description'])

async def verify_table_structure(conn, table_name, expected_columns):
    """Verify that a table has the expected columns."""
    # Get column info
    result = await conn.execute(text(f"PRAGMA table_info({table_name});"))
    columns = [row[1] for row in result.fetchall()]  # row[1] is the column name
    
    logger.info(f"Table {table_name} columns: {columns}")
    
    # Check that all expected columns exist
    for col in expected_columns:
        assert col in columns, f"Column {col} not found in table {table_name}"

@pytest.mark.asyncio
async def test_database_operations(db_setup):
    """Test basic CRUD operations on the database."""
    async with TestingSessionLocal() as session:
        try:
            # Insert test data
            await session.execute(text("""
                INSERT INTO roles (name, description, is_default, permission_level) 
                VALUES ('test_role', 'Test Role', 0, 1)
            
            """))
            
            # Insert a test user
            await session.execute(text("""
                INSERT INTO users (email, hashed_password, is_active, is_superuser, full_name)
                VALUES ('test@example.com', 'hashed_password', 1, 0, 'Test User')
            
            """))
            
            # Insert a test profession
            await session.execute(text("""
                INSERT INTO professions (name, description)
                VALUES ('Test Profession', 'A test profession')
            
            """))
            
            await session.commit()
            
            # Verify the data was inserted
            result = await session.execute(text("SELECT name FROM roles WHERE name = 'test_role'"))
            role = result.scalar_one_or_none()
            assert role == 'test_role', "Failed to insert and query test role"
            
            result = await session.execute(text("SELECT email FROM users WHERE email = 'test@example.com'"))
            user = result.scalar_one_or_none()
            assert user == 'test@example.com', "Failed to insert and query test user"
            
            result = await session.execute(text("SELECT name FROM professions WHERE name = 'Test Profession'"))
            profession = result.scalar_one_or_none()
            assert profession == 'Test Profession', "Failed to insert and query test profession"
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during database operations: {e}")
            raise
        finally:
            await session.close()
