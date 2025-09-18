"""Direct test of database initialization."""
import os
import asyncio
import pytest
import sqlite3
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test database path
TEST_DB_PATH = "test_direct_init.db"

# Import the application's database initialization
from app.db.session import init_db, Base, async_engine

# Create a test engine
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=True,
    connect_args={"check_same_thread": False, "timeout": 30}
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
    
    # Override the async_engine with our test engine
    import app.db.session
    original_engine = app.db.session.async_engine
    app.db.session.async_engine = test_engine
    
    # Initialize the database
    await init_db()
    
    yield
    
    # Restore the original engine
    app.db.session.async_engine = original_engine
    
    # Clean up (comment out to inspect the database after tests)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_database_file_created(db_setup):
    """Test that the database file is created and not empty."""
    # Check if the database file exists
    assert os.path.exists(TEST_DB_PATH), f"Database file {TEST_DB_PATH} was not created"
    
    # Check if the file has content
    size = os.path.getsize(TEST_DB_PATH)
    logger.info(f"Database file size: {size} bytes")
    assert size > 0, "Database file is empty"

@pytest.mark.asyncio
async def test_tables_exist():
    """Test that the expected tables exist in the database."""
    # Connect to the SQLite database directly
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Tables in database: {tables}")
        
        # Check for expected tables (without filtering out sqlite_ tables)
        expected_tables = [
            'alembic_version', 'users', 'roles', 'user_roles', 'professions', 
            'elite_specializations', 'compositions', 'composition_tags',
            'composition_members', 'builds', 'build_professions'
        ]
        
        # Log the difference between expected and actual tables
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
        
        # Verify all expected tables exist
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
            
    finally:
        conn.close()

@pytest.mark.asyncio
async def test_initial_data_loaded():
    """Test that initial data is loaded into the database."""
    # Connect to the SQLite database directly
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables name-based access to columns
    cursor = conn.cursor()
    
    try:
        # Check if roles are created
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        logger.info(f"Found {len(roles)} roles in the database")
        assert len(roles) > 0, "No roles found in the database"
        
        # Check if default roles exist
        cursor.execute("SELECT name FROM roles WHERE name IN ('admin', 'user')")
        role_names = [row[0] for row in cursor.fetchall()]
        assert 'admin' in role_names, "Admin role not found"
        assert 'user' in role_names, "User role not found"
        
        # Check if professions are created
        cursor.execute("SELECT * FROM professions")
        professions = cursor.fetchall()
        logger.info(f"Found {len(professions)} professions in the database")
        assert len(professions) > 0, "No professions found in the database"
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        raise
    finally:
        conn.close()
