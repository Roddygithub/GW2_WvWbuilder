"""Tests for the Users API endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select

from app.models import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    """Test user registration."""
    # Test data
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "testpassword123",
        "full_name": "New User",
    }

    # Make request
    response = await client.post("/api/v1/auth/register", json=user_data)

    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # Password should never be returned

    # Verify user was created in database
    result = await db_session.execute(select(User).filter_by(username="newuser"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "newuser@example.com"
    assert user.is_active is True
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    """Test user login and token generation."""
    # Test data
    login_data = {
        "username": test_user.username,
        "password": "testpassword",  # Default password from test_user fixture
    }

    # Make request
    response = await client.post("/api/v1/auth/login", data=login_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["id"] == test_user.id
    assert data["user"]["username"] == test_user.username


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, test_token):
    """Test retrieving the current authenticated user."""
    # Make request
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {test_token}"}
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient, test_user, test_token):
    """Test updating the current user's information."""
    # Update data
    update_data = {"full_name": "Updated Name", "email": "updated@example.com"}

    # Make request
    response = await client.patch(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"

    # Verify database was updated
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {test_token}"}
    )
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user, test_token, db_session):
    """Test changing the current user's password."""
    # Get current password hash
    result = await db_session.execute(select(User).filter_by(id=test_user.id))
    old_hashed_password = result.scalar_one().hashed_password

    # Change password
    response = await client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK

    # Verify password was changed
    await db_session.refresh(test_user)
    assert test_user.hashed_password != old_hashed_password

    # Verify login with new password works
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user.username, "password": "newsecurepassword123"},
    )
    assert login_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_admin_get_users(client: AsyncClient, admin_user, admin_token):
    """Test that admin can list all users."""
    # Make request as admin
    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1  # At least the admin user
    assert any(user["username"] == admin_user.username for user in users)


@pytest.mark.asyncio
async def test_admin_update_user(client: AsyncClient, test_user, admin_token):
    """Test that admin can update any user."""
    # Update data
    update_data = {"is_active": False, "is_superuser": True}

    # Make request as admin
    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False
    assert data["is_superuser"] is True
