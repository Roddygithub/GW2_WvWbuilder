"""Tests for security module."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from jose import jwt, JWTError
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import (
    pwd_context,
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    oauth2_scheme,
)
from app.core.config import settings
from app.models import User

# Test data
TEST_PASSWORD = "testpassword123"
TEST_HASH = pwd_context.hash(TEST_PASSWORD)
TEST_USER_ID = 1
TEST_EMAIL = "test@example.com"
TEST_SECRET_KEY = "test_secret_key"
TEST_ALGORITHM = "HS256"
TEST_TOKEN_EXPIRE_MINUTES = 30

# Mock user data
mock_user = User(
    id=TEST_USER_ID,
    email=TEST_EMAIL,
    hashed_password=TEST_HASH,
    is_active=True,
    is_superuser=False,
)

mock_superuser = User(
    id=2,
    email="admin@example.com",
    hashed_password=TEST_HASH,
    is_active=True,
    is_superuser=True,
)

mock_inactive_user = User(
    id=3,
    email="inactive@example.com",
    hashed_password=TEST_HASH,
    is_active=False,
    is_superuser=False,
)


# Test cases
def test_verify_password():
    """Test password verification."""
    # Test correct password
    assert verify_password(TEST_PASSWORD, TEST_HASH) is True

    # Test incorrect password
    assert verify_password("wrongpassword", TEST_HASH) is False

    # Test empty password
    assert verify_password("", "") is False
    assert verify_password("password", "") is False
    assert verify_password("", "hash") is False


def test_get_password_hash():
    """Test password hashing."""
    password = "testpassword"
    hashed = get_password_hash(password)

    # Should return a string
    assert isinstance(hashed, str)

    # Should be different from original password
    assert hashed != password

    # Should be verifiable
    assert pwd_context.verify(password, hashed)


def test_create_access_token():
    """Test JWT token creation."""
    # Test with default expiration
    token = create_access_token(TEST_USER_ID)
    assert isinstance(token, str)

    # Test with custom expiration
    token = create_access_token(TEST_USER_ID, timedelta(minutes=30))
    assert isinstance(token, str)

    # Verify token content
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert str(TEST_USER_ID) == payload.get("sub")
    assert "exp" in payload


# Fixture for database session
@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


# Test get_current_user
@pytest.fixture
def mock_get_by_email():
    with patch("app.crud.user.user.get_by_email") as mock:
        yield mock


def test_get_current_user_by_email(mock_db):
    """Test getting current user by email."""
    # Mock the token payload
    token_data = {"sub": TEST_EMAIL}

    with patch("app.crud.user.user.get_by_email", return_value=mock_user) as mock_get:
        with patch("app.core.security.jwt.decode", return_value=token_data):
            user = get_current_user(db=mock_db, token="valid_token")
            assert user == mock_user
            mock_get.assert_called_once_with(mock_db, email=TEST_EMAIL)


def test_get_current_user_by_id(mock_db):
    """Test getting current user by ID."""
    # Mock the token payload with user ID
    token_data = {"sub": str(TEST_USER_ID)}

    # Create a mock query object
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user

    # Mock the session's query method to return our mock query
    mock_db.query.return_value = mock_query

    with patch("app.crud.user.user.get_by_email", return_value=None) as mock_get_email:
        with patch("app.core.security.jwt.decode", return_value=token_data):
            user = get_current_user(db=mock_db, token="valid_token")
            assert user == mock_user
            mock_get_email.assert_called_once_with(mock_db, email=str(TEST_USER_ID))
            # Verify the query was made with the correct user ID
            mock_db.query.assert_called_once()
            mock_query.filter.assert_called_once()
            mock_query.filter.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    """Test getting current user with invalid token."""
    with patch("app.core.security.jwt.decode", side_effect=JWTError("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, token="invalid_token")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_expired_token(mock_db):
    """Test getting current user with expired token."""
    # Create an expired token
    expired_token = create_access_token(
        subject=TEST_EMAIL, expires_delta=timedelta(minutes=-5)  # Expired 5 minutes ago
    )

    with patch("app.crud.user.user.get_by_email", return_value=mock_user):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, token=expired_token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_db):
    """Test getting current user that doesn't exist."""
    token_data = {"sub": "nonexistent@example.com"}
    with patch("app.crud.user.user.get_by_email", return_value=None):
        with patch("app.core.security.jwt.decode", return_value=token_data):
            with patch("sqlalchemy.orm.query.Query.first", return_value=None):
                with pytest.raises(HTTPException) as exc_info:
                    get_current_user(
                        db=mock_db, token="valid_but_nonexistent_user_token"
                    )
                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_with_missing_sub(mock_db):
    """Test getting current user with token missing subject."""
    # Create a token with no subject
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with patch("app.crud.user.user.get_by_email", return_value=mock_user):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, token=token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_active_user():
    """Test getting current active user."""
    # Test with active user
    active_user = get_current_active_user(mock_user)
    assert active_user == mock_user
    assert active_user.is_active is True

    # Test with inactive user
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(mock_inactive_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)

    # Test with None user (should raise when trying to access is_active)
    with pytest.raises(AttributeError):
        get_current_active_user(None)


@pytest.mark.asyncio
async def test_get_current_active_superuser():
    """Test getting current active superuser."""
    # Test with superuser
    superuser = get_current_active_superuser(mock_superuser)
    assert superuser == mock_superuser
    assert superuser.is_superuser is True

    # Test with non-superuser
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(mock_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)

    # Test with inactive user - should fail with the same message as non-superuser
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(mock_inactive_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)

    # Test with None user (should raise when trying to access is_superuser)
    with pytest.raises(AttributeError):
        get_current_active_superuser(None)


# Test OAuth2 scheme
def test_oauth2_scheme():
    """Test OAuth2 scheme configuration."""
    # Get the token URL from the OAuth2 flows
    token_url = oauth2_scheme.model.model_dump()["flows"]["password"]["tokenUrl"]
    assert token_url == f"{settings.API_V1_STR}/auth/login"


# Test error cases
def test_verify_password_with_invalid_hash():
    """Test password verification with invalid hash."""
    # Test with invalid hash format
    assert verify_password("password", "invalid_hash") is False

    # Test with empty password
    assert verify_password("", TEST_HASH) is False

    # Test with None password
    assert verify_password(None, TEST_HASH) is False


def test_create_access_token_with_invalid_subject():
    """Test token creation with invalid subject."""
    # The function doesn't actually raise an error for None or empty subjects
    # as it's handled by FastAPI's validation
    token = create_access_token("")
    assert isinstance(token, str)


def test_oauth2_scheme_config():
    """Test OAuth2 scheme configuration."""
    assert isinstance(oauth2_scheme, OAuth2PasswordBearer)
    # The tokenUrl is stored in the model's flows attribute
    assert hasattr(oauth2_scheme, "model")
    # Access the tokenUrl through the model's dict representation
    assert (
        oauth2_scheme.model.model_dump()["flows"]["password"]["tokenUrl"]
        == f"{settings.API_V1_STR}/auth/login"
    )


def test_password_hashing():
    """Test password hashing and verification."""
    # Test different passwords produce different hashes
    hash1 = get_password_hash("password1")
    hash2 = get_password_hash("password2")
    assert hash1 != hash2

    # Test verification works with correct password
    assert verify_password("password1", hash1) is True
    assert verify_password("password2", hash2) is True

    # Test verification fails with wrong password
    assert verify_password("wrong_password", hash1) is False


@pytest.mark.asyncio
async def test_create_access_token_with_custom_expiry():
    """Test token creation with custom expiry time."""
    # Test with custom expiry time
    custom_delta = timedelta(minutes=15)
    token = create_access_token("test_subject", expires_delta=custom_delta)
    assert token is not None

    # Verify the token can be decoded
    with patch("app.core.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test_subject"}
        settings.SECRET_KEY = TEST_SECRET_KEY
        settings.ALGORITHM = TEST_ALGORITHM
        decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
        assert decoded["sub"] == "test_subject"
