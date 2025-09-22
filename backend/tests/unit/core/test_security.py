"""Tests for security utilities."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from jose import JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    pwd_context,
    get_password_hash_sha256,
    create_refresh_token,
    verify_refresh_token,
    get_token_from_request,
)
from app.models import User, Role
from app.models.association_tables import user_roles
from app.core.exceptions import InactiveUserException, UnauthorizedException

# Test data
TEST_PASSWORD = "testpassword123"
TEST_HASH = pwd_context.hash(TEST_PASSWORD)
TEST_EMAIL = "test@example.com"
TEST_USER_ID = 1
TEST_REFRESH_TOKEN = "test_refresh_token"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_ROLE_ID = 1
TEST_ROLE_NAME = "test_role"
TEST_PERMISSION_LEVEL = 1


# Fixtures
@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id=TEST_USER_ID,
        email=TEST_EMAIL,
        hashed_password=TEST_HASH,
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_role():
    """Create a mock role for testing."""
    return Role(
        id=TEST_ROLE_ID,
        name=TEST_ROLE_NAME,
        permission_level=TEST_PERMISSION_LEVEL,
        is_default=True,
    )


@pytest.fixture
def mock_user_role(mock_user, mock_role):
    """Create a mock user-role relationship for testing."""
    # Simuler une relation many-to-many avec une liste de rôles
    mock_user.roles = [mock_role]
    return mock_user, mock_role


# Tests
def test_verify_password():
    """Test password verification."""
    # Test with correct password
    hashed = pwd_context.hash(TEST_PASSWORD)
    assert verify_password(TEST_PASSWORD, hashed) is True

    # Test with incorrect password
    assert verify_password("wrongpassword", hashed) is False

    # Test with empty password
    empty_hash = pwd_context.hash("")
    assert verify_password("", empty_hash) is True

    # Test with None password
    assert verify_password(None, hashed) is False
    assert verify_password(TEST_PASSWORD, None) is False


def test_get_password_hash():
    """Test password hashing."""
    # Test normal password hashing
    hashed = pwd_context.hash(TEST_PASSWORD)
    assert hashed != TEST_PASSWORD
    assert len(hashed) > 0

    # Test empty password
    empty_hash = pwd_context.hash("")
    assert empty_hash is not None
    assert len(empty_hash) > 0

    # Test that same password produces different hashes (due to salt)
    hashed2 = pwd_context.hash(TEST_PASSWORD)
    assert hashed != hashed2

    # Test with None input
    with pytest.raises((AttributeError, TypeError)):
        pwd_context.hash(None)


def test_create_access_token():
    """Test JWT token creation."""
    # Test with default expiration
    token = create_access_token(TEST_USER_ID)
    assert isinstance(token, str)
    assert len(token) > 0

    # Test with custom expiration
    expires_delta = timedelta(minutes=30)
    token = create_access_token(TEST_USER_ID, expires_delta=expires_delta)
    assert isinstance(token, str)

    # Test with additional data
    token = create_access_token(TEST_USER_ID, custom_claim="test_value")
    assert isinstance(token, str)

    # Test with None subject (user_id)
    with pytest.raises((TypeError, ValueError)):
        create_access_token(None)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.mark.asyncio
async def test_get_current_user(mock_user, mock_db_session, mock_role, mock_user_role):
    """Test getting current user from valid token."""
    # Create a valid token with user ID as subject
    token = create_access_token(TEST_USER_ID)

    # Set up mock user with roles
    mock_user.roles = [mock_role]

    # Mock the user retrieval
    mock_crud = MagicMock()
    mock_crud.user.get_by_email = MagicMock(return_value=None)
    mock_crud.user.get = MagicMock(return_value=mock_user)

    # Mock the database query for user
    mock_user_query = MagicMock()
    mock_user_query.filter.return_value.first.return_value = mock_user

    # Mock the database query for roles
    mock_role_query = MagicMock()
    mock_role_query.join.return_value.filter.return_value.all.return_value = [mock_role]

    # Set up the session to return different queries based on the model
    def query_side_effect(model, *args, **kwargs):
        if model == User:
            return mock_user_query
        elif model == Role:
            return mock_role_query
        return MagicMock()

    mock_db_session.query.side_effect = query_side_effect

    # Patch the dependencies
    with (
        patch("app.core.security.crud", mock_crud),
        patch("app.core.security.get_db", return_value=mock_db_session),
    ):

        # Call the function directly with the token
        user = get_current_user(db=mock_db_session, token=token)

    # Verify the results
    assert user.id == TEST_USER_ID
    assert user.email == TEST_EMAIL
    assert len(user.roles) == 1
    assert user.roles[0].name == TEST_ROLE_NAME
    mock_crud.user.get_by_email.assert_called_once_with(
        mock_db_session, email=str(TEST_USER_ID)
    )


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db_session):
    """Test getting current user with various invalid tokens."""
    # Test with malformed token
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db_session, token="invalid.token.here")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with empty token
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db_session, token="")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with None token
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db_session, token=None)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with JWT decode error
    with patch("app.core.security.jwt.decode", side_effect=JWTError("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db=mock_db_session, token="invalid.token.here")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with expired token
    with patch(
        "app.core.security.jwt.decode",
        side_effect=ExpiredSignatureError("Token expired"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db=mock_db_session, token="expired.token.here")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_db_session):
    """Test getting current user when user is not found."""
    # Create a valid token
    token = create_access_token(TEST_USER_ID)

    # Test with user not found by email or ID
    mock_crud = MagicMock()
    mock_crud.user.get_by_email = MagicMock(return_value=None)
    mock_crud.user.get = MagicMock(return_value=None)

    # Mock the database query to return None
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query

    # Patch the dependencies
    with (
        patch("app.core.security.crud", mock_crud),
        patch("app.core.security.get_db", return_value=mock_db_session),
    ):

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db=mock_db_session, token=token)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in str(exc_info.value.detail)

    # Verify that both get_by_email and get were called
    mock_crud.user.get_by_email.assert_called_once_with(
        mock_db_session, email=str(TEST_USER_ID)
    )
    mock_crud.user.get.assert_called_once_with(mock_db_session, id=TEST_USER_ID)


def test_get_current_active_user(mock_user):
    """Test getting current active user."""
    # Test with active user
    active_user = get_current_active_user(mock_user)
    assert active_user == mock_user

    # Test with inactive user
    mock_user.is_active = False
    with pytest.raises(InactiveUserException) as exc_info:
        get_current_active_user(mock_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)

    # Test with None user
    with pytest.raises(ValueError):
        get_current_active_user(None)


def test_get_current_active_superuser(mock_user):
    """Test getting current active superuser."""
    # Set up a superuser
    mock_user.is_superuser = True

    # Call the function with our mock dependency
    superuser = get_current_active_superuser(current_user=mock_user)
    assert superuser == mock_user


def test_get_current_active_superuser_not_superuser(mock_user):
    """Test getting current active superuser when user is not a superuser."""
    mock_user.is_superuser = False

    with pytest.raises(UnauthorizedException) as exc_info:
        get_current_active_superuser(mock_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not enough permissions" in str(exc_info.value.detail)


# New test functions for additional security utilities


def test_get_password_hash_sha256():
    """Test SHA-256 password hashing."""
    # Test with normal password
    hashed = get_password_hash_sha256(TEST_PASSWORD)
    assert hashed != TEST_PASSWORD
    assert len(hashed) == 64  # SHA-256 produces 64 character hex string

    # Test with empty password
    empty_hash = get_password_hash_sha256("")
    assert (
        empty_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )  # SHA-256 of empty string

    # Test with None input
    with pytest.raises(AttributeError):
        get_password_hash_sha256(None)


def test_create_refresh_token():
    """Test refresh token creation."""
    # Test with default expiration
    token = create_refresh_token(TEST_USER_ID)
    assert isinstance(token, str)
    assert len(token) > 0

    # Test with custom expiration
    expires_delta = timedelta(days=30)
    token = create_refresh_token(TEST_USER_ID, expires_delta=expires_delta)
    assert isinstance(token, str)

    # Test with additional data
    token = create_refresh_token(TEST_USER_ID, custom_claim="test_value")
    assert isinstance(token, str)

    # Test with None subject (user_id)
    with pytest.raises((TypeError, ValueError)):
        create_refresh_token(None)


def test_verify_refresh_token():
    """Test refresh token verification."""
    # Create a valid refresh token
    token = create_refresh_token(TEST_USER_ID)

    # Test valid token
    with patch("app.core.security.jwt.decode") as mock_decode, \
         patch("app.core.security.TokenPayload") as mock_token_payload:
        # Mock the token decoding
        mock_decode.return_value = {"sub": str(TEST_USER_ID), "exp": (datetime.now(timezone.utc) + timedelta(days=1)).timestamp()}
        # Mock the TokenPayload to return a simple dict with exp as datetime
        mock_token_payload.return_value.dict.return_value = {
            "sub": str(TEST_USER_ID),
            "exp": datetime.now(timezone.utc) + timedelta(days=1)
        }
        token_data = verify_refresh_token(token)
        assert token_data["sub"] == str(TEST_USER_ID)

    # Test invalid token
    with patch("app.core.security.jwt.decode", side_effect=JWTError("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token("invalid.token.here")
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Impossible de valider les informations d'identification" in str(exc_info.value.detail)

    # Test expired token
    with patch("app.core.security.jwt.decode") as mock_decode, \
         patch("app.core.security.TokenPayload") as mock_token_payload:
        # Mock an expired token
        mock_decode.return_value = {"sub": str(TEST_USER_ID), "exp": (datetime.now(timezone.utc) - timedelta(days=1)).timestamp()}
        # Mock the TokenPayload to return an expired datetime
        mock_token_payload.return_value.dict.return_value = {
            "sub": str(TEST_USER_ID),
            "exp": datetime.now(timezone.utc) - timedelta(days=1)
        }
        # Mock the exp attribute directly on the instance
        mock_token_payload.return_value.exp = datetime.now(timezone.utc) - timedelta(days=1)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token("expired.token.here")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token expiré" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_token_from_request():
    """Test extracting token from request."""
    # Test with Authorization header (lowercase)
    class Headers(dict):
        def get(self, key, default=None):
            # Convertir la clé en minuscules pour une correspondance insensible à la casse
            key_lower = key.lower()
            for k, v in self.items():
                if k.lower() == key_lower:
                    return v
            return default
    
    request = MagicMock(spec=Request)
    # Créer un objet headers personnalisé
    headers = Headers()
    headers["authorization"] = f"Bearer {TEST_ACCESS_TOKEN}"
    request.headers = headers
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN, f"Expected {TEST_ACCESS_TOKEN}, got {token}"

    # Test with Authorization header (uppercase)
    request = MagicMock(spec=Request)
    # Créer un objet headers personnalisé
    headers = Headers()
    headers["Authorization"] = f"Bearer {TEST_ACCESS_TOKEN}"
    request.headers = headers
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN, f"Expected {TEST_ACCESS_TOKEN}, got {token}"

    # Test with cookie - version simplifiée
    request = MagicMock(spec=Request)
    request.headers = {}
    # Créer un objet cookies personnalisé avec une méthode get
    class Cookies(dict):
        def get(self, key, default=None):
            # Utiliser super().get() pour éviter la récursion
            return super().get(key, default)
    
    cookies = Cookies()
    cookies["access_token"] = TEST_ACCESS_TOKEN
    request.cookies = cookies
    request.query_params = {}
    
    # Appeler la fonction et vérifier le résultat
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN, f"Expected {TEST_ACCESS_TOKEN}, got {token}"

    # Test with query parameter
    request = MagicMock(spec=Request)
    request.headers = {}
    request.cookies = {}
    request.query_params = {"token": TEST_ACCESS_TOKEN}
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN

    # Test with missing token
    request = MagicMock(spec=Request)
    request.headers = {}
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token is None

    # Test with malformed Authorization header
    request = MagicMock(spec=Request)
    request.headers = {"authorization": "InvalidToken"}
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token is None

    # Test with empty token in Authorization header
    request = MagicMock(spec=Request)
    request.headers = {"authorization": "Bearer "}
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token == ""  # Empty string is returned for "Bearer "
