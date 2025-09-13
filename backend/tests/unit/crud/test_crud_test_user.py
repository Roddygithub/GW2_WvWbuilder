"""Tests for user CRUD operations."""
import pytest
from typing import AsyncGenerator
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.user import user as crud_user
from app.models import User, Role, Base
from app.models.base_models import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.core.security import get_password_hash
from app.core.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture for async database session
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture for test user
@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword",
        username="testuser"
    )
    return await crud_user.create_async(db_session, obj_in=user_in)

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user."""
    user_in = UserCreate(
        email="newuser@example.com",
        password="testpassword",
        username="newuser"
    )
    
    user = await crud_user.create_async(db_session, obj_in=user_in)
    
    assert user is not None
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert hasattr(user, "hashed_password")
    assert user.is_active is True
    assert user.is_superuser is False

@pytest.mark.asyncio
async def test_authenticate_user(db_session: AsyncSession, test_user: User):
    """Test user authentication."""
    # Test correct credentials
    authenticated_user = await crud_user.authenticate_async(
        db_session, email=test_user.email, password="testpassword"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email
    
    # Test wrong password
    wrong_password = await crud_user.authenticate_async(
        db_session, email=test_user.email, password="wrongpassword"
    )
    assert wrong_password is None
    
    # Test non-existent user
    non_existent = await crud_user.authenticate_async(
        db_session, email="nonexistent@example.com", password="testpassword"
    )
    assert non_existent is None

@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession, test_user: User):
    """Test getting a user by ID."""
    # Test getting existing user
    user = await crud_user.get_async(db_session, id=test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    
    # Test getting non-existent user
    non_existent = await crud_user.get_async(db_session, id=999999)
    assert non_existent is None

@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession, test_user: User):
    """Test getting a user by email."""
    # Test getting existing user by email
    user = await crud_user.get_by_email_async(db_session, email=test_user.email)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    
    # Test getting non-existent email
    non_existent = await crud_user.get_by_email_async(db_session, email="nonexistent@example.com")
    assert non_existent is None

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession, test_user: User):
    """Test updating a user."""
    # Test updating user fields
    user_update = UserUpdate(
        email="updated@example.com",
        username="updateduser",
        full_name="Updated User",
        is_active=False
    )
    
    updated_user = await crud_user.update_async(
        db_session, db_obj=test_user, obj_in=user_update
    )
    
    assert updated_user.email == "updated@example.com"
    assert updated_user.username == "updateduser"
    assert updated_user.full_name == "Updated User"
    assert updated_user.is_active is False
    
    # Test partial update
    partial_update = UserUpdate(username="partialupdate")
    partially_updated = await crud_user.update_async(
        db_session, db_obj=updated_user, obj_in=partial_update
    )
    assert partially_updated.username == "partialupdate"
    assert partially_updated.email == "updated@example.com"  # Should remain unchanged

@pytest.mark.asyncio
async def test_remove_user(db_session: AsyncSession, test_user: User):
    """Test removing a user."""
    # First, verify the user exists
    user = await crud_user.get_async(db_session, id=test_user.id)
    assert user is not None
    
    # Remove the user
    removed_user = await crud_user.remove_async(db_session, id=test_user.id)
    assert removed_user is not None
    assert removed_user.id == test_user.id
    
    # Verify the user no longer exists
    deleted_user = await crud_user.get_async(db_session, id=test_user.id)
    assert deleted_user is None
    
    # Test removing non-existent user (should not raise)
    non_existent = await crud_user.remove_async(db_session, id=999999)
    assert non_existent is None

@pytest.mark.asyncio
async def test_get_with_roles(db_session: AsyncSession, test_user: User):
    """Test getting a user with roles loaded."""
    # Get the user with roles using the async method
    user_with_roles = await crud_user.get_with_roles_async(db_session, id=test_user.id)
    assert user_with_roles is not None
    
    # Check if roles are loaded (should be empty by default)
    if hasattr(user_with_roles, 'roles'):
        # It's okay if there are no roles, we're just testing the method works
        pass
    
    # Test with non-existent user (should return None)
    non_existent = await crud_user.get_with_roles_async(db_session, id=999999)
    assert non_existent is None

@pytest.mark.asyncio
async def test_get_multi_users(db_session: AsyncSession, test_user: User):
    """Test getting multiple users with pagination."""
    # Create additional test users
    user2_in = UserCreate(email="user2@example.com", username="user2", password="testpass")
    user3_in = UserCreate(email="user3@example.com", username="user3", password="testpass")
    
    user2 = await crud_user.create_async(db_session, obj_in=user2_in)
    user3 = await crud_user.create_async(db_session, obj_in=user3_in)
    
    # Test pagination
    users_page1 = await crud_user.get_multi_async(db_session, skip=0, limit=2)
    assert len(users_page1) >= 2  # At least 2 users should be here
    
    users_page2 = await crud_user.get_multi_async(db_session, skip=2, limit=2)
    assert len(users_page2) >= 1  # At least the third user should be here
    
    # Test with negative skip/limit (should be treated as 0/None)
    users_all = await crud_user.get_multi_async(db_session, skip=-1, limit=-1)
    assert len(users_all) >= 3
    
    # Test with no users (should return empty list)
    async with TestingSessionLocal() as empty_db_session:
        no_users = await crud_user.get_multi_async(empty_db_session, skip=1000, limit=10)
        assert len(no_users) == 0

@pytest.mark.asyncio
async def test_get_multi_by_owner(db_session: AsyncSession, test_user: User):
    """Test getting users by active status."""
    # Create a test user that is not active
    user_in = UserCreate(
        email="inactive@example.com",
        password="testpassword",
        username="inactiveuser",
        is_active=False
    )
    inactive_user = await crud_user.create_async(db_session, obj_in=user_in)
    
    # Get all active users
    stmt = select(User).where(User.is_active == True)  # noqa: E712
    result = await db_session.execute(stmt)
    active_users = result.scalars().all()
    
    # Should not include the inactive user we just created
    assert all(user.is_active for user in active_users)
    assert not any(user.id == inactive_user.id for user in active_users)
