"""Minimal test for database setup."""
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

# Create a minimal model
Base = declarative_base()

class TestTable(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Test database URL - using file-based SQLite for better debugging
TEST_DB_URL = "sqlite+aiosqlite:///test_minimal.db"

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

@pytest.mark.asyncio
async def test_minimal_database():
    """Test that we can create a minimal database and table."""
    # Remove existing test database if it exists
    if os.path.exists("test_minimal.db"):
        os.remove("test_minimal.db")
    
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
        finally:
            await session.close()
    
    # Clean up
    if os.path.exists("test_minimal.db"):
        os.remove("test_minimal.db")
