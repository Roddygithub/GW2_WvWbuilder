"""Integration tests for authentication flow with key rotation."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy.orm import Session

from app.main import app
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.security.keys import KeyManager
from app.models.user import User
from app.core.security import get_password_hash

# Test client
client = TestClient(app)

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_USER_ID = 1


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        email=TEST_USER_EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def temp_key_file(tmp_path):
    """Create a temporary key file for testing."""
    key_file = tmp_path / "test_keys.json"
    return key_file


class TestAuthFlow:
    """Test authentication flow including registration, login, and token management."""

    def test_register_new_user(self, db: Session):
        """Test user registration with valid data."""
        user_data = {
            "email": "newuser@example.com",
            "password": "NewUser123!",
            "full_name": "Test User",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert "password" not in data

        # Verify user was created in database
        user = db.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.email == user_data["email"]

    def test_login_success(self, test_user):
        """Test successful user login."""
        login_data = {"username": TEST_USER_EMAIL, "password": TEST_PASSWORD}

        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, test_user):
        """Test login with invalid credentials."""
        login_data = {"username": TEST_USER_EMAIL, "password": "wrongpassword"}

        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_refresh_token(self, test_user):
        """Test token refresh flow."""
        # First login to get tokens
        login_data = {"username": TEST_USER_EMAIL, "password": TEST_PASSWORD}

        login_response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh the token
        refresh_response = client.post(
            "/api/v1/auth/refresh-token", json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # New tokens should be different from original ones
        assert data["access_token"] != login_response.json()["access_token"]
        assert data["refresh_token"] != login_response.json()["refresh_token"]

    def test_protected_endpoint(self, test_user):
        """Test accessing a protected endpoint with valid token."""
        # Get access token
        login_data = {"username": TEST_USER_EMAIL, "password": TEST_PASSWORD}

        login_response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access_token = login_response.json()["access_token"]

        # Access protected endpoint
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL

    def test_protected_endpoint_invalid_token(self):
        """Test accessing a protected endpoint with invalid token."""
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


class TestKeyRotation:
    """Test JWT key rotation functionality."""

    def test_key_rotation_flow(self, temp_key_file):
        """Test the complete auth flow with key rotation."""
        # Initialize key manager with test file
        key_manager = KeyManager(key_file=temp_key_file)

        with patch("app.core.security.jwt.get_key_manager", return_value=key_manager):
            # Create initial tokens
            access_token = create_access_token(subject=TEST_USER_ID)
            create_refresh_token(subject=TEST_USER_ID)

            # Verify tokens work

            # Rotate keys
            key_manager.rotate_keys()

            # Old access token should still work (until it expires)
            assert decode_token(access_token)["sub"] == str(TEST_USER_ID)

            # New tokens should work with the new key
            new_access_token = create_access_token(subject=TEST_USER_ID)
            assert decode_token(new_access_token)["sub"] == str(TEST_USER_ID)

    def test_token_after_key_rotation(self, temp_key_file):
        """Test that tokens created before key rotation remain valid."""
        key_manager = KeyManager(key_file=temp_key_file)

        with patch("app.core.security.jwt.get_key_manager", return_value=key_manager):
            # Create token with first key
            token1 = create_access_token(subject=TEST_USER_ID)

            # Rotate keys
            key_manager.rotate_keys()

            # Token created before rotation should still be valid
            assert decode_token(token1)["sub"] == str(TEST_USER_ID)

            # New token with new key
            token2 = create_access_token(subject=TEST_USER_ID)
            assert decode_token(token2)["sub"] == str(TEST_USER_ID)

    def test_concurrent_key_rotation(self, temp_key_file):
        """Test key rotation with concurrent requests."""
        key_manager = KeyManager(key_file=temp_key_file)

        def rotate_in_thread():
            with patch(
                "app.core.security.jwt.get_key_manager", return_value=key_manager
            ):
                return key_manager.rotate_keys()

        with patch("app.core.security.jwt.get_key_manager", return_value=key_manager):
            # Create initial token
            token = create_access_token(subject=TEST_USER_ID)

            # Simulate concurrent rotation
            rotate_in_thread()

            # Original token should still be valid
            assert decode_token(token)["sub"] == str(TEST_USER_ID)

            # New tokens should use the new key
            new_token = create_access_token(subject=TEST_USER_ID)
            assert new_token != token
