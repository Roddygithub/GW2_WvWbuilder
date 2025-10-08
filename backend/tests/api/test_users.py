"""
Tests for User and Authentication API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config import settings
from app.models import User
from app.crud import user as user_crud
from app.schemas.user import User
from tests.constants import TestData


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test suite for authentication-related endpoints."""

    async def test_register_user(self, async_client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "new_register_user",
            "email": "new_register@example.com",
            "password": "a_secure_password",
        }
        response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "hashed_password" not in data

    async def test_login_success(self, async_client: AsyncClient, user_factory):
        """Test successful login with valid credentials."""
        user = await user_factory(username="login_user", password="testpassword")
        login_data = {"username": user.username, "password": "testpassword"}

        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login", data=login_data
        )
        assert response.status_code == status.HTTP_200_OK
        token = response.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials fails."""
        login_data = {"username": "nouser", "password": "wrongpassword"}
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login", data=login_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
class TestUserEndpoints:
    """Test suite for user management endpoints."""

    async def test_read_user_me(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test retrieving the current authenticated user's details."""
        user = await user_factory(username="me_user", email="me@example.com")
        headers = await auth_headers(username=user.username, password="testpassword")

        response = await async_client.get(f"{settings.API_V1_STR}/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "me_user"
        assert data["email"] == "me@example.com"

    async def test_read_user_by_id_as_admin(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that an admin can retrieve any user by their ID."""
        user_to_find = await user_factory(username="find_me")
        admin_headers = await auth_headers(username="admin_reader", is_superuser=True)

        response = await async_client.get(f"{settings.API_V1_STR}/users/{user_to_find.id}", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "find_me"

    async def test_read_nonexistent_user_as_admin(self, async_client: AsyncClient, auth_headers):
        """Test that an admin cannot retrieve a non-existent user by ID."""
        admin_headers = await auth_headers(username="admin_reader_nonexistent", is_superuser=True)

        response = await async_client.get(f"{settings.API_V1_STR}/users/999999", headers=admin_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()

    async def test_read_user_by_id_forbidden_for_normal_user(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that a normal user cannot retrieve another user by ID."""
        user_to_find = await user_factory(username="hidden_user")
        normal_user_headers = await auth_headers(username="normal_user")

        response = await async_client.get(f"{settings.API_V1_STR}/users/{user_to_find.id}", headers=normal_user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_user_me(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that a user can update their own information."""
        user = await user_factory(username="updater_user")
        headers = await auth_headers(username=user.username, password="testpassword")
        update_data = {"full_name": "A New Full Name"}

        response = await async_client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "A New Full Name"

    async def test_admin_update_other_user(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that an admin can update another user's information."""
        user_to_update = await user_factory(username="user_to_be_updated")
        admin_headers = await auth_headers(username="admin_updater", is_superuser=True)
        update_data = {"is_active": False}

        response = await async_client.put(f"{settings.API_V1_STR}/users/{user_to_update.id}", json=update_data, headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is False

    async def test_admin_update_nonexistent_user(self, async_client: AsyncClient, auth_headers):
        """Test that an admin cannot update a non-existent user."""
        admin_headers = await auth_headers(username="admin_updater_nonexistent", is_superuser=True)
        update_data = {"is_active": False}

        response = await async_client.put(f"{settings.API_V1_STR}/users/999999", json=update_data, headers=admin_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()

    async def test_normal_user_cannot_update_other_user(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that a normal user cannot update another user's information."""
        user_to_update = await user_factory(username="protected_user")
        normal_user_headers = await auth_headers(username="attacker_user")
        update_data = {"is_superuser": True} # Malicious attempt

        response = await async_client.put(f"{settings.API_V1_STR}/users/{user_to_update.id}", json=update_data, headers=normal_user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_read_users_as_admin(self, async_client: AsyncClient, user_factory, auth_headers):
        """Test that an admin can list all users."""
        await user_factory(username="user1_list")
        await user_factory(username="user2_list")
        admin_headers = await auth_headers(username="admin_lister", is_superuser=True)

        response = await async_client.get(f"{settings.API_V1_STR}/users/", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3 # The two created users + the admin