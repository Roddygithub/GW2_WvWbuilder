"""
Tests for the get_current_user function in app.api.deps.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from jose import JWTError

# Test data
TEST_USER_ID = 1
TEST_TOKEN = "test_token"


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test retrieving a user with a valid token."""
    # Mock the necessary components
    mock_request = MagicMock()
    mock_db = AsyncMock()

    # Mock the user object
    mock_user = MagicMock()
    mock_user.id = TEST_USER_ID
    mock_user.is_active = True
    mock_user.is_superuser = False

    # Mock the JWT decode function and user_crud.get
    with patch("app.api.deps.jwt.decode") as mock_jwt_decode, patch("app.crud.user_crud.get") as mock_user_get:

        # Configure the mocks
        mock_jwt_decode.return_value = {"sub": str(TEST_USER_ID)}
        mock_user = MagicMock()
        mock_user.id = TEST_USER_ID
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user_get.return_value = mock_user

        # Import the function to test
        from app.api.deps import get_current_user

        # Call the function
        result = await get_current_user(mock_request, TEST_TOKEN, mock_db)

        # Get the actual secret key from settings
        from app.core.config import settings

        # Assertions
        assert result == mock_user
        mock_jwt_decode.assert_called_once_with(
            TEST_TOKEN, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_aud": False}
        )
        mock_user_get.assert_called_once_with(db=mock_db, id=TEST_USER_ID)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test handling of invalid token."""
    # Mock the necessary components
    mock_request = MagicMock()
    mock_db = AsyncMock()

    # Mock the JWT decode function to raise an error
    with patch("app.api.deps.jwt.decode") as mock_jwt_decode, patch("app.crud.user_crud.get"):
        mock_jwt_decode.side_effect = JWTError("Invalid token")

        # Import the function to test
        from app.api.deps import get_current_user, CredentialsException

        # Call the function and expect an exception
        with pytest.raises(CredentialsException) as exc_info:
            await get_current_user(mock_request, "invalid_token", mock_db)

        # Assert the exception details
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)
