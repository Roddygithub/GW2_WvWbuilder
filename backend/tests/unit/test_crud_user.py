"""Tests for user CRUD operations."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.security import get_password_hash
from tests.utils.utils import random_email, random_lower_string


def test_get_user(db: Session) -> None:
    """Test retrieving a user by ID."""
    # Create test user data
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Retrieve the user
    stored_user = crud.user.get(db, id=user.id)
    
    # Assertions
    assert stored_user
    assert user.id == stored_user.id
    assert user.email == stored_user.email
    assert stored_user.hashed_password is not None
    assert not stored_user.is_superuser


@pytest.mark.asyncio
async def test_get_user_async(async_db: AsyncSession) -> None:
    """Test retrieving a user by ID asynchronously."""
    # Create test user data
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = await crud.user.create_async(async_db, obj_in=user_in)
    
    # Retrieve the user
    stored_user = await crud.user.get_async(async_db, id=user.id)
    
    # Assertions
    assert stored_user
    assert user.id == stored_user.id
    assert user.email == stored_user.email
    assert stored_user.hashed_password is not None
    assert not stored_user.is_superuser


def test_get_user_by_email(db: Session) -> None:
    """Test retrieving a user by email."""
    # Create test user data
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Retrieve the user by email
    stored_user = crud.user.get_by_email(db, email=email)
    
    # Assertions
    assert stored_user
    assert user.id == stored_user.id
    assert user.email == stored_user.email


def test_create_user(db: Session) -> None:
    """Test creating a new user."""
    # Create test user data
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    full_name = "Test User"
    
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name
    )
    
    # Create the user
    user = crud.user.create(db, obj_in=user_in)
    
    # Assertions
    assert user.email == email
    assert hasattr(user, "hashed_password")
    assert not hasattr(user, "password")  # Password should be hashed and stored in hashed_password
    assert user.full_name == full_name
    assert user.is_active is True
    assert user.is_superuser is False


def test_authenticate_user(db: Session) -> None:
    """Test authenticating a user."""
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Test authentication
    authenticated_user = crud.user.authenticate(db, email=email, password=password)
    
    # Assertions
    assert authenticated_user
    assert user.id == authenticated_user.id
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    """Test failed authentication with wrong password."""
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    crud.user.create(db, obj_in=user_in)
    
    # Test authentication with wrong password
    user = crud.user.authenticate(db, email=email, password="wrongpassword")
    
    # Assertions
    assert user is None


def test_check_if_user_is_superuser(db: Session) -> None:
    """Test checking if a user is a superuser."""
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test Admin",
        is_superuser=True
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Check if user is superuser
    is_superuser = crud.user.is_superuser(user)
    
    # Assertions
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    """Test checking if a normal user is not a superuser."""
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Check if user is superuser
    is_superuser = crud.user.is_superuser(user)
    
    # Assertions
    assert is_superuser is False


def test_get_multi_users(db: Session) -> None:
    """Test retrieving multiple users with pagination."""
    # Create test users
    for _ in range(5):
        email = random_email()
        username = random_lower_string()
        password = random_lower_string()
        user_in = schemas.UserCreate(
            email=email,
            username=username,
            password=password,
            full_name="Test User"
        )
        crud.user.create(db, obj_in=user_in)
    
    # Get users with pagination
    users = crud.user.get_multi(db, skip=0, limit=3)
    
    # Assertions
    assert len(users) == 3
    
    # Get next page
    users = crud.user.get_multi(db, skip=3, limit=3)
    
    # Assertions
    assert len(users) == 2  # Only 2 more users should be left


def test_update_user(db: Session) -> None:
    """Test updating a user."""
    # Create a test user
    password = random_lower_string()
    username = random_lower_string()
    email = random_email()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Original Name"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Update the user
    new_email = random_email()
    new_full_name = "Updated Name"
    user_update = schemas.UserUpdate(
        email=new_email,
        full_name=new_full_name
    )
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
    
    # Assertions
    assert updated_user.id == user.id
    assert updated_user.email == new_email
    assert updated_user.full_name == new_full_name


def test_remove_user(db: Session) -> None:
    """Test removing a user."""
    # Create test user data
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="User to be removed"
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Remove the user
    removed_user = crud.user.remove(db, id=user.id)
    
    # Try to retrieve the removed user
    db_user = crud.user.get(db, id=user.id)
    
    # Assertions
    assert removed_user.id == user.id
    assert db_user is None
