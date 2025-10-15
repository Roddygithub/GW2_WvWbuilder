"""Test API dependencies."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status

from app.api.deps import (
    get_async_db,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)
from app.models import User

# Test data
TEST_USER = User(
    id=1,
    email="test@example.com",
    hashed_password="hashedpassword123",
    is_active=True,
    is_superuser=False,
)


class TestDependencies:
    """Test API dependency injection functions."""

    @pytest.mark.asyncio
    async def test_get_async_db(self, db_session):
        """Test the get_async_db dependency."""
        # Create a generator from the async function
        db_gen = get_async_db()

        # Get the session
        session = await anext(db_gen)

        # Verify it's the same session
        assert session == db_session

        # Verify the session is closed after the request
        with pytest.raises(StopAsyncIteration):
            await anext(db_gen)

        # Verify the session was closed
        db_session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_current_user(self):
        """Test getting the current user from a valid token."""
        # Create a mock token
        token = "valid.token.here"

        # Mock the security.get_current_user function
        with patch(
            "app.api.deps.security.get_current_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = TEST_USER

            # Call the dependency
            result = await get_current_user(token=token)

            # Assertions
            assert result == TEST_USER
            mock_get_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_current_active_user(self):
        """Test getting the current active user."""
        # Mock the get_current_user dependency
        with patch(
            "app.api.deps.get_current_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = TEST_USER

            # Call the dependency
            result = await get_current_active_user(current_user=TEST_USER)

            # Assertions
            assert result == TEST_USER

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """Test getting an inactive user raises an error."""
        # Create an inactive user
        inactive_user = User(
            id=2,
            email="inactive@example.com",
            hashed_password="hashedpassword123",
            is_active=False,
        )

        # Call the dependency with an inactive user
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=inactive_user)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_active_superuser(self):
        """Test getting the current active superuser."""
        # Create a superuser
        superuser = User(
            id=3,
            email="admin@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
            is_superuser=True,
        )

        # Call the dependency with a superuser
        result = await get_current_active_superuser(current_user=superuser)

        # Assertions
        assert result == superuser

    @pytest.mark.asyncio
    async def test_get_current_active_superuser_regular_user(self):
        """Test that a regular user cannot access superuser endpoints."""
        # Call the dependency with a regular user
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_superuser(current_user=TEST_USER)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "The user doesn't have enough privileges" in str(exc_info.value.detail)


# Helper function to use with async generators
async def anext(ait):
    """Get the next item from an async iterator."""
    return await ait.__anext__()
