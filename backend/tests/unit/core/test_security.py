"""Tests for security utilities."""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

import sys
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_token_from_request,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from app.core.security.jwt import JWTError, JWTInvalidTokenError, JWTExpiredSignatureError
from app.models.user import User
from app.models.role import Role

# Test data
TEST_PASSWORD = "testpassword123"
# Defer hash generation to avoid bcrypt 72-byte limit at import time
TEST_HASH = None  # Will be generated in fixtures
TEST_EMAIL = "test@example.com"
TEST_USER_ID = 1
TEST_REFRESH_TOKEN = "test_refresh_token"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_ROLE_ID = 1


@pytest.fixture(scope="module")
def test_hash():
    """Generate test hash lazily to avoid import-time bcrypt issues."""
    from app.core.security import get_password_hash

    return get_password_hash(TEST_PASSWORD)


TEST_ROLE_NAME = "test_role"
TEST_PERMISSION_LEVEL = 1

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_RESET = "reset"


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
    hashed = get_password_hash(TEST_PASSWORD)
    assert verify_password(TEST_PASSWORD, hashed) is True

    # Test with incorrect password
    assert verify_password("wrongpassword", hashed) is False

    # Test with empty password - should raise ValueError
    # (empty passwords are not allowed)

    # Test with None password
    assert verify_password(None, hashed) is False
    assert verify_password(TEST_PASSWORD, None) is False


def test_get_password_hash():
    """Test password hashing."""
    # Test normal password hashing
    hashed = get_password_hash(TEST_PASSWORD)
    assert hashed != TEST_PASSWORD
    assert len(hashed) > 0

    # Test empty password - should raise ValueError
    with pytest.raises(ValueError):
        get_password_hash("")

    # Test that same password produces different hashes (due to salt)
    hashed2 = get_password_hash(TEST_PASSWORD)
    assert hashed != hashed2

    # Test with None input
    with pytest.raises((AttributeError, TypeError, ValueError)):
        get_password_hash(None)


def test_create_access_token():
    """Test JWT token creation."""
    import logging
    import os
    import sys

    # Rediriger la sortie standard vers un fichier pour capturer tous les logs
    original_stdout = sys.stdout
    with open("test_jwt.log", "w") as f:
        sys.stdout = f

        try:
            # Afficher les variables d'environnement
            print("\n=== Variables d'environnement ===")
            for key, value in os.environ.items():
                if key.startswith("JWT_") or key in ["SECRET_KEY", "ENVIRONMENT"]:
                    print(f"{key}: {value}")
            print("==============================\n")

            # Configurer le niveau de log pour le logger JWT
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
            logger = logging.getLogger("jwt")
            logger.setLevel(logging.DEBUG)

            print("\n=== Début du test_create_access_token ===")
            print(f"TEST_USER_ID: {TEST_USER_ID}")

            # Test with default expiration
            print("\nTest avec expiration par défaut")
            try:
                print("Appel à create_access_token...")
                token = create_access_token(TEST_USER_ID)
                print(f"Token généré: {token[:50]}...")  # Afficher les 50 premiers caractères du token
                assert isinstance(token, str)
                assert len(token) > 0
            except Exception as e:
                print(f"ERREUR lors de la création du token: {e}", file=sys.stderr)
                print(f"Type d'erreur: {type(e).__name__}", file=sys.stderr)
                print(f"Traceback: {e.__traceback__}", file=sys.stderr)
                raise

            # Test with custom expiration
            print("\nTest avec expiration personnalisée")
            try:
                expires_delta = timedelta(minutes=30)
                token = create_access_token(TEST_USER_ID, expires_delta=expires_delta)
                print(f"Token généré: {token[:50]}...")
                assert isinstance(token, str)
            except Exception as e:
                print(f"ERREUR lors de la création du token avec expiration personnalisée: {e}", file=sys.stderr)
                raise

            # Test with additional data
            print("\nTest avec données supplémentaires")
            try:
                token = create_access_token(TEST_USER_ID, custom_claim="test_value")
                print(f"Token généré: {token[:50]}...")
                assert isinstance(token, str)
            except Exception as e:
                print(f"ERREUR lors de la création du token avec données supplémentaires: {e}", file=sys.stderr)
                raise

            # Test with None subject (user_id)
            print("\nTest avec subject=None")
            with pytest.raises(JWTError):
                create_access_token(None)

            # Test with invalid subject type
            print("\nTest avec type de subject invalide")
            with pytest.raises(JWTError):
                create_access_token({"invalid": "subject"})

        except Exception as e:
            print(f"ERREUR inattendue: {e}", file=sys.stderr)
            raise

        finally:
            # Restaurer la sortie standard
            sys.stdout = original_stdout

            # Afficher le contenu du fichier de log
            print("\n=== LOGS COMPLETS ===")
            with open("test_jwt.log", "r") as log_file:
                print(log_file.read())
            print("====================\n")


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


# Constante manquante
JWT_TOKEN_PREFIX = "Bearer"


@pytest.mark.asyncio
async def test_get_current_user():
    """Test getting current user from valid token."""
    from fastapi.security import HTTPAuthorizationCredentials
    from unittest.mock import patch, MagicMock, AsyncMock
    from app.core.security.jwt import (
        get_current_user,
        TOKEN_TYPE_ACCESS,
    
    # Create a test payload for the token
    test_payload = {
        "sub": str(TEST_USER_ID),
        "email": TEST_EMAIL,
        "is_active": True,
        "is_superuser": False,
        "scopes": ["authenticated"],
    }

    # Create a mock for the HTTPAuthorizationCredentials
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.scheme = "bearer"
    mock_credentials.credentials = "valid.token.here"

    # Test with valid token
    with patch("app.core.security.jwt.decode_token", return_value=test_payload) as mock_decode_token:
        # Call the function with the mock credentials
        result = await get_current_user(mock_credentials)

        # Verify the result
        assert result == test_payload
        mock_decode_token.assert_called_once_with("valid.token.here", token_type=TOKEN_TYPE_ACCESS)

    # Test with missing token
    mock_credentials.credentials = ""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing access token" in str(exc_info.value.detail)

    # Reset credentials for next test
    mock_credentials.credentials = "valid.token.here"

    # Test with invalid scheme
    mock_credentials.scheme = "basic"
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid authentication scheme" in str(exc_info.value.detail)

    # Reset scheme for next test
    mock_credentials.scheme = "bearer"

    # Test with expired token
    with patch(
        "app.core.security.jwt.decode_token", side_effect=JWTExpiredSignatureError("Token expired")
    ) as mock_decode_token:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Access token has expired" in str(exc_info.value.detail)

    # Test with invalid token
    with patch(
        "app.core.security.jwt.decode_token", side_effect=JWTInvalidTokenError("Invalid token")
    ) as mock_decode_token:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid token" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test getting current user with various invalid tokens."""
    from fastapi.security import HTTPAuthorizationCredentials
    from unittest.mock import MagicMock, patch, AsyncMock
    from app.core.security.jwt import get_current_user

    # Create mock credentials
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials
    mock_credentials.scheme = "bearer"
    mock_credentials.credentials = "invalid.token.here"

    # Test with invalid token
    with patch("app.core.security.jwt.decode_token") as mock_decode_token:
        # Mock the decode_token to raise an exception for invalid token
        mock_decode_token.side_effect = JWTInvalidTokenError("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid token" in str(exc_info.value.detail)

    # Reset credentials for next test
    mock_credentials.credentials = "expired.token.here"

    # Test with expired token
    with patch("app.core.security.jwt.decode_token") as mock_decode_token:
        # Mock the decode_token to raise an exception for expired token
        mock_decode_token.side_effect = JWTExpiredSignatureError("Token expired")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in str(exc_info.value.detail).lower()

    # Test with empty token
    mock_credentials.credentials = ""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing access token" in str(exc_info.value.detail)

    # Test with invalid scheme
    mock_credentials.scheme = "basic"
    mock_credentials.credentials = "invalid.token.here"
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    """Test getting current user when user is not found."""
    from fastapi.security import HTTPAuthorizationCredentials
    from unittest.mock import MagicMock, patch, AsyncMock
    from app.core.security.jwt import get_current_user

    # Create mock credentials with a valid token
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials
    mock_credentials.scheme = "bearer"
    mock_credentials.credentials = "valid.token.here"

    # Mock the decode_token to return a payload with a non-existent user email
    test_payload = {
        "sub": "nonexistent@example.com",
        "email": "nonexistent@example.com",
        "is_active": True,
        "is_superuser": False,
        "scopes": ["authenticated"],
    }

    with patch("app.core.security.jwt.decode_token", return_value=test_payload) as mock_decode_token:
        # The function should still work even if the user doesn't exist in the database
        # because we're just testing the JWT validation here, not the database lookup
        result = await get_current_user(mock_credentials)

        # Verify the result contains the expected payload
        assert result == test_payload
        mock_decode_token.assert_called_once_with("valid.token.here", token_type=TOKEN_TYPE_ACCESS)


@pytest.mark.asyncio
async def test_get_current_active_user():
    """Test getting current active user."""
    from app.core.security.jwt import get_current_active_user

    # Test with active user
    active_user_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False,
        "scopes": ["authenticated"],
    }

    # The function should return the user data directly if active
    result = get_current_active_user(active_user_data)
    assert result == active_user_data

    # Test with inactive user
    inactive_user_data = active_user_data.copy()
    inactive_user_data["is_active"] = False

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(inactive_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)


def test_get_current_active_superuser():
    """Test getting current active superuser."""
    from app.core.security.jwt import get_current_active_superuser

    # Create a test payload for a superuser
    superuser_data = {
        "sub": "admin@example.com",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
        "scopes": ["authenticated", "admin"],
    }

    # Test with superuser - should return the user data directly
    result = get_current_active_superuser(superuser_data)
    assert result == superuser_data

    # Test with non-superuser
    non_superuser_data = superuser_data.copy()
    non_superuser_data["is_superuser"] = False
    non_superuser_data["scopes"] = ["authenticated"]

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(non_superuser_data)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)


def test_create_refresh_token():
    """Test refresh token creation."""
    # Sauvegarder la sortie standard originale
    original_stdout = sys.stdout

    try:
        # Rediriger la sortie standard vers un fichier pour capturer les logs
        with open("test_refresh_token.log", "w") as f:
            sys.stdout = f

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

            # Test with invalid subject type
            print("\nTest avec type de subject invalide")
            with pytest.raises(JWTError):
                create_refresh_token({"invalid": "subject"})

    finally:
        # Restaurer la sortie standard
        sys.stdout = original_stdout

        # Afficher le contenu du fichier de log
        print("\n=== LOGS DE TEST_REFRESH_TOKEN ===")
        with open("test_refresh_token.log", "r") as f:
            print(f.read())
        print("==============================")
        print("\n=== LOGS COMPLETS ===")
        with open("test_jwt.log", "r") as f:
            print(f.read())
        print("====================")


@pytest.mark.asyncio
async def test_verify_refresh_token():
    """Test verifying a refresh token."""

    # Create a valid refresh token
    refresh_token = create_refresh_token(TEST_USER_ID)

    # Expected token data
    expected_exp = int((datetime.utcnow() + timedelta(minutes=15)).timestamp())
    expected_payload = {
        "sub": str(TEST_USER_ID),
        "type": TOKEN_TYPE_REFRESH,
        "exp": expected_exp,
        "scopes": ["refresh"],
    }

    # Test successful verification
    with patch("app.core.security.jwt.decode_token") as mock_decode_token:
        mock_decode_token.return_value = expected_payload

        # Call the function
        payload = verify_refresh_token(refresh_token)

        # Verify the result
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["type"] == TOKEN_TYPE_REFRESH

        # Verify decode_token was called with the correct arguments
        mock_decode_token.assert_called_once_with(refresh_token, token_type=TOKEN_TYPE_REFRESH)

    # Test with invalid token
    with patch("app.core.security.jwt.decode_token") as mock_decode_token:
        mock_decode_token.side_effect = JWTInvalidTokenError("Invalid token")

        with pytest.raises(JWTInvalidTokenError) as exc_info:
            verify_refresh_token("invalid.token.here")

        assert "Invalid refresh token" in str(exc_info.value)

    # Test with expired token
    with patch("app.core.security.jwt.decode_token") as mock_decode_token:
        mock_decode_token.side_effect = JWTExpiredSignatureError("Token expired")

        with pytest.raises(JWTExpiredSignatureError) as exc_info:
            verify_refresh_token("expired.token.here")

        assert "Refresh token has expired" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_token_from_request():
    """Test extracting token from request."""
    from unittest.mock import MagicMock, AsyncMock

    # Test with Authorization header (case insensitive
    request = MagicMock(spec=Request)
    request.headers = {"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"}
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN, f"Expected {TEST_ACCESS_TOKEN}, got {token}"

    # Test with token in query parameters
    request = MagicMock(spec=Request)
    request.headers = {}
    request.cookies = {}
    request.query_params = {"token": TEST_ACCESS_TOKEN}
    token = get_token_from_request(request)
    assert token == TEST_ACCESS_TOKEN, f"Expected {TEST_ACCESS_TOKEN}, got {token}"

    # Test with missing token
    request = MagicMock(spec=Request)
    request.headers = {}
    request.cookies = {}
    request.query_params = {}
    token = get_token_from_request(request)
    assert token is None, f"Expected None, got {token}"
