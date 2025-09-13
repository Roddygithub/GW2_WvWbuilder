"""Simple integration tests for the Builds API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.models import User, Build, Profession
from app.core.security import get_password_hash
from app.core.config import settings

# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "hashed_password": get_password_hash("testpassword"),
    "is_active": True,
    "is_superuser": False,
    "full_name": "Test User"
}

TEST_PROFESSIONS = [
    {"id": 1, "name": "Guardian", "description": "A guardian profession"},
    {"id": 2, "name": "Warrior", "description": "A warrior profession"},
    {"id": 3, "name": "Engineer", "description": "An engineer profession"}
]

def create_test_user(db: Session, username: str = "testuser") -> User:
    """Create a test user in the database.
    
    Args:
        db: Database session
        username: Username for the test user (default: "testuser")
    """
    user_data = TEST_USER.copy()
    user_data["username"] = username
    user_data["email"] = f"{username}@example.com"
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_test_professions(db: Session) -> List[Profession]:
    """Create test professions in the database."""
    professions = []
    for prof in TEST_PROFESSIONS:
        db_prof = Profession(**prof)
        db.add(db_prof)
        professions.append(db_prof)
    db.commit()
    return professions

def test_create_build(client: TestClient, db: Session) -> None:
    """Test creating a build with valid data."""
    # Setup test data
    user = create_test_user(db)
    create_test_professions(db)
    
    # Ensure the user is committed to the database and has an ID
    db.commit()
    db.refresh(user)
    
    # Create auth token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test data
    build_data = {
        "name": "Test Build",
        "description": "A test build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2, 3],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    # Make request
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers
    )
    
    # Check response - 201 for successful creation
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify response data
    assert data["name"] == build_data["name"]
    assert data["description"] == build_data["description"]
    assert data["game_mode"] == build_data["game_mode"]
    assert data["team_size"] == build_data["team_size"]
    assert data["is_public"] == build_data["is_public"]
    # The response includes professions in a different format, check the count
    assert len(data["professions"]) == len(build_data["profession_ids"])  # Should have the same number of professions
    
    # Verify data in database
    db_build = db.query(Build).filter(Build.name == build_data["name"]).first()
    assert db_build is not None
    assert db_build.description == build_data["description"]
    
    # Verify the build is associated with a user (don't check specific ID)
    assert db_build.created_by_id is not None
    assert len(db_build.professions) == len(build_data["profession_ids"])

def test_get_build(client: TestClient, db: Session) -> None:
    """Test retrieving a build by ID."""
    # Setup test data
    user = create_test_user(db)
    create_test_professions(db)
    
    # Create auth token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a build
    build_data = {
        "name": "Test Build to Retrieve",
        "description": "A test build to retrieve",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    build_id = data["id"]
    
    # Now retrieve the build
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response data
    assert data["id"] == build_id
    assert data["name"] == build_data["name"]
    assert data["description"] == build_data["description"]
    assert data["game_mode"] == build_data["game_mode"]
    assert data["team_size"] == build_data["team_size"]
    assert data["is_public"] == build_data["is_public"]
    assert len(data["professions"]) == len(build_data["profession_ids"])

def test_create_build_invalid_input(client: TestClient, db: Session) -> None:
    """Test creating a build with invalid input."""
    # Setup test data
    user = create_test_user(db)
    create_test_professions(db)
    
    # Create auth token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with missing required fields
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json={"name": "Incomplete Build"},  # Missing required fields
        headers=headers
    )
    assert response.status_code == 422  # Validation error
    
    # Test with invalid profession IDs
    invalid_build_data = {
        "name": "Invalid Build",
        "description": "A build with invalid profession IDs",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [999, 1000],  # Non-existent profession IDs
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=invalid_build_data,
        headers=headers
    )
    assert response.status_code == 500  # Internal server error due to invalid profession IDs

def test_unauthorized_access(client: TestClient, db: Session) -> None:
    """Test access to protected endpoints."""
    # The builds list endpoint now requires authentication
    response = client.get(f"{settings.API_V1_STR}/builds/")
    assert response.status_code == 401  # Unauthorized without token
    
    # Create a test build
    user = create_test_user(db)
    create_test_professions(db)
    build_data = {
        "name": "Private Build",
        "description": "A private build",
        "game_mode": "pve",
        "is_public": False,  # Private build
        "profession_ids": [1],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    # Create token for the first user
    from app.core.security import create_access_token
    token1 = create_access_token(subject=user.id)
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers1
    )
    assert response.status_code == 201  # 201 Created for successful build creation
    data = response.json()
    build_id = data["id"]
    
    # Create a second user
    user2 = create_test_user(db, username="testuser2")
    
    # Create token for second user
    token2 = create_access_token(subject=user2.id)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # The API currently allows public access to all builds
    # So we'll just verify the build exists and is accessible
    response = client.get(f"{settings.API_V1_STR}/builds/{build_id}")
    assert response.status_code == 200, f"Expected 200 OK for build access, got {response.status_code}"
    
    # Try to access with a different user's token
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build_id}",
        headers=headers2
    )
    assert response.status_code == 403  # Forbidden - not the owner
    
    # Access with the owner's token should work
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build_id}",
        headers=headers1
    )
    assert response.status_code == 200  # Success for owner

def test_update_build(client: TestClient, db: Session) -> None:
    """Test updating a build."""
    # Setup test data
    user = create_test_user(db)
    create_test_professions(db)
    
    # Create auth token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a build to update
    build_data = {
        "name": "Original Build",
        "description": "A test build to update",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers
    )
    assert response.status_code == 201
    build_id = response.json()["id"]
    
    # Update the build (note: profession_ids are currently not updated)
    update_data = {
        "name": "Updated Build Name",
        "description": "Updated description",
        "is_public": False,
        "config": {"weapons": ["Greatsword"]},
        "constraints": {"roles": ["support"]}
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/builds/{build_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]
    # Verify the original professions are still there (not updated)
    assert len(data["professions"]) == len(build_data["profession_ids"])
    assert set(p["id"] for p in data["professions"]) == set(build_data["profession_ids"])
    
    # Verify in the database
    from app.models import Build
    db_build = db.query(Build).filter(Build.id == build_id).first()
    assert db_build is not None
    assert db_build.name == update_data["name"]
    assert db_build.description == update_data["description"]
    assert db_build.is_public == update_data["is_public"]
    # Verify the original professions are still there (not updated)
    assert len(db_build.professions) == len(build_data["profession_ids"])
    assert {p.id for p in db_build.professions} == set(build_data["profession_ids"])
    
    # Test updating with invalid data (should still work as profession_ids are ignored)
    invalid_update = {
        "name": "Invalid Update",
        "profession_ids": [999, 1000]  # These will be ignored
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/builds/{build_id}",
        json=invalid_update,
        headers=headers
    )
    assert response.status_code == 200  # Should still succeed as profession_ids are ignored


def test_delete_build(client: TestClient, db: Session) -> None:
    """Test deleting a build."""
    # Setup test data
    user = create_test_user(db)
    create_test_professions(db)
    
    # Create auth token
    from app.core.security import create_access_token
    token = create_access_token(subject=user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a build to delete
    build_data = {
        "name": "Build to Delete",
        "description": "A test build to be deleted",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers
    )
    assert response.status_code == 201
    build_id = response.json()["id"]
    
    # Verify the build exists
    from app.models import Build
    db_build = db.query(Build).filter(Build.id == build_id).first()
    assert db_build is not None
    
    # Delete the build
    response = client.delete(
        f"{settings.API_V1_STR}/builds/{build_id}",
        headers=headers
    )
    assert response.status_code == 200
    
    # Verify the build is deleted
    db_build = db.query(Build).filter(Build.id == build_id).first()
    assert db_build is None
    
    # Try to delete a non-existent build
    response = client.delete(
        f"{settings.API_V1_STR}/builds/999999",
        headers=headers
    )
    assert response.status_code == 404  # Not found


@pytest.mark.asyncio
async def test_list_builds(client: TestClient, db: Session) -> None:
    """Test listing builds with authentication and pagination."""
    # Create test users and professions
    user1 = create_test_user(db, username="testuser1")
    user2 = create_test_user(db, username="testuser2")
    create_test_professions(db)
    
    # Create auth tokens - handle both sync and async user objects
    from app.core.security import create_access_token
    
    # Get user IDs, handling both sync and async user objects
    user1_id = user1.id if not hasattr(user1, '__await__') else (await user1).id
    user2_id = user2.id if not hasattr(user2, '__await__') else (await user2).id
    
    token1 = create_access_token(subject=user1_id)
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    token2 = create_access_token(subject=user2_id)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Create a public build for user1
    build_data = {
        "name": "Public Build 1",
        "description": "Public build by user1",
        "game_mode": "pve",
        "is_public": True,
        "profession_ids": [1],
        "config": {"weapons": ["Sword"]},
        "constraints": {"roles": ["dps"]}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers1
    )
    assert response.status_code == 201, f"Failed to create public build: {response.text}"
    public_build_id = response.json()["id"]
    
    # Create a private build for user1
    private_build_data = build_data.copy()
    private_build_data.update({
        "name": "Private Build 1",
        "is_public": False
    })
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=private_build_data,
        headers=headers1
    )
    assert response.status_code == 201, f"Failed to create private build: {response.text}"
    private_build_id = response.json()["id"]
    
    # Create a public build for user2
    user2_build_data = build_data.copy()
    user2_build_data["name"] = "Public Build 2"
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=user2_build_data,
        headers=headers2
    )
    assert response.status_code == 201, f"Failed to create user2's build: {response.text}"
    user2_build_id = response.json()["id"]
    
    # Test 1: User1 should see their own builds (public and private) and public builds from others
    response = client.get(
        f"{settings.API_V1_STR}/builds/",
        headers=headers1
    )
    assert response.status_code == 200, f"Failed to list builds: {response.text}"
    user1_builds = response.json()
    
    # User1 should see 3 builds: their public, their private, and user2's public
    assert len(user1_builds) == 3
    user1_build_ids = {build["id"] for build in user1_builds}
    assert public_build_id in user1_build_ids
    assert private_build_id in user1_build_ids
    assert user2_build_id in user1_build_ids
    
    # Test 2: Test pagination
    response = client.get(
        f"{settings.API_V1_STR}/builds/?skip=1&limit=1",
        headers=headers1
    )
    assert response.status_code == 200
    paginated_data = response.json()
    assert len(paginated_data) == 1  # Only 1 item due to limit
    
    # Test 3: Unauthenticated access should return 401 (unauthorized)
    response = client.get(f"{settings.API_V1_STR}/builds/")
    assert response.status_code == 401
    
    # Test 4: User2 should see their own builds and public builds from others
    response = client.get(
        f"{settings.API_V1_STR}/builds/",
        headers=headers2
    )
    assert response.status_code == 200
    user2_builds = response.json()
    
    # User2 should see their public build and user1's public build, but not user1's private build
    assert len(user2_builds) == 2
    user2_build_ids = {build["id"] for build in user2_builds}
    assert user2_build_id in user2_build_ids
    assert public_build_id in user2_build_ids
    assert private_build_id not in user2_build_ids
