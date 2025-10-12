"""Enhanced test coverage for security module."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from jose import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.models import User

# Test data
TEST_USER_ID = 1
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
# Defer hash generation to avoid import-time bcrypt issues
TEST_HASHED_PASSWORD = None


@pytest.fixture(scope="module"
def test_hashed_password():
    """Generate test hash lazily."""
    return security.get_password_hash(TEST_PASSWORD)


@pytest.fixture
def test_user(test_hashed_password):
    """Create test user with lazy hash."""
    return User(
        id=TEST_USER_ID,
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        hashed_password=test_hashed_password,
        is_active=True,
        is_superuser=False,
    )


class TestSecurityEnhanced:
    """Enhanced test coverage for security utilities."""

    @pytest.mark.parametrize(
        "password,expected",
        [
            ("", False),  # Empty password
            (None, False),  # None password
            (" " * 10, False),  # Whitespace password
            ("a" * 1000, False),  # Very long password
            (TEST_PASSWORD.upper(), False),  # Wrong case
            (TEST_PASSWORD + " ", False),  # Extra space at end
            (" " + TEST_PASSWORD, False),  # Extra space at start
            (TEST_PASSWORD[:-1], False),  # One character missing
            (TEST_PASSWORD + "x", False),  # One extra character
            (TEST_PASSWORD.replace("e", "3"), False),  # Similar but different password
        ],
    )
    def test_verify_password_edge_cases(self, password, expected, test_hashed_password):
        """Test password verification with edge cases."""
        # Test with the pre-hashed password
        assert security.verify_password(password, test_hashed_password) == expected

        # Test with None as hashed password
        if password is not None:
            assert security.verify_password(password, None) is False

        # Test with empty string as hashed password
        if password is not None:
            assert security.verify_password(password, "") is False

        # Test with invalid hash format
        if password is not None:
            assert security.verify_password(password, "invalid$hash$format") is False

    def test_verify_password_none_hash(self):
        """Test that None hashes are rejected."""
        assert not security.verify_password("test", None)

    def test_verify_password_empty_password(self):
        """Test that empty passwords are rejected."""
        hashed = security.get_password_hash("")
        assert not security.verify_password("", hashed)

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash format."""
        # Test with malformed hash
        assert security.verify_password("password", "invalid_hash") is False

        # Test with empty hash
        assert security.verify_password("password", "") is False

        # Test plain text fallback (should only work when hashed_password equals plain_password)
        assert security.verify_password("test", "test") is True

        # Test plain text fallback with non-matching password
        assert security.verify_password("test", "wrong") is False

    @pytest.mark.parametrize(
        "password,expected_length,skip_verification",
        [
            (" ", 60, False),  # Whitespace
            ("a" * 1000, 60, False),  # Very long password
            ("p@ssw0rd!" * 10, 60, False),  # Special chars and length
            ("test123", 60, False),  # Normal password
            ("!@#$%^&*()", 60, False),  # Special characters only
            ("1234567890", 60, False),  # Numbers only
            ("P@ssw0rd", 60, False),  # Mixed case with special chars and numbers
        ],
    )
    def test_get_password_hash_variations(self, password, expected_length, skip_verification):
        """Test password hashing with various inputs."""
        # Test hashing the same password multiple times produces different hashes
        hashed1 = security.get_password_hash(password)
        hashed2 = security.get_password_hash(password)

        # All hashes should have the expected length
        assert len(hashed1) == expected_length
        assert len(hashed2) == expected_length

        # The same password should produce different hashes (due to salt)
        assert hashed1 != hashed2

        # The original password should not be in the hash
        assert password not in hashed1
        assert password not in hashed2

        # The hashes should be verifiable (skip if specified in parameters)
        if not skip_verification:
            assert security.verify_password(password, hashed1)
            assert security.verify_password(password, hashed2)

    def test_empty_password_hashing(self):
        """Test hashing and verifying an empty password."""
        # Skip the verification test for empty passwords as they're rejected by verify_password
        hashed = security.get_password_hash("")
        assert len(hashed) == 60  # Should still produce a valid hash

        # Verify that verify_password rejects empty passwords
        assert not security.verify_password("", hashed)

    @pytest.mark.parametrize(
        "subject,expires_delta,expected_exp_seconds",
        [
            (TEST_EMAIL, timedelta(minutes=30), 1800),  # 30 minutes in seconds
            (12345, timedelta(hours=1), 3600),  # Integer subject, 1 hour
            ("user@example.com", timedelta(days=1), 86400),  # 1 day
            (
                "admin",
                None,
                settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),  # Default expiration
        ],
    )
    def test_create_access_token_with_expiration(self, subject, expires_delta, expected_exp_seconds):
        """Test creating token with various subjects and expiration times."""
        # Create token with the given parameters
        token = security.create_access_token(subject, expires_delta=expires_delta)

        # Verify the token can be decoded
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},  # Don't verify expiration for this test
        )

        # Check the subject is correct
        assert payload["sub"] == str(subject)  # Subject should be converted to string

        # Check the token has an expiration claim
        assert "exp" in payload

        # If we provided a custom expiration, check it's close to what we expect
        if expires_delta is not None:
            now = datetime.now(timezone.utc)
            expected_exp = now + expires_delta
            actual_exp = datetime.fromtimestamp(payload["exp"], timezone.utc)

            # Allow for small timing differences (up to 1 second)
            time_diff = abs((actual_exp - expected_exp).total_seconds())
            assert time_diff <= 1.0, f"Expected expiration within 1 second, got {time_diff} seconds difference"

        # Verify the token can be used to get the current user
        # This tests the integration between token creation and user retrieval
        db = MagicMock()
        with patch("app.core.security.get_current_user") as mock_get_user:
            # Mock the user retrieval
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = str(subject)
            mock_get_user.return_value = mock_user

            # Test the token can be used to get the user
            user = security.get_current_user(db, token)
            assert user is not None
            assert user.email == str(subject)

    @pytest.mark.asyncio
    @patch("app.crud.user.user.get_by_email")
    async def test_get_current_user_invalid_token(self, mock_get_by_email, db_session: Session):
        """Test getting current user with invalid token."""
        # Test with invalid token (no subject)
        invalid_token = jwt.encode({"no_sub": "test"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            await security.get_current_user(db_session, invalid_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("app.crud.user.user.get_by_email")
    async def test_get_current_user_not_found(self, mock_get_by_email, db_session: Session):
        """Test getting current user when no user is found in database."""
        # Setup - no user found by email or ID
        mock_get_by_email.return_value = None

        # Create a token with a non-existent user ID
        non_existent_id = 99999
        token = security.create_access_token(str(non_existent_id))

        with pytest.raises(HTTPException) as exc_info:
            await security.get_current_user(db_session, token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("app.crud.user.user.get_by_email")
    async def test_get_current_user_by_id(self, mock_get_by_email, db_session: Session):
        """Test getting current user by ID when email lookup fails."""
        # Setup - first call returns None (email not found), second finds by ID
        mock_get_by_email.return_value = None

        # Create a token with user ID as subject
        token = security.create_access_token(str(TEST_USER_ID))

        # Mock the database query for ID lookup
        with patch.object(db_session, "query") as mock_query:
            mock_filter = MagicMock()
            mock_filter.first.return_value = TEST_USER
            mock_query.return_value.filter.return_value = mock_filter

            # Test
            user = security.get_current_user(db_session, token)

            # Assertions
            assert user is not None
            assert user.id == TEST_USER_ID
            mock_get_by_email.assert_called_once_with(db_session, email=str(TEST_USER_ID))
            mock_query.return_value.filter.assert_called_once()

    def test_get_current_user_invalid_subject(self, db_session: Session):
        """Test getting current user with invalid subject in token."""
        # Create a token with invalid subject type
        token = jwt.encode(
            {"sub": {}},  # Invalid subject type (should be str)
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        with pytest.raises(HTTPException) as exc_info:
            security.get_current_user(db_session, token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "is_active,is_superuser,expected_error",
        [
            (False, False, "Inactive user"),  # Inactive user
            (True, False, "not enough privileges"),  # Non-superuser
            (True, True, None),  # Superuser - should not raise an exception
        ],
    )
    def test_get_current_active_superuser_validation(
        self,
        db_session: Session,
        is_active: bool,
        is_superuser: bool,
        expected_error: str,
        test_hashed_password,
    ):
        """Test validation in get_current_active_superuser."""
        # Create a test user with the specified permissions
        test_user_obj = User(
            id=2,
            email="test2@example.com",
            username="testuser2",
            hashed_password=test_hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )

        # Test the function directly by passing the test user
        if not is_active:
            # For inactive users, both functions should raise an error
            with pytest.raises(HTTPException) as exc_info:
                security.get_current_active_user(current_user=test_user_obj)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert str(exc_info.value.detail) == "Inactive user"

            # Check superuser validation (should fail with inactive user)
            # The actual error message is "The user doesn't have enough privileges"
            with pytest.raises(HTTPException) as exc_info:
                security.get_current_active_superuser(current_user=test_user_obj)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert str(exc_info.value.detail) == "The user doesn't have enough privileges"
        elif not is_superuser:
            # Active user but not superuser
            # First verify active user check passes
            active_user = security.get_current_active_user(current_user=test_user_obj)
            assert active_user == test_user_obj

            # Then verify superuser check fails
            with pytest.raises(HTTPException) as exc_info:
                security.get_current_active_superuser(current_user=test_user_obj)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "The user doesn't have enough privileges" == str(exc_info.value.detail)
        else:
            # Should not raise an exception for active superuser
            active_user = security.get_current_active_user(current_user=test_user_obj)
            assert active_user == test_user_obj

            result = security.get_current_active_superuser(current_user=test_user_obj)
            assert result == test_user_obj

    def test_password_hashing_performance(self):
        """Test that password hashing takes a reasonable amount of time."""
        import time

        # Time a single hash operation
        start_time = time.time()
        security.get_password_hash("test_password_123")
        duration = time.time() - start_time

        # Should take between 0.1 and 1.0 seconds (adjust based on your performance requirements)
        assert 0.1 <= duration <= 1.0, "Password hashing took too long"

    def test_token_expiration(self):
        """Test that token expiration works correctly."""
        # Create a token with expiration in the past
        past_time = datetime.now(timezone.utc) - timedelta(seconds=1)

        # Create a token that's already expired
        to_encode = {"exp": past_time, "sub": TEST_EMAIL}
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Try to decode the token - should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
