import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Generator
from datetime import datetime, timedelta

# Import app settings and utilities
from app.core.config import settings
from app.core.security import create_access_token
from app.models import User, Build, Profession, build_profession
from app.schemas.build import BuildCreate, BuildUpdate

# Import test utilities and helpers
from tests.conftest import client, db
from tests.integration.fixtures.factories import UserFactory, ProfessionFactory

def create_test_user(db: Session, **kwargs) -> User:
    """Helper to create a test user."""
    user = UserFactory(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_professions(db: Session, count: int = 5) -> List[Profession]:
    """Helper to create test professions."""
    professions = [ProfessionFactory() for _ in range(count)]
    db.add_all(professions)
    db.commit()
    return professions

def create_test_build(
    db: Session, 
    owner_id: int, 
    is_public: bool = True, 
    **overrides
) -> Build:
    """Helper to create a test build."""
    build_data = {
        "name": "Test Build",
        "description": "A test build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": is_public,
        "owner_id": owner_id,
        **overrides
    }
    build = Build(**build_data)
    db.add(build)
    db.commit()
    db.refresh(build)
    return build

def get_auth_headers(user_id: int) -> Dict[str, str]:
    """Get authentication headers for a user."""
    access_token = create_access_token(subject=str(user_id))
    return {"Authorization": f"Bearer {access_token}"}

# Test data
TEST_BUILD_DATA = {
    "name": "New Test Build",
    "description": "A new test build",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "profession_ids": [1, 2, 3]
}

# Authentication Tests
class TestBuildAuthentication:
    """Test authentication requirements for build endpoints."""
    
    def test_create_build_unauthenticated(self, client: TestClient, db: Session):
        """Test creating a build without authentication should fail."""
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=TEST_BUILD_DATA
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]
    
    def test_update_build_unauthenticated(self, client: TestClient, db: Session):
        """Test updating a build without authentication should fail."""
        # Create a test user and build
        user = create_test_user(db, email="test1@example.com")
        build = create_test_build(db, owner_id=user.id)
        
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_build_unauthenticated(self, client: TestClient, db: Session):
        """Test deleting a build without authentication should fail."""
        # Create a test user and build
        user = create_test_user(db, email="test2@example.com")
        build = create_test_build(db, owner_id=user.id)
        
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Authorization Tests
class TestBuildAuthorization:
    """Test authorization for build endpoints."""
    
    def test_update_other_users_build(self, client: TestClient, db: Session):
        """Test updating another user's build should fail."""
        # Create two test users
        owner = create_test_user(db, email="owner@example.com")
        other_user = create_test_user(db, email="other@example.com")
        
        # Owner creates a build
        build = create_test_build(db, owner_id=owner.id)
        
        # Other user tries to update the build
        headers = get_auth_headers(other_user.id)
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            headers=headers,
            json={"name": "Unauthorized Update"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_delete_other_users_build(self, client: TestClient, db: Session):
        """Test deleting another user's build should fail."""
        # Create two test users
        owner = create_test_user(db, email="owner2@example.com")
        other_user = create_test_user(db, email="other2@example.com")
        
        # Owner creates a build
        build = create_test_build(db, owner_id=owner.id)
        
        # Other user tries to delete the build
        headers = get_auth_headers(other_user.id)
        response = client.delete(
            f"{settings.API_V1_STR}/builds/{build.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

# Error Handling Tests
class TestBuildErrorHandling:
    """Test error handling for build endpoints."""
    
    def test_get_nonexistent_build(self, client: TestClient, db: Session):
        """Test getting a non-existent build returns 404."""
        user = create_test_user(db, email="test3@example.com")
        headers = get_auth_headers(user.id)
        
        response = client.get(
            f"{settings.API_V1_STR}/builds/999999",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_build_invalid_professions(self, client: TestClient, db: Session):
        """Test creating a build with invalid profession IDs returns 400."""
        user = create_test_user(db, email="test4@example.com")
        headers = get_auth_headers(user.id)
        
        # Create some test professions
        professions = create_test_professions(db, count=3)
        valid_profession_ids = [p.id for p in professions]
        
        # Try to create a build with one invalid profession ID
        invalid_build_data = {
            **TEST_BUILD_DATA,
            "profession_ids": [*valid_profession_ids, 99999]  # Invalid ID
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            headers=headers,
            json=invalid_build_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_build_validation_error(self, client: TestClient, db: Session):
        """Test creating a build with invalid data returns 422."""
        user = create_test_user(db, email="test5@example.com")
        headers = get_auth_headers(user.id)
        
        # Missing required field 'name'
        invalid_data = {
            "description": "Missing name field",
            "game_mode": "wvw",
            "team_size": 5
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            headers=headers,
            json=invalid_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "field required" in str(response.json()["detail"][0]["msg"]).lower()

# Pagination Tests
class TestBuildPagination:
    """Test pagination for listing builds."""
    
    def test_list_builds_pagination(self, client: TestClient, db: Session):
        """Test pagination parameters for listing builds."""
        user = create_test_user(db, email="test6@example.com")
        headers = get_auth_headers(user.id)
        
        # Create 15 test builds
        for i in range(15):
            create_test_build(
                db,
                owner_id=user.id,
                name=f"Test Build {i+1}",
                is_public=True
            )
        
        # Test first page (limit=10, skip=0)
        response = client.get(
            f"{settings.API_V1_STR}/builds/",
            headers=headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["skip"] == 0
        assert data["limit"] == 10
        
        # Test second page (limit=10, skip=10)
        response = client.get(
            f"{settings.API_V1_STR}/builds/",
            headers=headers,
            params={"skip": 10, "limit": 10}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5  # Only 5 items left
        assert data["total"] == 15
        assert data["skip"] == 10
        assert data["limit"] == 10
        
        # Test with custom limit
        response = client.get(
            f"{settings.API_V1_STR}/builds/",
            headers=headers,
            params={"skip": 5, "limit": 3}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 3
        assert data["skip"] == 5
        assert data["limit"] == 3
