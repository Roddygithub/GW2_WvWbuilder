"""
Tests for the Authentication API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.security import create_access_token
from app.models import User
from app.schemas.user import UserCreate, UserUpdate

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    """Test user registration."""
    # Test data
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "testpassword123",
        "full_name": "New User"
    }
    
    # Make request
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Password should never be returned
    
    # Verify user was created in database
    result = await db_session.execute(
        "SELECT * FROM users WHERE username = :username",
        {"username": user_data["username"]}
    )
    user = result.first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.is_active is True
    assert user.is_superuser is False

@pytest.mark.asynbox async def test_login_success(client: AsyncClient, test_user):
    """Test successful user login."""
    # Test data
    login_data = {
        "username": test_user.username,
        "password": "testpassword"  # Default password from test_user fixture
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
    assert "hashed_password" not in data["user"]

@pytest.mark.asynbox async def test_login_incorrect_password(client: AsyncClient, test_user):
    """Test login with incorrect password."""
    # Test data with wrong password
    login_data = {
        "username": test_user.username,
        "password": "wrongpassword"
    }
    
    # Make request
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    # Verify response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]

@pytest.mark.asynbox async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    # Test data with non-existent user
    login_data = {
        "username": "nonexistent",
        "password": "password"
    }
    
    # Make request
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    # Verify response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]

@pytest.mark.asynbox async def test_get_current_user(client: AsyncClient, test_user, test_token):
    """Test retrieving the current authenticated user."""
    # Make request with valid token
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert "hashed_password" not in data

@pytest.mark.asynbox async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test retrieving current user without authentication."""
    # Make request without token
    response = await client.get("/api/v1/users/me")
    
    # Verify response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asynbox async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test retrieving current user with invalid token."""
    # Make request with invalid token
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asynbox async def test_update_current_user(client: AsyncClient, test_user, test_token):
    """Test updating the current user's information."""
    # Update data
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    
    # Make request
    response = await client.patch(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]
    
    # Verify the update persisted
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

@pytest.mark.asynbox async def test_change_password_success(client: AsyncClient, test_user, test_token, db_session):
    """Test successfully changing the current user's password."""
    # Get current password hash
    result = await db_session.execute(
        "SELECT hashed_password FROM users WHERE id = :id",
        {"id": test_user.id}
    )
    old_hashed_password = result.scalar_one()
    
    # Change password
    response = await client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "testpassword",  # Default from test_user
            "new_password": "newsecurepassword123"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "Password updated successfully" in data["message"]
    
    # Verify password was changed in database
    await db_session.refresh(test_user)
    assert test_user.hashed_password != old_hashed_password
    
    # Verify login with new password works
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "newsecurepassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK

@pytest.mark.asynbox async def test_change_password_incorrect_current(client: AsyncClient, test_token):
    """Test changing password with incorrect current password."""
    # Try to change password with wrong current password
    response = await client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Incorrect current password" in data["detail"]

@pytest.mark.asynbox async def test_refresh_token(client: AsyncClient, test_user):
    """Test refreshing an access token with a refresh token."""
    # First, login to get a refresh token
    login_data = {
        "username": test_user.username,
        "password": "testpassword"  # Default from test_user
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_response.json().get("refresh_token")
    
    # Now refresh the token
    response = await client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": refresh_token}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asynbox async def test_logout(client: AsyncClient, test_token):
    """Test user logout."""
    # Make request to logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "Successfully logged out" in data["message"]
    
    # Verify token is now invalid
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
