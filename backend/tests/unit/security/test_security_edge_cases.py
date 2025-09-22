"""Additional test cases for security module focusing on edge cases and error conditions."""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status

from app.core import security

# Reuse test data from test_security.py
TEST_EMAIL = "test@example.com"
TEST_HASHED_PASSWORD = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hash of "testpassword123"


# Mock the get_db dependency
def mock_get_db():
    return MagicMock()


class TestSecurityEdgeCases:
    """Test edge cases and error conditions in the security module."""

    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        # Both empty
        assert security.verify_password("", "") is False

        # Empty password
        assert security.verify_password("", TEST_HASHED_PASSWORD) is False

        # Empty hash
        assert security.verify_password("password", "") is False

    def test_verify_password_invalid_hash(self):
        """Test password verification with an invalid hash format."""
        # Malformed hash
        assert security.verify_password("password", "invalid$hash") is False

        # Hash with invalid format
        assert security.verify_password("password", "$invalid$format") is False

    def test_create_access_token_with_none_subject(self):
        """Test token creation with None as subject."""
        # The function actually accepts None as subject
        token = security.create_access_token(None)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_empty_subject(self):
        """Test token creation with empty string as subject."""
        token = security.create_access_token("")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_get_current_user_with_numeric_subject(self, db_session):
        """Test getting user with numeric subject (user ID)."""
        # Setup test user in the database
        from app.models import User as UserModel

        # Create a test user
        test_user = UserModel(
            id=123,
            email="user@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            is_active=True,
            username="testuser",
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a valid JWT token for the test user
        token = security.create_access_token(subject=str(test_user.id))

        # Test getting the current user with the token
        user = security.get_current_user(db_session, token)

        # Assert the correct user was returned
        assert user is not None
        assert user.id == 123
        assert user.email == "user@example.com"

    def test_get_current_user_with_expired_token(self, db_session):
        """Test getting user with an expired token."""
        # Create an expired token (1 second in the past)
        expired_token = security.create_access_token(
            TEST_EMAIL, expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(HTTPException) as exc_info:
            security.get_current_user(db_session, expired_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_invalid_token(self, db_session):
        """Test handling of invalid JWT tokens."""
        # Test with an invalid token format
        with pytest.raises(HTTPException) as exc_info:
            security.get_current_user(db_session, "invalid.token.here")

        # Assert the exception has the correct status code and message
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_get_current_active_user_with_none(self):
        """Test get_current_active_user with None user."""
        # The function is a FastAPI dependency that expects to be called by FastAPI
        # which would inject the current_user. We need to test it differently.

        # Mock the FastAPI dependency injection
        async def mock_dep():
            return None

        # The actual function is a dependency, so we need to test it differently
        # by calling it directly with None
        with pytest.raises(AttributeError):
            security.get_current_active_user(None)

    def test_get_current_active_superuser_with_none(self):
        """Test get_current_active_superuser with None user."""
        # The function is a FastAPI dependency that expects to be called by FastAPI
        # which would inject the current_user. We need to test it differently.
        with pytest.raises(AttributeError):
            security.get_current_active_superuser(None)

    @patch("app.core.security.pwd_context.verify")
    def test_verify_password_exception_handling(self, mock_verify):
        """Test exception handling in verify_password."""
        # Setup mock to raise an exception
        mock_verify.side_effect = Exception("Test exception")

        # Should handle the exception and return False
        assert security.verify_password("password", TEST_HASHED_PASSWORD) is False

        # Verify the mock was called
        mock_verify.assert_called_once()

    def test_oauth2_scheme_initialization(self):
        """Test that the OAuth2 scheme is initialized correctly."""
        from fastapi.security.oauth2 import OAuth2PasswordBearer

        assert security.oauth2_scheme is not None
        assert isinstance(security.oauth2_scheme, OAuth2PasswordBearer)

        # The tokenUrl is a property that returns the URL
        token_url = security.oauth2_scheme.model.model_dump()["flows"]["password"][
            "tokenUrl"
        ]
        assert token_url.endswith("/auth/login")
