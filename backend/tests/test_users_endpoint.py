"""Tests for the users endpoint."""
import pytest
from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from app.models import User, Role
from app.crud import user as user_crud, role as role_crud
from tests.integration.fixtures.factories import UserFactory, RoleFactory

# Helper function to get auth headers
def get_auth_headers(client, user=None):
    """Get authentication headers for a user."""
    # Get the auth header from the test client
    if user is not None:
        return client.auth_header(user)
    return client.auth_header()

@pytest.mark.usefixtures("client", "db_session")
class TestUsersEndpoint:
    """Test users endpoint."""

    def test_read_users(self, client, db_session):
        """Test reading users as superuser."""
        # Create a test user
        test_user = UserFactory()
        db_session.add(test_user)
        db_session.commit()
        
        # Get auth header for superuser
        superuser = UserFactory(is_superuser=True)
        db_session.add(superuser)
        db_session.commit()
        
        # Test reading users as superuser
        headers = get_auth_headers(client, superuser)
        response = client.get(
            "/api/v1/users/",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0

    def test_create_user(self, client, db_session):
        """Test creating a new user."""
        # Get auth header for superuser
        superuser = UserFactory(is_superuser=True)
        db_session.add(superuser)
        db_session.commit()
        
        headers = get_auth_headers(client, superuser)
        
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "is_active": True
        }
        
        # Test creating a new user
        response = client.post(
            "/api/v1/users/",
            headers=headers,
            json=user_data
        )
        
        # Test creating a user with existing email (should fail)
        response_duplicate = client.post(
            "/api/v1/users/",
            headers=headers,
            json=user_data
        )
        assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["username"] == user_data["username"]
        assert "hashed_password" not in user

    def test_read_user_me(self, client, db_session):
        """Test reading the current user's profile."""
        # Create a test user and get auth token
        test_user = UserFactory()
        db_session.add(test_user)
        db_session.commit()
        
        headers = get_auth_headers(client, test_user)
        
        # Test getting own profile
        response = client.get(
            "/api/v1/users/me",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        user = response.json()
        assert "email" in user
        assert "username" in user
        assert "hashed_password" not in user

    def test_add_and_remove_role(self, client, db_session):
        """Test adding and removing a role from a user."""
        # Create test data
        test_user = UserFactory()
        test_role = RoleFactory(name="test_role")
        another_user = UserFactory()  # Another regular user
        db_session.add_all([test_user, test_role, another_user])
        db_session.commit()
        
        # Get auth headers - any authenticated user can manage roles
        user_headers = client.auth_header(test_user)
        another_user_headers = client.auth_header(another_user)
        
        # Test 1: Add role to self
        response = client.post(
            f"/api/v1/users/{test_user.id}/roles/{test_role.id}",
            headers=user_headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the role was added
        db_session.refresh(test_user)
        assert any(role.id == test_role.id for role in test_user.roles), "Role was not added to user"
        
        # Test 2: Adding the same role again (should be idempotent)
        response_duplicate = client.post(
            f"/api/v1/users/{test_user.id}/roles/{test_role.id}",
            headers=user_headers
        )
        assert response_duplicate.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response_duplicate.status_code}: {response_duplicate.text}"
        
        # Test 3: Another user can manage roles (no permission check in endpoint)
        response_other_user = client.post(
            f"/api/v1/users/{test_user.id}/roles/{test_role.id}",
            headers=another_user_headers
        )
        assert response_other_user.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response_other_user.status_code}"
        
        # Test 4: Remove role
        response_remove = client.delete(
            f"/api/v1/users/{test_user.id}/roles/{test_role.id}",
            headers=user_headers
        )
        assert response_remove.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response_remove.status_code}: {response_remove.text}"
        
        # Verify the role was removed
        db_session.refresh(test_user)
        assert not any(role.id == test_role.id for role in test_user.roles), "Role was not removed from user"
        
        # Test 5: Removing non-existent role (should be idempotent)
        response_nonexistent = client.delete(
            f"/api/v1/users/{test_user.id}/roles/{test_role.id}",
            headers=user_headers
        )
        assert response_nonexistent.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response_nonexistent.status_code}"
        
        # Test 6: Non-existent user or role should return 404
        response_invalid_user = client.post(
            "/api/v1/users/999999/roles/1",
            headers=user_headers
        )
        assert response_invalid_user.status_code == status.HTTP_404_NOT_FOUND, \
            f"Expected 404, got {response_invalid_user.status_code}"
        
        response_invalid_role = client.post(
            f"/api/v1/users/{test_user.id}/roles/999999",
            headers=user_headers
        )
        assert response_invalid_role.status_code == status.HTTP_404_NOT_FOUND, \
            f"Expected 404, got {response_invalid_role.status_code}"

    def test_read_user_by_id(self, client, db_session):
        """Test reading a user by ID with different permission levels."""
        from fastapi import status
        from app.api.deps import get_current_user, get_current_active_user
        from app.main import app
        
        # Create test users
        regular_user = UserFactory(id=1001, email="regular@example.com", is_superuser=False)
        other_user = UserFactory(id=1002, email="other@example.com", is_superuser=False)
        superuser = UserFactory(id=1003, email="admin@example.com", is_superuser=True)
        
        # Add users to the database
        db_session.add_all([regular_user, other_user, superuser])
        db_session.commit()
        
        # Save the original overrides
        original_get_current_user = app.dependency_overrides.get(get_current_user)
        original_get_current_active_user = app.dependency_overrides.get(get_current_active_user)
        
        # Helper function to set up the current user for testing
        def set_current_user(user=None):
            if user is None:
                app.dependency_overrides[get_current_user] = lambda: None
                app.dependency_overrides[get_current_active_user] = lambda: None
            else:
                app.dependency_overrides[get_current_user] = lambda: user
                app.dependency_overrides[get_current_active_user] = lambda: user
        
        try:
            # Test 1: Unauthenticated request should fail with 401
            print("\n=== Test 1: Unauthenticated access ===")
            set_current_user(None)
            
            response = client.get(f"/api/v1/users/{regular_user.id}")
            print(f"Response: {response.status_code} - {response.text}")
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN], \
                f"Expected 401 or 403 for unauthenticated request, got {response.status_code}"
            
            # Test 2: Regular user can view own profile
            print("\n=== Test 2: Regular user views own profile ===")
            set_current_user(regular_user)
            
            response = client.get(f"/api/v1/users/{regular_user.id}")
            print(f"Response: {response.status_code} - {response.text}")
            assert response.status_code == status.HTTP_200_OK, \
                f"Expected 200 when user views own profile, got {response.status_code}"
                
            # Verify the response data
            user_data = response.json()
            assert user_data["id"] == regular_user.id
            assert "email" in user_data
            assert "username" in user_data
            assert "hashed_password" not in user_data
            
            # Test 3: Regular user cannot view another user's profile
            print("\n=== Test 3: Regular user views another user's profile ===")
            set_current_user(regular_user)
            
            response = client.get(f"/api/v1/users/{other_user.id}")
            print(f"Response: {response.status_code} - {response.text}")
            assert response.status_code == status.HTTP_403_FORBIDDEN, \
                f"Expected 403 when regular user views another user's profile, got {response.status_code}"
            
            # Test 4: Superuser can view any profile
            print("\n=== Test 4: Superuser views another user's profile ===")
            set_current_user(superuser)
            
            response = client.get(f"/api/v1/users/{regular_user.id}")
            print(f"Response: {response.status_code} - {response.text}")
            assert response.status_code == status.HTTP_200_OK, \
                f"Expected 200 when superuser views another user's profile, got {response.status_code}"
                
            # Verify the response data
            user_data = response.json()
            assert user_data["id"] == regular_user.id
            assert "email" in user_data
            assert "username" in user_data
            assert "hashed_password" not in user_data
            
        finally:
            # Restore the original overrides
            if original_get_current_user is not None:
                app.dependency_overrides[get_current_user] = original_get_current_user
            else:
                app.dependency_overrides.pop(get_current_user, None)
                
            if original_get_current_active_user is not None:
                app.dependency_overrides[get_current_active_user] = original_get_current_active_user
            else:
                app.dependency_overrides.pop(get_current_active_user, None)
