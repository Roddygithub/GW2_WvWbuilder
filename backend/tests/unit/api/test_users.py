"""Unit tests for user endpoints."""
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from typing import Dict, Any, Generator

from app.core.security import get_password_hash
from app.models.base_models import User
from app.schemas.user import UserCreate, UserUpdate
from app.api.deps import get_current_user, get_current_active_user, get_current_active_superuser

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_USERNAME = "testuser"

# Helper functions
def create_test_user(db: Session, email: str = TEST_USER_EMAIL, username: str = TEST_USER_USERNAME, 
                   password: str = TEST_USER_PASSWORD, is_superuser: bool = False) -> User:
    """Helper to create a test user."""
    from app.crud.user import user as user_crud
    from app.schemas.user import UserCreate
    from app.models.base_models import User as UserModel
    
    # Create user directly in the database
    hashed_password = get_password_hash(password)
    user = UserModel(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_superuser=is_superuser,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_token(user_id: int) -> str:
    """Helper to get an authentication token for testing."""
    # For testing, we'll use a simple token format that includes the user ID
    # This matches the format expected by our test override in conftest.py
    return f"test_token:{user_id}"

# Override the get_current_user dependency for testing
def override_get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Override for the get_current_user dependency for testing."""
    if not token.startswith("test_token:"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_id = int(token.split(":")[1])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Apply the override
app.dependency_overrides[get_current_user] = override_get_current_user

# Test cases
def test_create_user(client: TestClient, db: Session) -> None:
    """Test creating a new user (admin only)."""
    # First, create an admin user with superuser privileges
    admin = create_test_user(
        db,
        email="admin@example.com",
        username="admin",
        is_superuser=True  # Ensure this is set to True
    )
    
    # Verify the admin is actually a superuser
    assert admin.is_superuser is True, "Admin user must be a superuser"
    
    # Get auth token for admin
    token = get_auth_token(admin.id)
    
    # Test data for new user
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
        "is_superuser": False
    }
    
    # Create new user
    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check if the request was successful
    if response.status_code != status.HTTP_201_CREATED:
        print(f"Response content: {response.text}")
        print(f"Admin user is_superuser: {admin.is_superuser}")
        print(f"Admin user id: {admin.id}")
    
    assert response.status_code == status.HTTP_201_CREATED, \
        f"Expected status code 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data

def test_get_user_by_id_self(client: TestClient, db: Session) -> None:
    """Test that a user can fetch their own data."""
    # Create a test user
    user = create_test_user(db, email="self@example.com", username="selftestuser")
    
    # Get auth token for the test user
    token = get_auth_token(user.id)
    
    # User fetches their own data
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Expected status code 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "self@example.com"
    assert data["username"] == "selftestuser"

def test_get_user_by_id_superuser(client: TestClient, db: Session) -> None:
    """Test that a superuser can fetch any user's data."""
    # Create a regular user first
    regular_user = create_test_user(
        db, 
        email="regular@example.com", 
        username="regularuser"
    )
    
    # Create a superuser with is_superuser=True
    superuser = create_test_user(
        db,
        email="super@example.com",
        username="superuser",
        is_superuser=True
    )
    
    # Verify the superuser was created with the correct flag
    assert superuser.is_superuser is True, "Superuser flag not set correctly"
    
    # Get auth token for the superuser
    token = get_auth_token(superuser.id)
    
    # Superuser fetches regular user's data
    response = client.get(
        f"/api/v1/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Debug output if the test fails
    if response.status_code != status.HTTP_200_OK:
        print(f"Response content: {response.text}")
        print(f"Superuser is_superuser: {superuser.is_superuser}")
        print(f"Regular user id: {regular_user.id}")
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Expected status code 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["id"] == regular_user.id
    assert data["email"] == "regular@example.com"

def test_get_user_by_id_unauthorized(client: TestClient, db: Session) -> None:
    """Test that unauthenticated requests are rejected."""
    # Try to fetch user data without authentication
    response = client.get("/api/v1/users/1")
    
    # The endpoint requires authentication, so it should return 401 Unauthorized
    # because the user is not authenticated
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
        f"Expected status code 401, got {response.status_code}: {response.text}"

def test_get_user_by_id_forbidden(client: TestClient, db: Session) -> None:
    """Test that a user cannot fetch another user's data."""
    # Create two regular users
    user1 = create_test_user(db, email="user1@example.com", username="user1")
    user2 = create_test_user(db, email="user2@example.com", username="user2")
    
    # Get auth token for user1
    token = get_auth_token(user1.id)
    
    # User1 tries to fetch user2's data
    response = client.get(
        f"/api/v1/users/{user2.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # User1 should not be able to access user2's data
    assert response.status_code == status.HTTP_403_FORBIDDEN, \
        f"Expected status code 403, got {response.status_code}: {response.text}"
