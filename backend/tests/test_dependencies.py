"""Tests for FastAPI dependencies."""

import pytest
from fastapi import HTTPException, Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import User

# Test app for dependency injection
app = FastAPI()


# Test routes that use our dependencies
@app.get("/test/current-user")
async def test_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/test/active-user")
async def test_active_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@pytest.mark.asyncio
async def test_get_current_user(test_user: User):
    """Test getting the current user from a valid token."""
    # Create a valid token for the test user
    token = create_access_token({"sub": str(test_user.id)})

    # Call the dependency directly
    user = await get_current_user(token=token)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test that an invalid token raises an exception."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="invalid_token")

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    """Test that a missing token raises an exception."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=None)

    assert exc_info.value.status_code == 401
    assert "Not authenticated" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_active_user(test_user: User):
    """Test getting an active user."""
    # Create a token for the test user
    token = create_access_token({"sub": str(test_user.id)})

    # First get the current user
    current_user = await get_current_user(token=token)

    # Then verify they're active
    active_user = await get_current_active_user(current_user=current_user)

    assert active_user is not None
    assert active_user.id == test_user.id
    assert active_user.is_active is True


@pytest.mark.asyncio
async def test_get_current_active_user_inactive(inactive_user: User):
    """Test that an inactive user is rejected."""
    # Create a token for an inactive user
    token = create_access_token({"sub": str(inactive_user.id)})

    # First get the current user
    current_user = await get_current_user(token=token)

    # Should raise an exception when checking if active
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=current_user)

    assert exc_info.value.status_code == 400
    assert "Inactive user" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_active_superuser(test_user: User, superuser: User):
    """Test that only superusers can access superuser endpoints."""
    # Regular user should be rejected
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_superuser(current_user=test_user)

    assert exc_info.value.status_code == 403
    assert "Not enough permissions" in str(exc_info.value.detail)

    # Superuser should be allowed
    superuser = await get_current_active_superuser(current_user=superuser)
    assert superuser is not None
    assert superuser.is_superuser is True


@pytest.mark.asyncio
async def test_get_db():
    """Test that we can get a database session."""
    # This is a generator, so we need to get the first (and only) result
    db_gen = get_db()

    try:
        # Get the session
        db = await anext(db_gen)

        # Should be an async session
        assert isinstance(db, AsyncSession)

        # Should be able to execute a simple query
        result = await db.execute("SELECT 1")
        assert result.scalar() == 1

    finally:
        # Make sure to clean up
        try:
            await anext(db_gen)
        except StopAsyncIteration:
            pass


# Test the dependencies through the FastAPI app
client = TestClient(app)


@pytest.mark.asyncio
async def test_dependency_integration(test_token: str, test_user: User):
    """Test that dependencies work correctly in a FastAPI app."""
    # Test with valid token
    response = client.get("/test/current-user", headers={"Authorization": f"Bearer {test_token}"})

    assert response.status_code == 200
    assert response.json()["id"] == test_user.id

    # Test with invalid token
    response = client.get("/test/current-user", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401
    assert "Could not validate credentials" in response.text
