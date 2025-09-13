"""Tests for user management routes."""
import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pytestmark = pytest.mark.asyncio

async def test_create_user(
    async_client: AsyncClient,
    test_token: str,
    test_role: dict
):
    """Test creating a new user (admin only)."""
    user_data = {
        "email": "newuser@example.com",
        "password": "testpassword123",
        "username": "newuser",
        "full_name": "New User",
        "role_ids": [test_role["id"]]
    }
    
    response = await async_client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data
    assert len(data["roles"]) == 1
    assert data["roles"][0]["id"] == test_role["id"]

async def test_get_users(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict
):
    """Test listing users (admin only)."""
    response = await async_client.get(
        "/api/v1/users/",
        params={"skip": 0, "limit": 10},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user["id"] == test_user["id"] for user in data)
    assert all("hashed_password" not in user for user in data)

async def test_get_user(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict
):
    """Test retrieving a user by ID."""
    response = await async_client.get(
        f"/api/v1/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["email"] == test_user["email"]
    assert "hashed_password" not in data

async def test_update_user(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict
):
    """Test updating a user."""
    update_data = {
        "full_name": "Updated Name",
        "is_active": False,
        "role_ids": [test_user["roles"][0]["id"]]
    }
    
    response = await async_client.put(
        f"/api/v1/users/{test_user['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["is_active"] == update_data["is_active"]
    assert len(data["roles"]) == 1
    assert data["roles"][0]["id"] == update_data["role_ids"][0]

async def test_update_self(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict
):
    """Test that users can update their own profile."""
    update_data = {
        "full_name": "My New Name",
        "email": "updated@example.com"
    }
    
    response = await async_client.put(
        f"/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

async def test_change_password(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict,
    test_password: str
):
    """Test changing a user's password."""
    password_data = {
        "current_password": test_password,
        "new_password": "newsecurepassword123"
    }
    
    response = await async_client.post(
        "/api/v1/users/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password updated successfully"}

async def test_unauthorized_access(
    async_client: AsyncClient,
    test_user: dict
):
    """Test that user endpoints require authentication."""
    # Try to access without token
    response = await async_client.get("/api/v1/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = await async_client.get(f"/api/v1/users/{test_user['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_forbidden_actions(
    async_client: AsyncClient,
    test_user: dict,
    another_user_token: str
):
    """Test that regular users can't access admin endpoints."""
    # Regular user trying to list all users
    response = await async_client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Regular user trying to update another user
    response = await async_client.put(
        f"/api/v1/users/{test_user['id']}",
        json={"full_name": "Hacked"},
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_user_invalid_email(
    async_client: AsyncClient,
    test_token: str,
    test_role: dict
):
    """Test creating a user with an invalid email format."""
    user_data = {
        "email": "not-an-email",
        "password": "testpassword123",
        "username": "invalidemail",
        "full_name": "Invalid Email",
        "role_ids": [test_role["id"]]
    }
    
    response = await async_client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "value is not a valid email address" in str(response.content)

async def test_create_user_duplicate_email(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict,
    test_role: dict
):
    """Test creating a user with a duplicate email address."""
    user_data = {
        "email": test_user["email"],
        "password": "testpassword123",
        "username": "duplicateemail",
        "full_name": "Duplicate Email",
        "role_ids": [test_role["id"]]
    }
    
    response = await async_client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

async def test_update_nonexistent_user(
    async_client: AsyncClient,
    test_token: str
):
    """Test updating a user that doesn't exist."""
    update_data = {
        "full_name": "Nonexistent User",
        "is_active": True
    }
    
    response = await async_client.put(
        "/api/v1/users/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]

async def test_change_password_incorrect_current(
    async_client: AsyncClient,
    test_token: str
):
    """Test changing password with incorrect current password."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newsecurepassword123"
    }
    
    response = await async_client.post(
        "/api/v1/users/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Incorrect current password" in response.json()["detail"]

async def test_change_password_weak_password(
    async_client: AsyncClient,
    test_token: str,
    test_password: str
):
    """Test changing to a weak password."""
    password_data = {
        "current_password": test_password,
        "new_password": "123"
    }
    
    response = await async_client.post(
        "/api/v1/users/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "ensure this value has at least 8 characters" in str(response.content)
