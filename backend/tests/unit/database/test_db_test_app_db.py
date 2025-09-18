"""Test application database initialization."""
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

# Test database URL - using file-based SQLite for better debugging
TEST_DB_PATH = "test_app.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Override the async_engine with our test database URL
async_engine = create_async_engine(
    TEST_DB_URL,
    echo=True,
    connect_args={"check_same_thread": False, "timeout": 30}
)

TestingSessionLocal = async_sessionmaker(
    bind=async_engine,
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

@pytest.fixture(scope="session")
async def db_setup():
    """Set up the test database."""
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Initialize the database
    await init_db()
    
    yield
    
    # Clean up (optional, comment out to inspect the database after tests)
    # if os.path.exists(TEST_DB_PATH):
    #     os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_database_initialization(db_setup):
    """Test that the application database can be initialized with all tables."""
    # Check if the database file was created
    assert os.path.exists(TEST_DB_PATH), "Database file was not created"
    
    # Verify the database file has content
    size = os.path.getsize(TEST_DB_PATH)
    assert size > 0, "Database file is empty"
    logger.info(f"Database file size: {size} bytes")
    
    # Verify tables were created by checking for some expected tables
    async with async_engine.connect() as conn:
        # Get list of tables
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Tables in database: {tables}")
        
        # Check for some expected tables
        expected_tables = ['users', 'roles', 'professions']
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
        
        # Test inserting and querying data
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
    
    logger.info(f"Test database file created at: {os.path.abspath(TEST_DB_PATH)}")
