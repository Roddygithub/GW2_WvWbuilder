"""Tests for authentication routes."""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User
from app.schemas.token import Token

pytestmark = pytest.mark.asyncio

async def test_login_success(
    async_client: AsyncClient, 
    test_user: User,
    test_password: str
):
    """Test successful login with correct credentials."""
    login_data = {
        "username": test_user.email,
        "password": test_password
    }
    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    token = Token(**response.json())
    assert token.token_type == "bearer"
    assert token.access_token is not None
    assert token.refresh_token is not None

async def test_login_invalid_credentials(async_client: AsyncClient, test_user: User):
    """Test login with invalid credentials."""
    login_data = {
        "username": test_user.email,
        "password": "wrong_password"
    }
    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Incorrect email or password" in response.json()["detail"]

async def test_refresh_token(
    async_client: AsyncClient, 
    test_user: User,
    test_refresh_token: str
):
    """Test token refresh with valid refresh token."""
    response = await async_client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": test_refresh_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    token = Token(**response.json())
    assert token.token_type == "bearer"
    assert token.access_token is not None

async def test_refresh_token_invalid(async_client: AsyncClient):
    """Test token refresh with invalid refresh token."""
    response = await async_client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid refresh token" in response.json()["detail"]

async def test_me_authenticated(
    async_client: AsyncClient, 
    test_token: str,
    test_user: User
):
    """Test getting current user with valid token."""
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert "hashed_password" not in data

async def test_me_unauthenticated(async_client: AsyncClient):
    """Test getting current user without authentication."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_logout(
    async_client: AsyncClient, 
    test_token: str,
    test_refresh_token: str
):
    """Test logout functionality."""
    # First login to get tokens
    response = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": test_refresh_token},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Successfully logged out"}
    
    # Verify token is blacklisted
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize("endpoint", [
    "/api/v1/auth/me",
    "/api/v1/auth/refresh-token",
    "/api/v1/auth/logout"
])
async def test_protected_endpoints_require_auth(
    async_client: AsyncClient, 
    endpoint: str
):
    """Test that protected endpoints require authentication."""
    if endpoint == "/api/v1/auth/refresh-token":
        response = await async_client.post(endpoint, json={"refresh_token": "dummy"})
    elif endpoint == "/api/v1/auth/logout":
        response = await async_client.post(endpoint, json={"refresh_token": "dummy"})
    else:
        response = await async_client.get(endpoint)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]
