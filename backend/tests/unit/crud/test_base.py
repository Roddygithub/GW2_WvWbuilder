"""Tests for base CRUD operations."""

import pytest
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base as orm_declarative_base

from app.crud.base import CRUDBase

# Create a base class for our test models
Base = orm_declarative_base()


# Test Models
class TestModel(Base):
    """Test model for CRUD operations."""

    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)


class TestCreateSchema(BaseModel):
    """Test create schema."""

    name: str
    is_active: bool = True


class TestUpdateSchema(BaseModel):
    """Test update schema."""

    name: Optional[str] = None
    is_active: Optional[bool] = None


# Fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_engine():
    """Create database engine and tables."""
    # Create a fresh engine for testing with a unique in-memory database
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=True, future=True
    )

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Clean up
    await test_engine.dispose()


@pytest.fixture
def async_session_maker(db_engine):
    """Create a session maker for async tests."""
    return sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def db_session(async_session_maker):
    """Create a database session with automatic cleanup."""
    async with async_session_maker() as session:
        # Clear any existing data
        await session.execute(delete(TestModel))
        await session.commit()

        try:
            yield session
            await session.rollback()
        finally:
            await session.close()
            await session.commit()


@pytest.fixture
def crud():
    """Create a CRUDBase instance for testing."""
    return CRUDBase(TestModel)


@pytest.fixture
def test_model():
    """Create a test model instance."""
    return TestModel(name="test_model", is_active=True)


@pytest.fixture
def test_create_schema():
    """Create a test create schema."""
    return TestCreateSchema(name="test", is_active=True)


@pytest.fixture
def test_update_schema():
    """Create a test update schema."""
    return TestUpdateSchema(name="updated")


# Tests
def test_crud_init(crud):
    """Test CRUDBase initialization."""
    assert crud.model == TestModel
    assert hasattr(crud, "_select_stmt")
    assert str(crud._select_stmt) == str(select(TestModel))


@pytest.mark.asyncio
async def test_get_async(db_session, crud):
    """Test asynchronous get method."""
    # Create and add test model to the database
    test_model = TestModel(name="test_get_async", is_active=True)
    db_session.add(test_model)
    await db_session.commit()

    # Test with ID
    result = await crud.get_async(db_session, test_model.id)
    assert result is not None
    assert result.id == test_model.id
    assert result.name == test_model.name
    assert result.is_active is True


@pytest.mark.asyncio
async def test_get_multi_async(db_session, crud):
    """Test asynchronous get_multi method."""
    # Clear any existing data
    await db_session.execute(delete(TestModel))

    # Add test models to the database with unique IDs
    test_models = [
        TestModel(name="test1", is_active=True),
        TestModel(name="test2", is_active=True),
        TestModel(name="test3", is_active=False),
    ]

    for model in test_models:
        db_session.add(model)
    await db_session.commit()

    # Test get_multi with default parameters
    results = await crud.get_multi_async(db_session)
    assert len(results) == 3

    # Test with skip and limit
    results = await crud.get_multi_async(db_session, skip=1, limit=1)
    assert len(results) == 1
    assert results[0].id == 2


@pytest.mark.asyncio
async def test_create_async(db_session, crud, test_create_schema):
    """Test asynchronous create method."""
    # Test create_async
    result = await crud.create_async(db_session, obj_in=test_create_schema)

    # Verify the result
    assert result is not None
    assert result.id is not None
    assert result.name == test_create_schema.name
    assert result.is_active == test_create_schema.is_active

    # Verify the record was actually created in the database
    db_result = await crud.get_async(db_session, id=result.id)
    assert db_result is not None
    assert db_result.name == test_create_schema.name


@pytest.mark.asyncio
async def test_update_async(db_session, crud, test_update_schema):
    """Test asynchronous update method."""
    # Create and add a test model to the database
    test_model = TestModel(name="test_update_async", is_active=True)
    db_session.add(test_model)
    await db_session.commit()

    # Test update_async
    updated = await crud.update_async(
        db_session, db_obj=test_model, obj_in=test_update_schema
    )

    # Verify the result
    assert updated is not None
    assert updated.id == test_model.id
    assert updated.name == test_update_schema.name

    # Verify the record was actually updated in the database
    db_result = await crud.get_async(db_session, id=test_model.id)
    assert db_result is not None
    assert db_result.name == test_update_schema.name


@pytest.mark.asyncio
async def test_remove_async(db_session, crud):
    """Test asynchronous remove method."""
    # Create and add a test model to the database
    test_model = TestModel(name="test_remove", is_active=True)
    db_session.add(test_model)
    await db_session.commit()
    await db_session.refresh(test_model)

    # Get the ID after commit to ensure it's set
    model_id = test_model.id

    # Test remove_async
    removed = await crud.remove_async(db_session, id=model_id)

    # Verify the result
    assert removed is not None
    assert removed.id == model_id

    # Verify the record was actually removed from the database
    db_result = await crud.get_async(db_session, id=model_id)
    assert db_result is None


@pytest.mark.asyncio
async def test_count_async(db_session, crud):
    """Test asynchronous count method."""
    # Verify empty database
    count = await crud.count_async(db_session)
    assert count == 0, f"Expected 0 records, got {count}"

    # Add test models to the database
    test_models = [
        TestModel(name="test1", is_active=True),
        TestModel(name="test2", is_active=True),
        TestModel(name="test3", is_active=False),
    ]

    db_session.add_all(test_models)
    await db_session.commit()

    # Test count_async
    count = await crud.count_async(db_session)
    assert count == 3, f"Expected 3 records, got {count}"

    # Test with filter
    count_active = await crud.count_async(db_session, is_active=True)
    assert count_active == 2, f"Expected 2 active records, got {count_active}"


@pytest.mark.asyncio
async def test_exists_async(db_session, crud):
    """Test asynchronous exists method."""
    # Create and add a test model to the database
    test_model = TestModel(name="test_exists", is_active=True)
    db_session.add(test_model)
    await db_session.commit()

    # Test exists_async with existing ID
    exists = await crud.exists_async(db_session, id=test_model.id)
    assert exists is True

    # Test exists_async with non-existing ID
    exists = await crud.exists_async(db_session, id=999999)
    assert exists is False


# Test the CRUDBase initialization
def test_crud_init(crud):
    """Test CRUDBase initialization."""
    assert crud.model == TestModel
    assert hasattr(crud, "_select_stmt")
    assert str(crud._select_stmt) == str(select(TestModel))
