"""Integration tests for the users API endpoints."""

import pytest
import pytest_asyncio
from typing import Callable
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

pytestmark = pytest.mark.asyncio


class TestUserApi:
    """Test suite for user management API endpoints."""

    @pytest_asyncio.fixture
async def normal_user_headers(client: TestClient, auth_headers: Callable, test_data: dict) -> dict:
        """Fixture for a regular user's authentication headers."""
        user = test_data["users"]["test"]
        return await auth_headers(username=user.username, password="testpassword")

    @pytest_asyncio.fixture
async def superuser_headers(self, client: TestClient, auth_headers: Callable, test_data: dict) -> dict:
        """Fixture for a superuser's authentication headers."""
        user = test_data["users"]["admin"]
        return await auth_headers(username=user.username, password="testpassword", is_superuser=True)

    async def test_get_users_as_superuser(self, client: TestClient, superuser_headers: dict, test_data: dict):
        """Test that a superuser can retrieve a list of all users."""
        response = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_headers)
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2  # Based on test_data fixture
        assert "hashed_password" not in users[0]

    async def test_get_users_as_normal_user(self, client: TestClient, normal_user_headers: dict):
        """Test that a normal user cannot retrieve the list of all users."""
        response = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    async def test_create_user_as_superuser(self, client: TestClient, superuser_headers: dict, db: AsyncSession):
        """Test that a superuser can create a new user."""
        new_user_data = {
            "email": "new.user@example.com",
            "username": "new_user_username",
            "password": "a_secure_password",
            "is_superuser": False,
        }
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=new_user_data,
            headers=superuser_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        created_user = response.json()
        assert created_user["email"] == new_user_data["email"]
        assert created_user["username"] == new_user_data["username"]
        assert "id" in created_user
        assert "hashed_password" not in created_user

    async def test_create_user_duplicate_email(self, client: TestClient, superuser_headers: dict, test_data: dict):
        """Test that creating a user with a duplicate email fails."""
        existing_user_email = test_data["users"]["test"].email
        new_user_data = {
            "email": existing_user_email,
            "username": "another_new_user",
            "password": "a_secure_password",
        }
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=new_user_data,
            headers=superuser_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User with this email already exists" in response.json()["detail"]

    async def test_get_user_me(self, client: TestClient, normal_user_headers: dict):
        """Test that a user can retrieve their own information via /users/me."""
        response = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["username"] == "test"
        assert user_data["email"] == "test@example.com"

    async def test_get_user_by_id_as_superuser(self, client: TestClient, superuser_headers: dict, test_data: dict):
        """Test that a superuser can retrieve any user by their ID."""
        target_user_id = test_data["users"]["test"].id
        response = client.get(f"{settings.API_V1_STR}/users/{target_user_id}", headers=superuser_headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["id"] == target_user_id

    async def test_get_user_by_id_as_normal_user_forbidden(
        self, client: TestClient, normal_user_headers: dict, test_data: dict
    ):
        """Test that a normal user cannot retrieve another user's data by ID."""
        # ID of the admin user from test_data
        target_user_id = test_data["users"]["admin"].id
        response = client.get(f"{settings.API_V1_STR}/users/{target_user_id}", headers=normal_user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_user_as_superuser(self, client: TestClient, superuser_headers: dict, test_data: dict):
        """Test that a superuser can update another user's information."""
        target_user_id = test_data["users"]["test"].id
        update_data = {"username": "updated_username", "is_active": False}

        response = client.put(
            f"{settings.API_V1_STR}/users/{target_user_id}",
            json=update_data,
            headers=superuser_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        updated_user = response.json()
        assert updated_user["id"] == target_user_id
        assert updated_user["username"] == "updated_username"
        assert updated_user["is_active"] is False

    async def test_update_user_me(self, client: TestClient, normal_user_headers: dict, db: AsyncSession):
        """Test that a user can update their own information."""
        update_data = {"username": "my_new_username"}
        response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=normal_user_headers)
        assert response.status_code == status.HTTP_200_OK
        updated_user = response.json()
        assert updated_user["username"] == "my_new_username"

    async def test_delete_user_as_superuser(self, client: TestClient, superuser_headers: dict, user_factory):
        """Test that a superuser can delete a user."""
        # Create a user to be deleted
        user_to_delete = await user_factory(username="to_be_deleted", email="delete@me.com")

        response = client.delete(f"{settings.API_V1_STR}/users/{user_to_delete.id}", headers=superuser_headers)
        assert response.status_code == status.HTTP_200_OK
        deleted_user = response.json()
        assert deleted_user["id"] == user_to_delete.id

        # Verify the user is actually deleted
        get_response = client.get(f"{settings.API_V1_STR}/users/{user_to_delete.id}", headers=superuser_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
