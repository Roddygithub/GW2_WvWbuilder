"""Unit tests for async database operations."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal, async_engine
from app.db.base import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa: F401

@pytest.fixture(scope="module")
async def setup_db():
    """Set up test database with all tables."""
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up after tests
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_async_db_connection(setup_db):
    """Test that the async database connection works."""
    async with AsyncSessionLocal() as session:
        # Test a simple query
        result = await session.execute(select(1))
        value = result.scalar_one()
        assert value == 1

@pytest.mark.asyncio
async def test_async_db_transaction(setup_db):
    """Test basic transaction functionality."""
    test_email = "test-transaction@example.com"
    
    # Create a new session for the test
    async with AsyncSessionLocal() as session:
        # Clean up any existing test user first
        result = await session.execute(select(User).where(User.email == test_email))
        if existing_user := result.scalar_one_or_none():
            await session.delete(existing_user)
            await session.commit()
        
        # Create a new user
        user = User(
            username="testuser_transaction",
            email=test_email,
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        
        # Add and commit the user
        session.add(user)
        await session.commit()
        
        # Verify the user was saved
        result = await session.execute(select(User).where(User.email == test_email))
        saved_user = result.scalar_one_or_none()
        assert saved_user is not None
        assert saved_user.email == test_email
        
        # Clean up
        await session.delete(saved_user)
        await session.commit()
        
        # Verify the user was deleted
        result = await session.execute(select(User).where(User.email == test_email))
        assert result.scalar_one_or_none() is None
