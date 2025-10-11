"""Tests for CRUD base functionality."""

import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, select, delete
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

# Import the module/class to test
from app.crud.base import CRUDBase

# Create a test model
Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    def __repr__(self):
        return f"<TestModel(id={self.id}, name='{self.name}')>"


# Database setup for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Global engine and session factory
_engine = None
_async_session_factory = None


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator:
    """Fixture to initialize the database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
            echo=True,  # Enable SQL echo for debugging
        )

        # Create all tables
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield _engine

    # Cleanup
    await _engine.dispose()


@pytest.fixture
def async_session_maker(engine):
    """Create a sessionmaker for async tests."""
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(engine, async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Fixture to create a new database session for each test."""
    # Create a new session
    async with async_session_maker() as session:
        # Start a transaction
        await session.begin()

        try:
            yield session
        finally:
            # Rollback any changes made during the test
            await session.rollback()


@pytest.fixture(autouse=True)
async def clean_db(db_session):
    """Clean the database before each test."""
    # Delete all data from all tables
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(delete(table))
    await db_session.commit()


# Test cases
class TestCRUDBase:
    """Test cases for CRUDBase class."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test that CRUDBase can be initialized with a model."""
        crud = CRUDBase(TestModel)
        assert crud.model == TestModel
        assert hasattr(crud, "_select_stmt")
        assert str(crud._select_stmt) == str(select(TestModel))

    @pytest.mark.asyncio
    async def test_get_async(self, db_session):
        """Test getting a single item by ID asynchronously."""
        # Create a test item
        test_item = TestModel(id=1, name="Test Item", description="A test item")
        db_session.add(test_item)
        await db_session.commit()

        # Test get_async method
        crud = CRUDBase(TestModel)
        result = await crud.get_async(db_session, id=1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Item"
        assert result.description == "A test item"

    @pytest.mark.asyncio
    async def test_get_async_not_found(self, db_session):
        """Test getting a non-existent item returns None asynchronously."""
        crud = CRUDBase(TestModel)
        result = await crud.get_async(db_session, id=999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_async(self, db_session):
        """Test getting multiple items asynchronously."""
        # Create test items
        items = [
            TestModel(id=i, name=f"Item {i}", description=f"Description {i}") for i in range(1, 6)  # IDs from 1 to 5
        ]

        db_session.add_all(items)
        await db_session.commit()

        # Test get_multi_async method with default parameters
        crud = CRUDBase(TestModel)
        results = await crud.get_multi_async(db_session)

        assert len(results) == 5
        # Sort results by id to ensure consistent ordering
        sorted_results = sorted(results, key=lambda x: x.id)
        for i, item in enumerate(sorted_results, 1):
            assert item.id == i
            assert item.name == f"Item {i}"
            assert item.description == f"Description {i}"

    @pytest.mark.asyncio
    async def test_get_multi_async_with_skip_limit(self, db_session):
        """Test getting paginated items asynchronously."""
        # Create test items
        items = [TestModel(id=i, name=f"Item {i}", description=f"Description {i}") for i in range(1, 11)]  # 10 items

        db_session.add_all(items)
        await db_session.commit()

        # Test get_multi_async with pagination
        crud = CRUDBase(TestModel)

        # First page: items 1-5
        page1 = await crud.get_multi_async(db_session, skip=0, limit=5)
        assert len(page1) == 5
        assert page1[0].id == 1
        assert page1[-1].id == 5

        # Second page: items 6-10
        page2 = await crud.get_multi_async(db_session, skip=5, limit=5)
        assert len(page2) == 5
        assert page2[0].id == 6
        assert page2[-1].id == 10

    @pytest.mark.asyncio
    async def test_create_async(self, db_session):
        """Test creating an item asynchronously."""
        crud = CRUDBase(TestModel)

        # Test data
        item_data = {"id": 1, "name": "New Item", "description": "A new test item"}

        # Create item
        created_item = await crud.create_async(db_session, obj_in=item_data)

        # Verify the item was created
        assert created_item.id == 1
        assert created_item.name == "New Item"
        assert created_item.description == "A new test item"

        # Verify the item is in the database
        result = await crud.get_async(db_session, id=1)
        assert result is not None
        assert result.name == "New Item"
        assert result.description == "A new test item"

    @pytest.mark.asyncio
    async def test_update_async(self, db_session):
        """Test updating an item asynchronously."""
        # First create an item
        crud = CRUDBase(TestModel)
        item = TestModel(id=1, name="Old Name", description="Old Description")
        db_session.add(item)
        await db_session.commit()

        # Update the item
        updated_data = {"name": "Updated Name", "description": "Updated Description"}
        updated_item = await crud.update_async(db_session, db_obj=item, obj_in=updated_data, commit=True)

        # Verify the update
        assert updated_item.name == "Updated Name"
        assert updated_item.description == "Updated Description"

        # Verify the update in the database
        result = await crud.get_async(db_session, id=1)
        assert result.name == "Updated Name"
        assert result.description == "Updated Description"

    @pytest.mark.asyncio
    async def test_remove_async(self, db_session):
        """Test removing an item asynchronously."""
        # First create an item
        crud = CRUDBase(TestModel)
        item = TestModel(id=1, name="Item to remove", description="Will be removed")
        db_session.add(item)
        await db_session.commit()

        # Remove the item
        removed_item = await crud.remove_async(db_session, id=1)
        await db_session.commit()

        # Verify the removed item is returned
        assert removed_item is not None
        assert removed_item.id == 1

        # Verify the item is no longer in the database
        result = await crud.get_async(db_session, id=1)
        assert result is None
