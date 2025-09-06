"""Unit tests for user endpoints with proper authentication."""
from fastapi import status, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from typing import Dict, Any

from app.core.security import get_password_hash
from app.models.base_models import User
from app.schemas.user import UserCreate, UserUpdate
from app.api.deps import get_db, get_current_user, get_current_active_superuser
from app.main import app
from fastapi.security import OAuth2PasswordBearer
from app.crud import user as user_crud

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_USERNAME = "testuser"

# Helper functions
def create_test_user(db: Session, email: str = TEST_USER_EMAIL, 
                   username: str = TEST_USER_USERNAME, 
                   password: str = TEST_USER_PASSWORD, 
                   is_superuser: bool = False) -> User:
    """Helper to create a test user directly in the database."""
    hashed_password = get_password_hash(password)
    user = User(
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
    return f"test_token:{user_id}"

# Override the get_current_user and get_current_active_superuser dependencies for testing
def override_get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), 
                            db: Session = Depends(get_db)):
    """Override for the get_current_user dependency for testing."""
    if not token.startswith("test_token:"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_id = int(token.split(":")[1])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def override_get_current_active_superuser(current_user: User = Depends(override_get_current_user)):
    """Override for the get_current_active_superuser dependency for testing."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

# Apply the overrides
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_active_superuser] = override_get_current_active_superuser

# Test cases
def test_create_user_success(client: TestClient, db: Session) -> None:
    """Test creating a new user (admin only)."""
    # First, create an admin user with superuser privileges
    admin = create_test_user(
        db=db,
        email="admin@example.com",
        username="admin",
        is_superuser=True
    )
    
    # Debug: Check if admin is actually a superuser
    assert admin.is_superuser is True, "Admin user must be a superuser"
    
    # Create a new user as admin
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
        headers={"Authorization": f"Bearer {get_auth_token(admin.id)}"}
    )
    
    # Debug: Print response if test fails
    if response.status_code != status.HTTP_201_CREATED:
        print(f"Response: {response.status_code} - {response.text}")
        print(f"Admin user - id: {admin.id}, is_superuser: {admin.is_superuser}")
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data

def test_get_user_by_id_self(client: TestClient, db: Session) -> None:
    """Test that a user can fetch their own data."""
    # Create a test user
    user = create_test_user(db, email="self@example.com", username="selftestuser")
    
    # User fetches their own data
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {get_auth_token(user.id)}"}
    )
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Expected status code 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "self@example.com"
    assert data["username"] == "selftestuser"

def test_get_user_by_id_superuser(client: TestClient, db: Session) -> None:
    """Test that a superuser can fetch any user's data."""
    # Create a regular user
    regular_user = create_test_user(
        db, 
        email="regular@example.com", 
        username="regularuser"
    )
    
    # Create a superuser
    superuser = create_test_user(
        db,
        email="super@example.com",
        username="superuser",
        is_superuser=True
    )
    
    # Superuser fetches regular user's data
    response = client.get(
        f"/api/v1/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {get_auth_token(superuser.id)}"}
    )
    
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
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
        f"Expected status code 401, got {response.status_code}: {response.text}"

def test_get_user_by_id_forbidden(client: TestClient, db: Session) -> None:
    """Test that a user cannot fetch another user's data."""
    # Create two regular users
    user1 = create_test_user(db, email="user1@example.com", username="user1")
    user2 = create_test_user(db, email="user2@example.com", username="user2")
    
    # User1 tries to fetch user2's data
    response = client.get(
        f"/api/v1/users/{user2.id}",
        headers={"Authorization": f"Bearer {get_auth_token(user1.id)}"}
    )
    
    # User1 should not be able to access user2's data
    assert response.status_code == status.HTTP_403_FORBIDDEN, \
        f"Expected status code 403, got {response.status_code}: {response.text}"
