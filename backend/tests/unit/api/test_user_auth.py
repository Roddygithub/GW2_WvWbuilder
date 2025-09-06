"""Unit tests for user authentication and authorization."""
from fastapi import status, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from app.models.base_models import User
from app.api.deps import get_db, get_current_user
from app.main import app
from fastapi.security import OAuth2PasswordBearer

# Helper functions
def create_test_user(db: Session, email: str, username: str, is_superuser: bool = False) -> User:
    """Helper to create a test user."""
    user = User(
        email=email,
        username=username,
        hashed_password="hashed_password",
        is_superuser=is_superuser,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_token(user_id: int) -> str:
    """Helper to get an auth token for testing."""
    return f"test_token:{user_id}"

# Store test users to maintain state between test and dependency
_test_users = {}

# Override the get_current_user dependency for testing
def override_get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), 
                            db: Session = Depends(get_db)):
    """Override for the get_current_user dependency for testing."""
    if not token.startswith("test_token:"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_id = int(token.split(":")[1])
    
    # First check if we have a test user with this ID
    if user_id in _test_users:
        return _test_users[user_id]
        
    # Fall back to database if not found in test users
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

# Apply the override
app.dependency_overrides[get_current_user] = override_get_current_user

# Test cases
def test_get_user_by_id_self(client: TestClient, db: Session) -> None:
    """Test that a user can fetch their own data."""
    # Use the test client's built-in method to create a test user
    user = client.get_or_create_test_user()
    
    # Get the auth headers for this user
    headers = client.auth_header(user)
    
    # User fetches their own data
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers=headers
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK, \
        f"Expected status code 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Check that the response data matches the user we created
    assert data["id"] == user.id, f"Expected user ID {user.id}, got {data['id']}"
    assert data["email"] == user.email, \
        f"Expected email {user.email}, got {data['email']}"
    assert data["username"] == user.username, \
        f"Expected username {user.username}, got {data['username']}"
        
    # Also test with a different user to ensure proper access control
    other_user = client.get_or_create_test_user(
        email="other@example.com",
        username="otheruser"
    )
    
    # Try to access the first user's data with the second user's credentials
    headers = client.auth_header(other_user)
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers=headers
    )
    
    # Should be forbidden for non-superusers
    assert response.status_code == status.HTTP_403_FORBIDDEN, \
        f"Expected status code 403 for unauthorized access, got {response.status_code}"


def test_create_user_success(client: TestClient, db: Session) -> None:
    """Test that a superuser can create a new user."""
    # Create a superuser and store it in our test users dictionary
    admin = create_test_user(
        db=db,
        email="admin@example.com",
        username="admin",
        is_superuser=True
    )
    _test_users[admin.id] = admin
    
    # Test data for new user - using a unique email and username
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"newuser_{unique_id}@example.com",
        "username": f"newuser_{unique_id}",
        "password": "newpassword123",
        "is_superuser": False
    }
    
    # Create new user
    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {get_auth_token(admin.id)}"}
    )
    
    # Clean up
    if admin.id in _test_users:
        del _test_users[admin.id]
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED, \
        f"Expected status code 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data


def test_superuser_can_access_any_user(client: TestClient, db: Session) -> None:
    """Test that a superuser can access any user's data."""
    # Create a regular user
    regular_user = create_test_user(
        db=db,
        email="regular@example.com",
        username="regularuser"
    )
    
    # Create a superuser and store it in our test users dictionary
    superuser = create_test_user(
        db=db,
        email="super@example.com",
        username="superuser",
        is_superuser=True
    )
    
    # Store the superuser in our test users dictionary
    _test_users[superuser.id] = superuser
    
    # Verify the superuser is actually a superuser
    assert superuser.is_superuser is True, "Superuser flag not set correctly"
    
    # Superuser fetches regular user's data
    response = client.get(
        f"/api/v1/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {get_auth_token(superuser.id)}"}
    )
    
    # Clean up
    if superuser.id in _test_users:
        del _test_users[superuser.id]
    
    # Debug output if test fails
    if response.status_code != status.HTTP_200_OK:
        print(f"Superuser ID: {superuser.id}, is_superuser: {superuser.is_superuser}")
        print(f"Regular user ID: {regular_user.id}")
        print(f"Response: {response.status_code} - {response.text}")
    
    # Check that the request was successful
    assert response.status_code == status.HTTP_200_OK, \
        f"Expected status code 200, got {response.status_code}: {response.text}"
