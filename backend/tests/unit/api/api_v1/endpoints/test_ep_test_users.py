"""
Comprehensive tests for the Users API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserInDB

pytestmark = pytest.mark.asyncio

class TestUsersAPI:
    """Test suite for Users API endpoints."""

    async def test_create_user_success(
        self, async_client: AsyncClient, test_role: Role, db: AsyncSession
    ):
        """Test creating a new user with valid data."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpassword123",
            "full_name": "New User",
            "is_active": True,
            "role_ids": [test_role.id]
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/users/",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "hashed_password" not in data  # Password should not be returned
        assert data["is_active"] is True
        assert len(data["roles"]) == 1
        assert data["roles"][0]["id"] == test_role.id

    async def test_create_user_duplicate_email(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test creating a user with a duplicate email."""
        user_data = {
            "email": test_user.email,  # Duplicate email
            "username": "differentuser",
            "password": "testpassword123",
            "full_name": "Duplicate Email"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/users/",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.text.lower()

    async def test_get_users_me(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test retrieving the current user's profile."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert "hashed_password" not in data

    async def test_update_user_me(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test updating the current user's profile."""
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com",
            "password": "newpassword123"
        }
        
        response = await async_client.put(
            f"{settings.API_V1_STR}/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["full_name"] == update_data["full_name"]

    async def test_list_users(
        self, async_client: AsyncClient, test_user: User, superuser_token_headers: dict
    ):
        """Test listing users (admin only)."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(user["id"] == test_user.id for user in data)

    async def test_get_user_by_id(
        self, async_client: AsyncClient, test_user: User, superuser_token_headers: dict
    ):
        """Test retrieving a user by ID (admin only)."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/{test_user.id}",
            headers=superuser_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    async def test_update_user(
        self, async_client: AsyncClient, test_user: User, test_role: Role, superuser_token_headers: dict
    ):
        """Test updating a user (admin only)."""
        update_data = {
            "email": "admin_updated@example.com",
            "is_active": False,
            "role_ids": [test_role.id]
        }
        
        response = await async_client.put(
            f"{settings.API_V1_STR}/users/{test_user.id}",
            json=update_data,
            headers=superuser_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["is_active"] == update_data["is_active"]
        assert len(data["roles"]) == 1
        assert data["roles"][0]["id"] == test_role.id

    async def test_delete_user(
        self, async_client: AsyncClient, test_user: User, superuser_token_headers: dict, db: AsyncSession
    ):
        """Test deleting a user (admin only)."""
        # First create a user to delete
        user_data = {
            "email": "user_to_delete@example.com",
            "username": "tobedeleted",
            "password": "testpassword123",
            "full_name": "To Be Deleted"
        }
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/users/",
            json=user_data
        )
        user_id = create_response.json()["id"]
        
        # Now delete the user
        delete_response = await async_client.delete(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers
        )
        
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the user is gone
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
