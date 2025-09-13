"""Integration tests for the Builds API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, List, Generator, Optional

from app.core.security import create_access_token
from app.models import User, Build, Profession, Role, user_roles
from app.schemas.build import BuildCreate, BuildUpdate, GameMode, RoleType
from app.main import app
from app.db.base import Base
from app.api.deps import get_db
import random
import string
from fastapi import status

# Constants for test data
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500

# Override the database dependency for testing
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Test data
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "A test build for WvW",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "config": {"roles": ["heal", "dps", "support"]},
    "constraints": {"max_duplicates": 2},
    "profession_ids": [1, 2, 3]
}

# Invalid test data
INVALID_BUILD_DATA = [
    ({"name": ""}, "name", "String should have at least 1 character"),
    ({"game_mode": "invalid"}, "game_mode", "Input should be 'pve','pvp', or 'wvw'"),
    ({"team_size": 0}, "team_size", "Input should be greater than or equal to 1"),
    ({"team_size": 51}, "team_size", "Input should be less than or equal to 50"),
    ({"profession_ids": []}, "profession_ids", "List should have at least 1 item after validation")
]

@pytest.fixture(scope="function")
def test_professions(db: Session) -> List[Profession]:
    """Create test professions in the database."""
    professions = []
    for i in range(1, 6):
        profession = Profession(
            id=i,
            name=f"Profession {i}",
            description=f"Test Profession {i}"
        )
        db.add(profession)
        professions.append(profession)
    db.commit()
    return professions

@pytest.fixture(scope="function")
def create_test_user(db: Session, username: str = "testuser") -> User:
    """Create a test user with a role.
    
    Args:
        db: Database session
        username: Username for the test user
        
    Returns:
        User: The created user object
    """
    # Create a role if it doesn't exist
    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        role = Role(name="user", description="Regular user role")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Create a user with required fields
    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "hashed_password": "fakehashedpassword",
        "is_active": True,
        "is_superuser": False,
        "full_name": f"Test User {username}"
    }
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """Fixture to create a test user."""
    return create_test_user(db)
    db_user = User(
        username=user_data.get("username", "testuser"),
        email=user_data["email"],
        hashed_password=user_data["hashed_password"],
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.flush()
    
    # Assign role to user using the user_roles table
    stmt = user_roles.insert().values(user_id=db_user.id, role_id=role.id)
    db.execute(stmt)
    db.commit()
    db.refresh(db_user)
    return db_user

@pytest.fixture(scope="function")
def test_build(db: Session, test_user: User, test_professions: List[Profession]) -> Build:
    """Create a test build in the database."""
    build = Build(
        name="Existing Build",
        description="An existing test build",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        config={"roles": ["dps"]},
        constraints={"max_duplicates": 1},
        owner_id=test_user.id,
        created_by_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(build)
    db.flush()
    
    # Add professions to build
    for profession in test_professions[:3]:  # Link first 3 professions
        build.professions.append(profession)
    
    db.commit()
    db.refresh(build)
    return build

def get_auth_headers(user_id: int) -> Dict[str, str]:
    """Generate authentication headers for test requests."""
    access_token = create_access_token(subject=str(user_id))
    return {"Authorization": f"Bearer {access_token}"}

class TestBuildsAPI:
    """Test suite for the Builds API endpoints."""
    
    def test_unauthorized_access(self, client: TestClient, test_build: Build, test_user: User, db: Session):
        """Test that unauthorized users cannot access private builds."""
        # Create a second test user
        other_user = create_test_user(db, username="otheruser")
        other_token = create_access_token(subject=other_user.id)
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Test accessing private build with another user's token
        response = client.get(
            f"/api/v1/builds/{test_build.id}",
            headers=other_headers
        )
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND], \
            f"Expected 403 or 404 for unauthorized access to private build, got {response.status_code}"
        
        # Make the build public
        test_build.is_public = True
        db.commit()
        
        # Now it should be accessible
        response = client.get(
            f"/api/v1/builds/{test_build.id}",
            headers=other_headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 for public build access, got {response.status_code}"
    
    def test_update_build_other_user(self, client: TestClient, test_build: Build, test_user: User, db: Session):
        """Ensure a user cannot update another user's build."""
        # Create a second user
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed_password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(user2)
        db.commit()
        
        # Try to update test_build with user2's credentials
        headers = get_auth_headers(user2.id)
        update_data = {"name": "Unauthorized Update"}
        
        response = client.put(
            f"/builds/{test_build.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()
        
        # Verify build was not updated
        db.refresh(test_build)
        assert test_build.name != "Unauthorized Update"
    
    def test_delete_build_unauthorized(self, client: TestClient, test_build: Build, db: Session):
        """Test deleting a build without proper authorization."""
        # Test without authentication
        response = client.delete(f"/builds/{test_build.id}")
        assert response.status_code == 401
        
        # Create a second user with limited permissions
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed_password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(user2)
        db.commit()
        
        # Test with unauthorized user
        headers = get_auth_headers(user2.id)
        response = client.delete(f"/builds/{test_build.id}", headers=headers)
        assert response.status_code == 403
    
    def test_create_build_with_max_team_size(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test creating a build with the maximum allowed team size."""
        headers = get_auth_headers(test_user.id)
        max_team_data = TEST_BUILD_DATA.copy()
        max_team_data["team_size"] = 50  # Maximum allowed
        
        response = client.post("/builds/", json=max_team_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["team_size"] == 50
    
    def test_create_build_empty_name(self, client: TestClient, test_user: User):
        """Test creating a build with empty name."""
        headers = get_auth_headers(test_user.id)
        invalid_data = TEST_BUILD_DATA.copy()
        invalid_data["name"] = ""
        
        response = client.post("/builds/", json=invalid_data, headers=headers)
        assert response.status_code == 422
        assert "name" in str(response.json()["detail"][0]["loc"])
    
    def test_create_build_long_name(self, client: TestClient, test_user: User):
        """Test creating a build with a name that's too long."""
        headers = get_auth_headers(test_user.id)
        invalid_data = TEST_BUILD_DATA.copy()
        invalid_data["name"] = "x" * 256  # Assuming 255 is the max length
        
        response = client.post("/builds/", json=invalid_data, headers=headers)
        assert response.status_code == 422
        assert "name" in str(response.json()["detail"][0]["loc"])
    
    def test_update_build_remove_all_professions(self, client: TestClient, test_build: Build, test_user: User):
        """Test updating a build to remove all professions."""
        headers = get_auth_headers(test_user.id)
        
        # Verify build has professions initially
        response = client.get(f"/builds/{test_build.id}", headers=headers)
        assert len(response.json()["professions"]) > 0
        
        # Update with empty profession list
        response = client.put(
            f"/builds/{test_build.id}",
            json={"profession_ids": []},
            headers=headers
        )
        
        # Should return 422 as we require at least one profession
        assert response.status_code == 422
        assert "profession_ids" in str(response.json()["detail"][0]["loc"])
    
    def test_create_build(self, client: TestClient, db: Session, test_user: User, test_professions: List[Profession]):
        """Test creating a build with valid data."""
        headers = get_auth_headers(test_user.id)
        response = client.post(
            "/builds/",
            json=TEST_BUILD_DATA,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == TEST_BUILD_DATA["name"]
        assert data["description"] == TEST_BUILD_DATA["description"]
        assert data["game_mode"] == TEST_BUILD_DATA["game_mode"]
        assert data["team_size"] == TEST_BUILD_DATA["team_size"]
        assert data["is_public"] == TEST_BUILD_DATA["is_public"]
        assert data["owner_id"] == test_user.id
        assert len(data["professions"]) == len(TEST_BUILD_DATA["profession_ids"])
    
    @pytest.mark.parametrize("invalid_data,field,error_message", INVALID_BUILD_DATA)
    def test_create_build_validation_errors(
        self, 
        client: TestClient, 
        test_user: User, 
        invalid_data: Dict[str, Any], 
        field: str, 
        error_message: str
    ):
        """Test creating a build with invalid data."""
        headers = get_auth_headers(test_user.id)
        data = TEST_BUILD_DATA.copy()
        data.update(invalid_data)
        
        response = client.post("/builds/", json=data, headers=headers)
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(field in str(error["loc"]) and error_message in str(error) for error in errors)
    
    def test_get_build(self, client: TestClient, test_build: Build, test_user: User):
        """Test retrieving a build by ID."""
        headers = get_auth_headers(test_user.id)
        response = client.get(f"/builds/{test_build.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_build.id
        assert data["name"] == test_build.name
        assert len(data["professions"]) == 3  # Should have 3 professions from fixture
    
    def test_update_build(self, client: TestClient, test_build: Build, test_user: User):
        """Test updating a build."""
        headers = get_auth_headers(test_user.id)
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
            "is_public": False,
            "profession_ids": [1, 2]  # Update to only 2 professions
        }
        
        response = client.put(
            f"/builds/{test_build.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_public"] == update_data["is_public"]
        assert len(data["professions"]) == 2  # Should now have 2 professions
    
    def test_delete_build(self, client: TestClient, test_build: Build, test_user: User, db: Session):
        """Test deleting a build."""
        headers = get_auth_headers(test_user.id)
        
        # First, verify the build exists
        response = client.get(f"/builds/{test_build.id}", headers=headers)
        assert response.status_code == 200
        
        # Delete the build
        response = client.delete(f"/builds/{test_build.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_build.id
        
        # Verify the build is deleted
        response = client.get(f"/builds/{test_build.id}", headers=headers)
        assert response.status_code == 404
    
    def test_list_builds_pagination_boundaries(self, client: TestClient, test_user: User, test_build: Build, db: Session):
        """Test pagination boundaries and edge cases."""
        headers = get_auth_headers(test_user.id)
        
        # Create additional test builds
        for i in range(15):
            build = Build(
                name=f"Test Build {i}",
                description=f"Test Build {i} Description",
                game_mode="wvw",
                team_size=5,
                is_public=True,
                config={"roles": ["dps"]},
                constraints={},
                owner_id=test_user.id,
                created_by_id=test_user.id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(build)
        db.commit()
        
        # Test valid pagination
        response = client.get("/builds/", headers=headers, params={"skip": 5, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        # Test requesting page beyond available data
        response = client.get("/builds/", headers=headers, params={"skip": 100, "limit": 10})
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # Test invalid pagination parameters
        response = client.get("/builds/", headers=headers, params={"skip": -1, "limit": 10})
        assert response.status_code == 422
        
        response = client.get("/builds/", headers=headers, params={"skip": 0, "limit": 0})
        assert response.status_code == 422
    
    def test_list_builds_filter_invalid(self, client: TestClient, test_user: User, test_build: Build):
        """Test filtering with invalid parameters."""
        headers = get_auth_headers(test_user.id)
        
        # Test with non-existent profession
        response = client.get(
            "/builds/", 
            headers=headers, 
            params={"profession_id": 9999}
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
        
        # Test with invalid game mode
        response = client.get(
            "/builds/", 
            headers=headers, 
            params={"game_mode": "invalid"}
        )
        assert response.status_code == 422
    
    def test_list_builds_private_vs_public(self, client: TestClient, test_user: User, db: Session):
        """Test that private builds are only visible to their owners."""
        # Create a second user
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed_password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(user2)
        db.flush()
        
        # Create a private build for test_user
        private_build = Build(
            name="Private Build",
            description="A private build",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            config={"roles": ["dps"]},
            constraints={},
            owner_id=test_user.id,
            created_by_id=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(private_build)
        
        # Create a public build for user2
        public_build = Build(
            name="Public Build",
            description="A public build",
            game_mode="pvp",
            team_size=3,
            is_public=True,
            config={"roles": ["support"]},
            constraints={},
            owner_id=user2.id,
            created_by_id=user2.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(public_build)
        db.commit()
        
        # Test user should see their private build and the public one
        headers = get_auth_headers(test_user.id)
        response = client.get("/builds/", headers=headers)
        assert response.status_code == 200
        builds = response.json()
        assert len(builds) == 2
        assert any(b["name"] == "Private Build" for b in builds)
        assert any(b["name"] == "Public Build" for b in builds)
        
        # User2 should only see the public build
        headers = get_auth_headers(user2.id)
        response = client.get("/builds/", headers=headers)
        assert response.status_code == 200
        builds = response.json()
        assert len(builds) == 1
        assert builds[0]["name"] == "Public Build"
    
    def test_list_builds(self, client: TestClient, test_build: Build, test_user: User):
        """Test listing builds with pagination."""
        headers = get_auth_headers(test_user.id)
        
        # Create a second build
        build2 = Build(
            name="Second Build",
            description="Another test build",
            game_mode="pvp",
            team_size=3,
            is_public=True,
            config={"roles": ["dps"]},
            constraints={"max_duplicates": 1},
            owner_id=test_user.id,
            created_by_id=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db = test_build.Session()
        db.add(build2)
        db.commit()
        
        # Test listing all builds
        response = client.get("/builds/", headers=headers, params={"skip": 0, "limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should return both builds
        
        # Test pagination
        response = client.get("/builds/", headers=headers, params={"skip": 1, "limit": 1})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Should return only one build due to pagination
        
        # Test filtering by game_mode
        response = client.get("/builds/", headers=headers, params={"game_mode": "pvp"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["game_mode"] == "pvp"

    def test_update_build_with_professions(self, client: TestClient, test_build: Build, test_user: User, test_professions: List[Profession]):
        """Test updating a build's professions."""
        headers = get_auth_headers(test_user.id)
        
        # Update build with different professions
        update_data = {
            "profession_ids": [4, 5]  # Different professions than the fixture
        }
        
        response = client.put(
            f"/builds/{test_build.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["professions"]) == 2
        assert all(p["id"] in [4, 5] for p in data["professions"])
        
        # Verify the update in the database
        db = test_build.Session()
        updated_build = db.query(Build).filter(Build.id == test_build.id).first()
        assert len(updated_build.professions) == 2
        assert {p.id for p in updated_build.professions} == {4, 5}
    
    def test_update_build_nonexistent_professions(self, client: TestClient, test_build: Build, test_user: User):
        """Test updating a build with non-existent profession IDs."""
        headers = get_auth_headers(test_user.id)
        
        update_data = {
            "profession_ids": [999, 1000]  # Non-existent profession IDs
        }
        
        response = client.put(
            f"/builds/{test_build.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

class TestBuildGeneration:
    """Test suite for the build generation endpoint."""
    
    def test_generate_build_no_constraints(self, client: TestClient, test_user: User):
        """Test generating a build with default parameters."""
        headers = {"Authorization": f"Bearer {create_access_token(subject=test_user.id)}"}
        
        response = client.post(
            "/api/v1/builds/generate",
            json={},
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "build" in data
        assert "team" in data
        
    def test_generate_build_conflicting_constraints(self, client: TestClient, test_user: User):
        """Test generating a build with impossible constraints."""
        headers = {"Authorization": f"Bearer {create_access_token(subject=test_user.id)}"}
        
        # Request more healers than team size
        data = {
            "team_size": 5,
            "min_healers": 6  # More than team size
        }
        
        response = client.post(
            "/api/v1/builds/generate",
            json=data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_generate_build_excluded_professions(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build when excluding all available professions."""
        headers = {"Authorization": f"Bearer {create_access_token(subject=test_user.id)}"}
        
        # Exclude all available professions
        data = {
            "excluded_professions": [p.id for p in test_professions]
        }
        
        response = client.post(
            "/api/v1/builds/generate",
            json=data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_build_no_constraints(self, client: TestClient, test_user: User):
        """Test generating a build with default parameters (no constraints)."""
        headers = get_auth_headers(test_user.id)
        
        response = client.post(
            "/generate/",
            json={"team_size": 5, "game_mode": "wvw"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["suggested_composition"]) == 5
    
    def test_generate_build_conflicting_constraints(self, client: TestClient, test_user: User):
        """Test generating a build with impossible constraints."""
        headers = get_auth_headers(test_user.id)
        
        # Test with min_healers > team_size
        response = client.post(
            "/generate/",
            json={
                "team_size": 3,
                "game_mode": "wvw",
                "constraints": {"min_healers": 4}  # More than team size
            },
            headers=headers
        )
        
        assert response.status_code == 422
        assert "constraints" in str(response.json()["detail"][0]["loc"])
        
        # Test with min_dps + min_healers > team_size
        response = client.post(
            "/generate/",
            json={
                "team_size": 5,
                "game_mode": "wvw",
                "constraints": {"min_dps": 3, "min_healers": 3}
            },
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_generate_build_excluded_professions(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build when excluding all available professions."""
        headers = get_auth_headers(test_user.id)
        
        # Get all profession IDs to exclude them all
        all_profession_ids = [p.id for p in test_professions]
        
        response = client.post(
            "/generate/",
            json={
                "team_size": 5,
                "game_mode": "wvw",
                "excluded_professions": all_profession_ids
            },
            headers=headers
        )
        
        assert response.status_code == 400
        assert "no available professions" in response.json()["detail"].lower()

class TestBuildGeneration:
    
    def test_generate_build(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build with default parameters."""
        headers = get_auth_headers(test_user.id)
        generation_data = {
            "team_size": 5,
            "game_mode": "wvw",
            "constraints": {
                "min_healers": 1,
                "min_dps": 2,
                "min_support": 1
            }
        }
        
        response = client.post("/generate/", json=generation_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "build" in data
        assert "suggested_composition" in data
        assert "metrics" in data
        
        # Verify the build was created with the expected structure
        build = data["build"]
        assert build["game_mode"] == "wvw"
        assert build["team_size"] == 5
        
        # Verify the composition meets the constraints
        composition = data["suggested_composition"]
        assert len(composition) == 5  # Should match team_size
        
        # Verify metrics are calculated correctly
        metrics = data["metrics"]
        assert "role_distribution" in metrics
        assert metrics["role_distribution"].get("healer", 0) >= 1
        assert metrics["role_distribution"].get("dps", 0) >= 2
        assert metrics["role_distribution"].get("support", 0) >= 1
    
    def test_generate_build_unauthorized(self, client: TestClient):
        """Test generating a build without authentication."""
        generation_data = {
            "team_size": 5,
            "game_mode": "wvw"
        }
        
        response = client.post("/generate/", json=generation_data)
        assert response.status_code == 401  # Unauthorized
    
    def test_generate_build_invalid_data(self, client: TestClient, test_user: User):
        """Test generating a build with invalid data."""
        headers = get_auth_headers(test_user.id)
        
        test_cases = [
            ({"team_size": 0, "game_mode": "wvw"}, "team_size"),  # Team size too small
            ({"team_size": 51, "game_mode": "wvw"}, "team_size"),  # Team size too large
            ({"team_size": 5, "game_mode": "invalid"}, "game_mode"),  # Invalid game mode
            ({"team_size": 5, "game_mode": "wvw", "constraints": {"min_healers": -1}}, "min_healers"),  # Negative min_healers
            ({"team_size": 5, "game_mode": "wvw", "constraints": {"min_dps": 6}}, "min_dps"),  # min_dps > team_size
        ]
        
        for data, error_field in test_cases:
            response = client.post("/generate/", json=data, headers=headers)
            assert response.status_code == 422
            errors = response.json()["detail"]
            assert any(error_field in str(error["loc"]) for error in errors), \
                   f"Expected error for field {error_field} not found in {errors}"
    
    def test_generate_build_with_specific_roles(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build with specific role requirements."""
        headers = get_auth_headers(test_user.id)
        
        # Test with specific role requirements
        generation_data = {
            "team_size": 5,
            "game_mode": "wvw",
            "constraints": {
                "required_roles": ["healer", "quickness", "alacrity"],
                "min_healers": 1,
                "min_dps": 2,
                "min_support": 1
            }
        }
        
        response = client.post("/generate/", json=generation_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify required roles are covered in the composition
        composition = data["suggested_composition"]
        roles = [member["role"].lower() for member in composition]
        assert any("heal" in role for role in roles)
        assert any("quickness" in role for role in roles)
        assert any("alacrity" in role for role in roles)
    
    def test_generate_build_with_profession_preferences(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build with preferred professions."""
        headers = get_auth_headers(test_user.id)
        
        # Get IDs of the first two test professions
        preferred_professions = [test_professions[0].id, test_professions[1].id]
        
        generation_data = {
            "team_size": 3,
            "game_mode": "wvw",
            "preferred_professions": preferred_professions,
            "constraints": {
                "min_healers": 1,
                "min_dps": 1,
                "min_support": 1
            }
        }
        
        response = client.post("/generate/", json=generation_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify preferred professions are used in the composition
        composition = data["suggested_composition"]
        profession_ids = {member["profession_id"] for member in composition if "profession_id" in member}
        assert any(pid in preferred_professions for pid in profession_ids)

class TestBuildDataIntegrity:
    """Test suite for data integrity in build operations."""
    
    def test_build_deletion_cascades(self, client: TestClient, test_user: User, test_build: Build, db: Session):
        """Verify that deleting a build removes all related data."""
        # Get build ID before deletion
        build_id = test_build.id
        
        # Delete the build
        headers = {"Authorization": f"Bearer {create_access_token(subject=test_user.id)}"}
        response = client.delete(
            f"/api/v1/builds/{build_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify build is deleted
        deleted_build = db.query(Build).filter(Build.id == build_id).first()
        assert deleted_build is None
        
        # Verify build-profession associations are deleted
        from app.models.build import build_profession
        stmt = build_profession.select().where(build_profession.c.build_id == build_id)
        result = db.execute(stmt).fetchall()
        assert len(result) == 0
        
    def test_transactional_integrity(self, client: TestClient, test_user: User, db: Session):
        """Test that failed operations don't leave partial data."""
        headers = {"Authorization": f"Bearer {create_access_token(subject=test_user.id)}"}
        
        # Try to create a build with an invalid profession ID
        build_data = {
            "name": "Test Build with Invalid Profession",
            "game_mode": "wvw",
            "profession_ids": [99999],  # Non-existent profession
            "config": {},
            "constraints": {}
        }
        
        # This should fail with 422
        response = client.post(
            "/api/v1/builds/",
            json=build_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verify no build was created
        build = db.query(Build).filter(Build.name == "Test Build with Invalid Profession").first()
        assert build is None
    
    def test_build_deletion_cascades(self, client: TestClient, test_user: User, test_build: Build, db: Session):
        """Verify that deleting a build removes all related data."""
        # Get build's profession associations
        build_id = test_build.id
        stmt = text("""
            SELECT * FROM build_profession_association 
            WHERE build_id = :build_id
        """)
        result = db.execute(stmt, {"build_id": build_id})
        assert result.rowcount > 0, "No profession associations found"
        
        # Delete the build
        headers = get_auth_headers(test_user.id)
        response = client.delete(f"/builds/{build_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify build is deleted
        assert db.query(Build).filter(Build.id == build_id).first() is None
        
        # Verify profession associations are deleted (should be handled by SQLAlchemy's cascade)
        result = db.execute(stmt, {"build_id": build_id})
        assert result.rowcount == 0, "Build-profession associations not deleted"
    
    def test_transactional_integrity(self, client: TestClient, test_user: User, db: Session):
        """Test that failed operations don't leave partial data."""
        headers = get_auth_headers(test_user.id)
        
        # Create test data that will cause a failure
        invalid_data = TEST_BUILD_DATA.copy()
        invalid_data["profession_ids"] = [999]  # Non-existent profession
        
        # Count builds before the test
        initial_count = db.query(Build).count()
        
        # This should fail due to non-existent profession
        response = client.post("/builds/", json=invalid_data, headers=headers)
        assert response.status_code == 404
        
        # Verify no partial build was created
        assert db.query(Build).count() == initial_count
        
        # Verify no build-profession associations were created
        result = db.execute("""
            SELECT COUNT(*) FROM build_profession_association 
            WHERE build_id NOT IN (SELECT id FROM builds)
        """)
        assert result.scalar() == 0, "Orphaned build-profession associations found"
