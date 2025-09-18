"""Basic test for database initialization."""
import os
import asyncio
import pytest
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a minimal model
Base = declarative_base()

class TestTable(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Test database URL - using file-based SQLite for better debugging
TEST_DB_PATH = "test_basic.db"
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

@pytest.mark.asyncio
async def test_basic_database():
    """Test basic database operations."""
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Create all tables
    async with test_engine.begin() as conn:
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        # Verify table was created
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Tables in database: {tables}")
        assert 'test_table' in tables, "Test table was not created"
    
    # Test inserting and querying data
    async with TestingSessionLocal() as session:
        try:
            # Insert a test record
            await session.execute(
                text("INSERT INTO test_table (name) VALUES ('test')")
            )
            await session.commit()
            
            # Query the record
            result = await session.execute(
                text("SELECT name FROM test_table WHERE name = 'test'")
            )
            record = result.scalar_one_or_none()
            assert record == 'test', "Failed to insert and query test record"
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during test: {e}")
            raise
    
    # Verify the database file exists
    assert os.path.exists(TEST_DB_PATH), "Database file was not created"
    logger.info(f"Test database file created at: {os.path.abspath(TEST_DB_PATH)}")
    
    # Print the database file size
    size = os.path.getsize(TEST_DB_PATH)
    logger.info(f"Database file size: {size} bytes")
