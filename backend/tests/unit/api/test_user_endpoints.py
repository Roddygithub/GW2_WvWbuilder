"""Unit tests for user endpoints with proper authentication."""
from fastapi import status, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from typing import Dict, Any

from app.core.security import get_password_hash
from app.models.base_models import User
from app.schemas.user import UserCreate
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

# Override the get_current_user dependency for testing
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

# Apply the overrides
app.dependency_overrides[get_current_user] = override_get_current_user

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
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data

# Mark the remaining tests as pending implementation
@pytest.mark.skip(reason="To be implemented")
def test_get_user_by_id_self(client: TestClient, db: Session) -> None:
    pass

@pytest.mark.skip(reason="To be implemented")
def test_get_user_by_id_superuser(client: TestClient, db: Session) -> None:
    pass

@pytest.mark.skip(reason="To be implemented") 
def test_get_user_by_id_unauthorized(client: TestClient, db: Session) -> None:
    pass

@pytest.mark.skip(reason="To be implemented")
def test_get_user_by_id_forbidden(client: TestClient, db: Session) -> None:
    pass
