"""
Unit tests for base models in the application.
"""

import asyncio
import pytest
from datetime import datetime
from uuid import uuid4

# SQLAlchemy imports
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create a new base class for test models
class TestBase(DeclarativeBase):
    """Base class for test models."""


# Define test models
class TestSQLModel(TestBase):
    """Basic SQLAlchemy test model."""

    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    value = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<TestSQLModel(id={self.id}, name='{self.name}', value={self.value})>"


class TestSQLUUIDModel(TestBase):
    """SQLAlchemy test model with UUID primary key."""

    __tablename__ = "test_uuid_model"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<TestSQLUUIDModel(id='{self.id}', name='{self.name}')>"


class TestSQLTimeStampedModel(TestBase):
    """SQLAlchemy test model with timestamps."""

    __tablename__ = "test_timestamped_model"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    name = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<TestSQLTimeStampedModel(id={self.id}, name='{self.name}')>"


class TestSQLUUIDTimeStampedModel(TestBase):
    """SQLAlchemy test model with UUID primary key and timestamps."""

    __tablename__ = "test_uuid_timestamped_model"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    name = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<TestSQLUUIDTimeStampedModel(id='{self.id}', name='{self.name}')>"


# Pytest fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create a new engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    yield engine

    # Clean up
    await engine.dispose()


@pytest.fixture
def session_factory(engine):
    """Create a session factory for testing."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def db(session_factory):
    """Create a new database session for testing."""
    async with session_factory() as session:
        yield session
        await session.rollback()


# Test cases
class TestBaseModel:
    """Test cases for the base model functionality."""

    async def test_create_model(self, db):
        """Test creating a basic model instance."""
        # Create a test model instance
        test_model = TestSQLModel(name="Test Model", value=42)
        db.add(test_model)
        await db.commit()

        # Verify the model was saved
        assert test_model.id is not None
        assert test_model.name == "Test Model"
        assert test_model.value == 42

        # Verify we can retrieve the model
        result = await db.get(TestSQLModel, test_model.id)
        assert result == test_model

    async def test_uuid_primary_key(self, db):
        """Test model with UUID primary key."""
        test_model = TestSQLUUIDModel(name="UUID Model")
        db.add(test_model)
        await db.commit()

        assert test_model.id is not None
        assert isinstance(test_model.id, str)
        assert len(test_model.id) == 36  # UUID string length

    async def test_timestamps(self, db):
        """Test model with automatic timestamps."""
        test_model = TestSQLTimeStampedModel(name="Timestamped Model")
        db.add(test_model)
        await db.commit()

        assert test_model.created_at is not None
        assert test_model.updated_at is None

        # Update the model and check updated_at
        old_created_at = test_model.created_at
        test_model.name = "Updated Name"
        await db.commit()

        assert test_model.updated_at is not None
        assert test_model.updated_at > test_model.created_at
        assert test_model.updated_at > old_created_at
