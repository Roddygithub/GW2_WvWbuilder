"""Unit tests for authentication and security utilities."""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser
)
from app.core.config import settings
from app.models import User

# Test data
TEST_PASSWORD = "testpassword123"
TEST_HASH = get_password_hash(TEST_PASSWORD)

def test_verify_password():
    """Test password verification."""
    # Test correct password
    assert verify_password(TEST_PASSWORD, TEST_HASH) is True
    
    # Test incorrect password
    assert verify_password("wrongpassword", TEST_HASH) is False

def test_password_hashing():
    """Test that password hashing produces different hashes for the same password."""
    hash1 = get_password_hash(TEST_PASSWORD)
    hash2 = get_password_hash(TEST_PASSWORD)
    
    # Hashes should be different due to random salt
    assert hash1 != hash2
    
    # Both should verify correctly
    assert verify_password(TEST_PASSWORD, hash1) is True
    assert verify_password(TEST_PASSWORD, hash2) is True

def test_create_access_token():
    """Test JWT token creation."""
    # Test data
    user_id = 1
    expires_delta = timedelta(minutes=15)
    
    # Create token
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=expires_delta
    )
    
    # Verify token
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    # Check claims
    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    
    # Check expiration time is approximately correct
    exp_time = datetime.fromtimestamp(payload["exp"])
    expected_time = datetime.utcnow() + expires_delta
    time_diff = (exp_time - expected_time).total_seconds()
    assert abs(time_diff) < 5  # Allow 5 seconds difference for test execution time

@pytest.mark.asyncio
async def test_get_current_user_valid_token(async_db, test_user):
    """Test getting current user with a valid token."""
    # Create a valid token
    token = create_access_token({"sub": str(test_user.id)})
    
    # Get current user
    user = await get_current_user(token=token, db=async_db)
    
    # Verify user
    assert user is not None
    assert user.id == test_user.id
    assert user.username == test_user.username

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(async_db):
    """Test getting current user with an invalid token."""
    # Invalid token
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="invalid_token", db=async_db)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(async_db):
    """Test getting current user that doesn't exist."""
    # Create token for non-existent user
    token = create_access_token({"sub": "9999"})  # Non-existent user ID
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=async_db)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_active_user_active(test_user):
    """Test getting current active user when user is active."""
    test_user.is_active = True
    active_user = await get_current_active_user(test_user)
    
    assert active_user is not None
    assert active_user.id == test_user.id

@pytest.mark.asyncio
async def test_get_current_active_user_inactive(test_user):
    """Test getting current active user when user is inactive."""
    test_user.is_active = False
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(test_user)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_active_superuser_superuser(admin_user):
    """Test getting current active superuser when user is a superuser."""
    admin_user.is_superuser = True
    superuser = await get_current_active_superuser(admin_user)
    
    assert superuser is not None
    assert superuser.id == admin_user.id
    assert superuser.is_superuser is True

@pytest.mark.asyncio
async def test_get_current_active_superuser_not_superuser(test_user):
    """Test getting current active superuser when user is not a superuser."""
    test_user.is_superuser = False
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_superuser(test_user)
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)
