"""Tests for edge cases in user CRUD operations."""
import pytest
from typing import AsyncGenerator
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, text
from fastapi import HTTPException

from app.crud.user import user as crud_user
from app.models import User, Base
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword",
        username="testuser"
    )
    return await crud_user.create_async(db_session, obj_in=user_in)

async def test_create_user_with_existing_email(db_session: AsyncSession, test_user: User):
    """Test creating a user with an existing email should raise an error."""
    user_in = UserCreate(
        email=test_user.email,  # Duplicate email
        password="newpassword",
        username="newuser"
    )
    
    with pytest.raises(Exception):  # Should raise IntegrityError
        await crud_user.create_async(db_session, obj_in=user_in)

async def test_create_user_with_invalid_email(db_session: AsyncSession):
    """Test creating a user with an invalid email format."""
    # Pydantic's email validation is more permissive, so we'll test with an empty email
    with pytest.raises(ValueError):
        UserCreate(
            email="",  # Empty email should be invalid
            password="testpassword",
            username="testuser"
        )

async def test_update_user_with_existing_email(db_session: AsyncSession, test_user: User):
    """Test updating a user with an email that already exists."""
    # Create a second user
    user2_in = UserCreate(
        email="another@example.com",
        password="testpassword",
        username="anotheruser"
    )
    user2 = await crud_user.create_async(db_session, obj_in=user2_in)
    
    # Try to update user2's email to test_user's email
    with pytest.raises(Exception):  # Should raise IntegrityError
        await crud_user.update_async(
            db_session, 
            db_obj=user2, 
            obj_in=UserUpdate(email=test_user.email)
        )

async def test_authenticate_nonexistent_user(db_session: AsyncSession):
    """Test authenticating a non-existent user."""
    user = await crud_user.authenticate_async(
        db_session, 
        email="nonexistent@example.com", 
        password="password"
    )
    assert user is None

async def test_authenticate_with_wrong_password(db_session: AsyncSession, test_user: User):
    """Test authenticating with wrong password."""
    user = await crud_user.authenticate_async(
        db_session, 
        email=test_user.email, 
        password="wrongpassword"
    )
    assert user is None

async def test_get_nonexistent_user(db_session: AsyncSession):
    """Test getting a user that doesn't exist."""
    user = await crud_user.get_async(db_session, id=999999)
    assert user is None

async def test_update_user_with_invalid_data(db_session: AsyncSession, test_user: User):
    """Test updating a user with invalid data."""
    with pytest.raises(ValueError):
        await crud_user.update_async(
            db_session,
            db_obj=test_user,
            obj_in=UserUpdate(email="invalid-email")
        )

async def test_remove_nonexistent_user(db_session: AsyncSession):
    """Test removing a user that doesn't exist."""
    user = await crud_user.remove_async(db_session, id=999999)
    assert user is None

async def test_get_multi_with_pagination(db_session: AsyncSession, test_user: User):
    """Test getting users with pagination."""
    # Create additional test users
    for i in range(1, 6):
        user_in = UserCreate(
            email=f"user{i}@example.com",
            password=f"password{i}",
            username=f"user{i}"
        )
        await crud_user.create_async(db_session, obj_in=user_in)
    
    # Get first page (2 users)
    users_page1 = await crud_user.get_multi_async(db_session, skip=0, limit=2)
    assert len(users_page1) == 2
    
    # Get second page (2 users)
    users_page2 = await crud_user.get_multi_async(db_session, skip=2, limit=2)
    assert len(users_page2) == 2
    
    # Verify different pages return different users
    assert users_page1[0].id != users_page2[0].id

async def test_get_user_by_email_nonexistent(db_session: AsyncSession):
    """Test getting a user by a non-existent email."""
    user = await crud_user.get_by_email_async(db_session, email="nonexistent@example.com")
    assert user is None
