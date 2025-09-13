import pytest
import logging
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Generator
from datetime import datetime, timedelta

# Import app settings and utilities
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.build import BuildCreate, BuildUpdate

# Import models to ensure they are registered with SQLAlchemy
from app.models import models  # noqa: F401
from app.models.build import Build  # noqa: F401
from app.models.build_profession import BuildProfession  # noqa: F401
from app.models.models import Composition, CompositionTag  # noqa: F401
from app.models.models import Profession, EliteSpecialization  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.user import User  # noqa: F401

# Import test utilities and helpers
from tests.conftest import client, db
from tests.integration.fixtures.factories import (
    BuildFactory, 
    UserFactory, 
    ProfessionFactory,
    EliteSpecializationFactory
)
from tests.integration.utils.test_helpers import create_test_profession, create_test_professions

# Test data
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "A test build for WvW",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "config": {"roles": ["heal", "dps", "support"]},
    "constraints": {"max_duplicates": 2},
    "profession_ids": [1, 2, 3, 4, 5]  # Will be replaced with actual IDs in tests
}

# Invalid test data
INVALID_BUILD_DATA = [
    ({"name": ""}, "name", "String should have at least 1 character"),  # Empty name
    ({"game_mode": "invalid"}, "game_mode", "Input should be 'pve','pvp', or 'wvw'"),
    ({"team_size": 0}, "team_size", "Input should be greater than 0"),
    ({"team_size": 11}, "team_size", "Input should be less than or equal to 10"),
    ({"config": {}}, "config", "Input should be a valid dictionary"),
    ({"constraints": {}}, "constraints", "Input should be a valid dictionary"),
    ({"profession_ids": []}, "profession_ids", "profession_ids must contain at least one profession"),
]

# Helper functions for testing
def create_test_build_data(db: Session, user=None, is_public=True, **overrides) -> Dict[str, Any]:
    """Create test data for build tests with optional overrides."""
    if user is None:
        user = UserFactory()
    
    # Create some professions if not provided
    if "professions" not in overrides:
        professions = [ProfessionFactory() for _ in range(5)]
        db.add_all(professions)
        db.commit()
    else:
        professions = overrides.pop("professions")
    
    # Create base test data
    test_data = TEST_BUILD_DATA.copy()
    test_data.update({
        "profession_ids": [p.id for p in professions],
        "is_public": is_public,
        **overrides
    })
    
    return {
        "user": user,
        "professions": professions,
        "build_data": test_data
    }

def assert_build_matches_data(build_data: Dict[str, Any], build_in_db: Build) -> None:
    """Assert that a build in the database matches the expected data."""
    assert build_in_db.name == build_data["name"]
    assert build_in_db.description == build_data["description"]
    assert build_in_db.game_mode == build_data["game_mode"]
    assert build_in_db.team_size == build_data["team_size"]
    assert build_in_db.is_public == build_data["is_public"]
    assert build_in_db.config == build_data["config"]
    assert build_in_db.constraints == build_data["constraints"]
    assert {p.id for p in build_in_db.professions} == set(build_data["profession_ids"])


def test_generate_build(client: TestClient, db: Session) -> None:
    """Test generating a build with default parameters."""
    # Setup test data - use the test user from the client fixture
    user = client.test_user
    
    # Create some professions for testing
    professions = [ProfessionFactory() for _ in range(3)]  # Only create 3 professions to respect the schema
    db.add_all(professions)
    db.commit()
    
    # Prepare build generation request data
    build_data = {
        "team_size": 3,  # Reduced to match the maximum allowed by the schema
        "required_roles": ["healer", "dps", "support"],
        "preferred_professions": [p.id for p in professions],
        "max_duplicates": 2,
        "min_healers": 1,
        "min_dps": 1,
        "min_support": 1,
        "constraints": {
            "require_cc": True,
            "require_cleanses": True,
            "require_stability": True,
            "require_projectile_mitigation": True
        }
    }
    
    # Make request to generate build - no need to set headers as the client handles it
    print(f"Sending request to {settings.API_V1_STR}/builds/generate/ with data: {build_data}")
    response = client.post(
        f"{settings.API_V1_STR}/builds/generate/",
        json=build_data,
    )
    
    # Print full response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    
    # Parse the JSON response
    try:
        response_data = response.json()
        print("\n=== RESPONSE DATA ===")
        print(f"Success: {response_data.get('success')}")
        print(f"Message: {response_data.get('message')}")
        print(f"Build data: {response_data.get('build')}")
        print(f"Suggested composition: {response_data.get('suggested_composition')}")
        print(f"Metrics: {response_data.get('metrics')}")
        print("==================\n")
    except Exception as e:
        print(f"Error parsing response JSON: {e}")
    
    # If the response indicates an error, print more details
    if response.status_code != 200 or not response.json().get('success', False):
        print("\n=== SERVER LOGS ===")
        print("Check server logs for more details on the error.")
        print("==================\n")
    
    # Parse the response
    response_data = response.json()
    print(f"API Response: {response_data}")
    
    # Check if the response indicates failure
    if not response_data.get('success', False):
        error_msg = response_data.get('message', 'No error message provided')
        print(f"Build generation failed with message: {error_msg}")
        
        # If there's a validation error, print details
        if 'detail' in response_data:
            print(f"Validation error details: {response_data['detail']}")
        
        # Check if professions are missing
        if 'No valid professions available' in error_msg:
            # Query the database to see what professions exist
            from app.models import Profession
            profs = db.query(Profession).all()
            print(f"Available professions in DB: {[p.name for p in profs]}")
            print(f"Preferred professions in request: {build_data.get('preferred_professions', [])}")
    
    # Assert the response structure
    assert response.status_code == 200, f"Status code: {response.status_code}, Response: {response.text}"
    
    # Check if the response indicates success
    assert response_data.get('success') is True, f"Expected success=True, got {response_data.get('success')}"
    
    # Check for required fields in the response
    assert "build" in response_data, f"'build' not in response: {response_data}"
    assert "suggested_composition" in response_data, f"'suggested_composition' not in response: {response_data}"
    
    # Verify build data in the response
    build = response_data["build"]
    print(f"Build data: {build}")
    assert "id" in build, f"'id' not in build data: {build}"
    assert "name" in build, f"'name' not in build data: {build}"
    assert "description" in build, f"'description' not in build data: {build}"
    assert "game_mode" in build, f"'game_mode' not in build data: {build}"
    assert "team_size" in build, f"'team_size' not in build data: {build}"
    assert build["team_size"] == build_data["team_size"], \
        f"Expected team_size={build_data['team_size']}, got {build['team_size']}"
    
    # Verify composition data
    suggested_composition = response_data["suggested_composition"]
    print(f"Suggested composition: {suggested_composition}")
    assert isinstance(suggested_composition, list), \
        f"Expected suggested_composition to be a list, got {type(suggested_composition)}"
    assert len(suggested_composition) == build_data["team_size"], \
        f"Expected {build_data['team_size']} items in suggested_composition, got {len(suggested_composition)}"
    
    # Verify metrics
    metrics = response_data["metrics"]
    print(f"Metrics: {metrics}")
    assert "boon_coverage" in metrics, f"'boon_coverage' not in metrics: {metrics}"
    assert "role_distribution" in metrics, f"'role_distribution' not in metrics: {metrics}"
    assert "profession_distribution" in metrics, f"'profession_distribution' not in metrics: {metrics}"

def test_generate_build_unauthorized(client: TestClient, db: Session) -> None:
    """Test generating a build without authentication."""
    # Clear any authentication from the client
    client.clear_auth()
    
    # Try to generate a build without authentication
    response = client.post(
        f"{settings.API_V1_STR}/builds/generate/",
        json={
            "team_size": 5,
            "required_roles": ["healer", "dps", "support"],
            "max_duplicates": 2,
            "min_healers": 1,
            "min_dps": 2,
            "min_support": 1
        }
    )
    
    # Should return 401 Unauthorized
    assert response.status_code == 401, "Expected 401 Unauthorized when accessing protected endpoint without authentication"
    assert "Not authenticated" in response.text

def test_generate_build_invalid_data(client: TestClient, db: Session) -> None:
    """Test generating a build with invalid data."""
    # Use the test user from the client fixture
    user = client.test_user
    
    # Create some professions for testing
    professions = [ProfessionFactory() for _ in range(5)]
    db.add_all(professions)
    db.commit()
    
    # Test with invalid game mode
    invalid_data = TEST_BUILD_DATA.copy()
    invalid_data["profession_ids"] = [p.id for p in professions]
    invalid_data["game_mode"] = "invalid"
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/generate/",
        json=invalid_data,
    )
    assert response.status_code == 422
    assert "game_mode" in response.text
    
    # Test with invalid team size
    invalid_data = TEST_BUILD_DATA.copy()
    invalid_data["profession_ids"] = [p.id for p in professions]
    invalid_data["team_size"] = 0
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/generate/",
        json=invalid_data,
    )
    assert response.status_code == 422
    assert "team_size" in response.text

def test_create_build(client: TestClient, db: Session) -> None:
    """Test creating a build with valid data."""
    # Use the test client's user
    test_user = client.test_user
    
    # Create test professions
    profession1 = create_test_profession(db, name="Test Profession 1", description="Test Profession 1 Description")
    profession2 = create_test_profession(db, name="Test Profession 2", description="Test Profession 2 Description")
    db.commit()
    
    # Create test build data
    build_data = {
        "name": "Test Build",
        "description": "A test build for WvW",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {"roles": ["heal", "dps", "support"]},
        "constraints": {"max_duplicates": 2},
        "profession_ids": [profession1.id, profession2.id]
    }
    
    # Make the request with the test client (it will handle authentication)
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data
    )
    
    # Verify the response
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    
    # Parse the response
    build_response = response.json()
    assert build_response["name"] == build_data["name"]
    assert build_response["description"] == build_data["description"]
    assert build_response["created_by_id"] == test_user.id
    assert len(build_response["professions"]) == 2
    assert {p["id"] for p in build_response["professions"]} == {profession1.id, profession2.id}
    
    # Verify the build was saved to the database
    db_build = db.query(Build).filter(Build.id == build_response["id"]).first()
    assert db_build is not None
    assert db_build.name == build_data["name"]
    assert len(db_build.professions) == 2
    db.refresh(db_build)
    # Verify the build is associated with the correct professions
    assert {p.id for p in db_build.professions} == {profession1.id, profession2.id}
    
    # Verify all build data in the response
    build_response = response.json()
    assert "id" in build_response
    assert build_response["name"] == build_data["name"]
    assert build_response["description"] == build_data["description"]
    assert build_response["game_mode"] == build_data["game_mode"]
    assert build_response["team_size"] == build_data["team_size"]
    assert build_response["is_public"] == build_data["is_public"]
    assert build_response["config"] == build_data["config"]
    assert build_response["constraints"] == build_data["constraints"]
    assert len(build_response["professions"]) == len(build_data["profession_ids"])
    
    # Verify build can be retrieved
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build_response['id']}"
    )
    assert response.status_code == 200
    retrieved_build = response.json()
    assert retrieved_build["id"] == build_response["id"]
    assert retrieved_build["name"] == build_data["name"]
    assert retrieved_build["created_by_id"] == test_user.id

def test_create_duplicate_build(client: TestClient, db: Session) -> None:
    """Test creating a duplicate build (same name for same user)."""
    # Use the test client's user
    user = client.test_user
    
    # Create test professions
    from app.models.profession import Profession
    professions = []
    for i in range(2):  # Only need 2 for this test
        profession = Profession(
            name=f"Test Profession {i}",
            description=f"Test Profession {i} Description",
            icon_url=f"icon_{i}.png"
        )
        db.add(profession)
        professions.append(profession)
    db.commit()
    
    # Create build data
    build_data = TEST_BUILD_DATA.copy()
    build_data["profession_ids"] = [p.id for p in professions]
    
    # Create first build
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    assert response.status_code == 201, response.text
    
    # Try to create duplicate build
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    
    # Should fail with 400 status code
    assert response.status_code == 400, response.text
    assert "already exists" in response.json()["detail"].lower()

def test_create_build_with_nonexistent_professions(client: TestClient, db: Session) -> None:
    """Test creating a build with non-existent profession IDs."""
    # Create a valid profession first
    from app.models.profession import Profession
    profession = Profession(
        name="Test Profession",
        description="Test Profession Description",
        icon_url="test_icon.png"
    )
    db.add(profession)
    db.commit()
    
    # Create build data with one valid and one invalid profession ID
    build_data = TEST_BUILD_DATA.copy()
    build_data["profession_ids"] = [profession.id, 9999]  # One valid, one invalid
    
    # Try to create build with non-existent professions
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    
    # Should fail with 404 status code
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()

def test_create_build_validation_errors(client: TestClient, db: Session) -> None:
    """Test creating a build with invalid data (validation errors)."""
    # Create a valid profession for the tests
    from app.models.profession import Profession
    profession = Profession(name="Test Profession", description="Test", icon_url="test.png")
    db.add(profession)
    db.commit()
    
    # Create base build data with valid profession IDs
    base_build_data = TEST_BUILD_DATA.copy()
    base_build_data["profession_ids"] = [profession.id]
    
    # Test each invalid case
    for invalid_data, field, error_msg in INVALID_BUILD_DATA:
        build_data = base_build_data.copy()
        build_data.update(invalid_data)
        
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
        )
        
        assert response.status_code == 422, f"Expected 422 for {field}, got {response.status_code}"
        errors = response.json()["detail"]
        assert any(error_msg.lower() in error["msg"].lower() for error in errors), \
            f"Expected error message containing '{error_msg}' for field {field}, got: {errors}"

def test_get_build(client: TestClient, db: Session) -> None:
    """Test retrieving a build by ID."""
    # First create a build
    user = client.test_user
    
    # Create some test professions
    from app.models.profession import Profession
    profession1 = Profession(name="Test Profession 1", icon_url="icon1.png")
    profession2 = Profession(name="Test Profession 2", icon_url="icon2.png")
    db.add_all([profession1, profession2])
    db.commit()
    
    # Create build data
    build_data = TEST_BUILD_DATA.copy()
    build_data["profession_ids"] = [profession1.id, profession2.id]
    
    # Create the build using the authenticated client
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    assert response.status_code == 201, response.text
    build_id = response.json()["id"]
    
    # Now retrieve it
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build_id}",
    )
    
    # Assert response
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == build_id
    assert data["name"] == build_data["name"]
    assert data["description"] == build_data["description"]
    assert data["game_mode"] == build_data["game_mode"]
    assert data["team_size"] == build_data["team_size"]
    assert data["is_public"] == build_data["is_public"]
    assert data["config"] == build_data["config"]
    assert data["constraints"] == build_data["constraints"]
    assert len(data["professions"]) == len(build_data["profession_ids"])

def test_get_nonexistent_build(client: TestClient, db: Session) -> None:
    """Test retrieving a non-existent build."""
    # Try to get a non-existent build
    response = client.get(
        f"{settings.API_V1_STR}/builds/999999",
    )
    
    # Should return 404
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()

def test_get_private_build_unauthorized(client: TestClient, db: Session) -> None:
    """Test retrieving a private build without authorization."""
    # Create a private build owned by another user
    from app.models.user import User
    from app.models.build import Build
    from app.models.profession import Profession
    from app.models.build_profession import BuildProfession
    
    # Create another user
    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(other_user)
    
    # Create a profession
    profession = Profession(name="Test Profession", description="Test", icon_url="test.png")
    db.add(profession)
    db.commit()
    db.refresh(profession)
    
    # Create a private build owned by the other user
    build = Build(
        name="Private Build",
        description="A private build",
        game_mode="wvw",
        team_size=5,
        is_public=False,
        config={"roles": ["dps", "support"]},
        constraints={"max_duplicates": 1},
        owner_id=other_user.id
    )
    db.add(build)
    db.commit()
    db.refresh(build)
    
    # Create build-profession association
    build_profession = BuildProfession(
        build_id=build.id,
        profession_id=profession.id
    )
    db.add(build_profession)
    db.commit()
    
    # Try to access the private build
    response = client.get(
        f"{settings.API_V1_STR}/builds/{build.id}",
    )
    
    # Should return 404 (not 403) to avoid leaking existence of private builds
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()

def test_update_build(client: TestClient, db: Session) -> None:
    """Test updating a build with valid data."""
    # First create a build to update
    user = client.test_user
    
    # Create a profession for the build
    from app.models.profession import Profession
    profession = Profession(name="Test Profession", description="Test", icon_url="test.png")
    db.add(profession)
    db.commit()
    
    # Create the build
    build_data = TEST_BUILD_DATA.copy()
    build_data["profession_ids"] = [profession.id]
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    assert response.status_code == 201, response.text
    build_id = response.json()["id"]
    
    # Update the build
    update_data = {
        "name": "Updated Build Name",
        "description": "Updated description",
        "is_public": False,
        "config": {"roles": ["dps", "heal"]},
        "constraints": {"max_duplicates": 2}
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/builds/{build_id}",
        json=update_data,
    )
    
    print(f"\n=== Update Build Request ===")
    print(f"URL: {settings.API_V1_STR}/builds/{build_id}")
    print(f"Headers: {client.headers}")
    print(f"Body: {update_data}")

    print(f"\n=== Update Build Response ===")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")

    # Assert response
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]
    assert data["config"] == update_data["config"]
    assert data["constraints"] == update_data["constraints"]
    assert data["updated_at"] is not None
    
    # Verify in database
    db.refresh(build := db.get(Build, build_id))
    assert build.name == update_data["name"]
    assert build.description == update_data["description"]
    assert build.is_public == update_data["is_public"]
    assert build.config == update_data["config"]
    assert build.constraints == update_data["constraints"]

def test_update_nonexistent_build(client: TestClient, db: Session) -> None:
    """Test updating a non-existent build."""
    # Try to update a non-existent build
    update_data = {
        "name": "Updated Build Name",
        "description": "Updated description"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/builds/999999",
        json=update_data,
    )
    
    # Should return 404
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()

def test_update_build_unauthorized(client: TestClient, db: Session) -> None:
    """Test updating a build without authorization."""
    # Create a build owned by another user
    from app.models.user import User
    from app.models.build import Build
    from app.models.profession import Profession
    from app.models.build_profession import BuildProfession
    
    # Create another user
    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(other_user)
    
    # Create a profession
    profession = Profession(name="Test Profession", description="Test", icon_url="test.png")
    db.add(profession)
    db.commit()
    db.refresh(profession)
    
    # Create a build owned by the other user
    build = Build(
        name="Test Build",
        description="A test build",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        config={"roles": ["dps", "support"]},
        constraints={"max_duplicates": 1},
        owner_id=other_user.id
    )
    db.add(build)
    db.commit()
    db.refresh(build)
    
    # Create build-profession association
    build_profession = BuildProfession(
        build_id=build.id,
        profession_id=profession.id
    )
    db.add(build_profession)
    db.commit()
    
    # Try to update the build
    update_data = {
        "name": "Unauthorized Update",
        "description": "This update should fail"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/builds/{build.id}",
        json=update_data,
    )
    
    # Should return 403 Forbidden
    assert response.status_code == 403, response.text
    assert "not enough privileges" in response.json()["detail"].lower()

def test_update_build_validation_errors(client: TestClient, db: Session) -> None:
    """Test updating a build with invalid data."""
    # First create a build to update
    # Create a profession for the build
    from app.models.profession import Profession
    profession = Profession(name="Test Profession", description="Test", icon_url="test.png")
    db.add(profession)
    db.commit()
    
    # Create the build
    build_data = TEST_BUILD_DATA.copy()
    build_data["profession_ids"] = [profession.id]
    
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
    )
    assert response.status_code == 201, response.text
    build_id = response.json()["id"]
    
    # Test each invalid case
    for invalid_data, field, error_msg in INVALID_BUILD_DATA:
        update_data = {field: invalid_data[field]}
        
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build_id}",
            json=update_data,
        )
        
        assert response.status_code == 422, f"Expected 422 for {field}, got {response.status_code}"
        errors = response.json()["detail"]
        assert any(error_msg.lower() in error["msg"].lower() for error in errors), \
            f"Expected error message containing '{error_msg}' for field {field}, got: {errors}"
    
    # Should return 403 for unauthorized access
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()
    
    # Try to delete without authentication
    response = client.delete(f"{settings.API_V1_STR}/builds/{build_id}")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
    
    # Verify build still exists
    assert db.get(Build, build_id) is not None

def test_list_builds(client: TestClient, db: Session) -> None:
    """Test listing builds with various filters and pagination."""
    # Create test users
    from app.models.user import User
    from app.models.profession import Profession
    from app.models.build import Build, BuildProfession
    
    # Create test professions
    professions = []
    for i in range(5):
        profession = Profession(
            name=f"Test Profession {i}",
            description=f"Test Profession {i} Description",
            icon_url=f"icon_{i}.png"
        )
        db.add(profession)
        professions.append(profession)
    db.commit()
    
    # Get the current user from the test client
    current_user = client.test_user
    
    # Create another user
    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(other_user)
    db.commit()
    
    # Create test builds
    builds = [
        # Current user's private build
        Build(
            name="Private Build 1",
            description="A private build",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            config={"roles": ["dps", "support"]},
            constraints={"max_duplicates": 1},
            owner_id=current_user.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
        # Current user's public build
        Build(
            name="Public Build 1",
            description="A public build",
            game_mode="wvw",
            team_size=10,
            is_public=True,
            config={"roles": ["heal", "support"]},
            constraints={"max_duplicates": 2},
            owner_id=current_user.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        # Other user's public build
        Build(
            name="Other's Public Build",
            description="Another public build",
            game_mode="pve",
            team_size=5,
            is_public=True,
            config={"roles": ["dps"]},
            constraints={"max_duplicates": 3},
            owner_id=other_user.id
        ),
        # Other user's private build
        Build(
            name="Other's Private Build",
            description="A private build",
            game_mode="pvp",
            team_size=3,
            is_public=False,
            config={"roles": ["support"]},
            constraints={"max_duplicates": 1},
            owner_id=other_user.id
        )
    ]
    
    # Add builds to session
    db.add_all(builds)
    db.commit()
    
    # Add profession associations
    for i, build in enumerate(builds):
        # Each build gets 2 professions
        for j in range(2):
            profession_idx = (i + j) % len(professions)
            bp = BuildProfession(
                build_id=build.id,
                profession_id=professions[profession_idx].id
            )
            db.add(bp)
    db.commit()
    
    # Test 1: List builds as owner (should see all own builds + public from others)
    response = client.get(f"{settings.API_V1_STR}/builds/")
    assert response.status_code == 200, response.text
    content = response.json()
    
    # Should see own builds (public + private) + other's public builds
    assert len(content) >= 3
    build_names = {build["name"] for build in content}
    assert "Private Build 1" in build_names
    assert "Public Build 1" in build_names
    assert "Other's Public Build" in build_names
    assert "Other's Private Build" not in build_names
    
    # Test 2: List builds as another user (should only see public builds)
    # Create a new test client with the other user
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as other_client:
        # Set the other user as the current user for this client
        other_client.set_current_user(other_user)
        
        response = other_client.get(f"{settings.API_V1_STR}/builds/")
        assert response.status_code == 200, response.text
        content = response.json()
        
        # Should only see public builds
        assert all(build["is_public"] for build in content)
        build_names = {build["name"] for build in content}
        assert "Public Build 1" in build_names
        assert "Other's Public Build" in build_names
        assert "Private Build 1" not in build_names
        assert "Other's Private Build" not in build_names
    
    # Test 3: Filter by game mode
    response = client.get(f"{settings.API_V1_STR}/builds/?game_mode=wvw")
    assert response.status_code == 200, response.text
    content = response.json()
    assert len(content) >= 2
    assert all(build["game_mode"] == "wvw" for build in content)
    
    # Test 4: Filter by team size range
    response = client.get(f"{settings.API_V1_STR}/builds/?min_team_size=5&max_team_size=5")
    assert response.status_code == 200, response.text
    content = response.json()
    assert len(content) >= 1
    assert all(build["team_size"] == 5 for build in content)
    
    # Test 5: Pagination
    response = client.get(f"{settings.API_V1_STR}/builds/?skip=1&limit=1")
    assert response.status_code == 200, response.text
    content = response.json()
    assert len(content) == 1
    
    # Test 6: Sort by creation date (newest first)
    response = client.get(f"{settings.API_V1_STR}/builds/?sort_by=created_at&sort_order=desc")
    assert response.status_code == 200, response.text
    content = response.json()
    assert len(content) >= 2
    
    # Test 7: List builds without authentication (should only see public)
    # Create an unauthenticated client
    with TestClient(app) as anon_client:
        response = anon_client.get(f"{settings.API_V1_STR}/builds/")
        assert response.status_code == 200, response.text
        content = response.json()
        assert all(build["is_public"] for build in content)
