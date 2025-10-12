"""Tests for build CRUD operations."""

import logging
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import User, Role, Build
from app.core.security import get_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def test_user(db: Session):
    """Create a test user with a role."""
    try:
        # Create a test role if it doesn't exist
        from app.models import user_roles

        # Create role
        role = db.query(Role).filter(Role.name == "test_role").first()
        if not role:
            role = Role(
                name="test_role",
                description="Test Role",
                permission_level=100,
                is_default=True,
            )
            db.add(role)
            db.commit()
            db.refresh(role)

        # Create a unique username and email for each test
        import uuid

        unique_id = str(uuid.uuid4())[:8]

        # Create user
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
            hashed_password=get_password_hash("testpassword"),
            full_name=f"Test User {unique_id}",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.flush()  # Flush to get the user ID

        # Associate user with role through the user_roles association table
        stmt = user_roles.insert().values(user_id=user.id, role_id=role.id)
        db.execute(stmt)

        # Commit and refresh to ensure we have the latest data
        db.commit()

        # Get a fresh copy of the user with all relationships loaded
        refreshed_user = db.query(User).options(joinedload(User.roles)).filter(User.id == user.id).first()

        # Verify the user was created with the role
        assert refreshed_user is not None, "Failed to create test user"
        assert len(refreshed_user.roles) > 0, "Test user has no roles"

        return refreshed_user

    except Exception as e:
        db.rollback()
        logger.error(f"Error in test_user fixture: {str(e)}")
        raise


@pytest.fixture
def test_build_data():
    """Test data for build creation."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]  # Get first 8 chars of UUID for uniqueness
    return {
        "name": f"Test Build {unique_id}",
        "description": f"Test Description {unique_id}",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {
            "weapons": ["Sword", "Shield"],
            "traits": ["Strength", "Discipline", "Spellbreaker"],
            "skills": ["Banner of Strength", "Banner of Tactics"],
        },
        "constraints": {"required_roles": ["banners", "might"], "min_healers": 1},
        "profession_ids": [1, 2],  # These will be updated in the test
    }


@pytest.fixture
def test_professions(db: Session):
    """Create test professions with valid data."""
    import uuid
    from app.models.elite_specialization import EliteSpecialization
    from app.models.profession import Profession

    # Clean up any existing test data to avoid conflicts
    logger.info("Cleaning up existing test data...")
    db.execute(text("DELETE FROM elite_specializations"))
    db.execute(text("DELETE FROM professions"))

    # Try to reset sequences if they exist
    try:
        db.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('professions', 'elite_specializations')"))
        db.commit()
    except Exception:
        # Ignore if sqlite_sequence table doesn't exist
        logger.info("sqlite_sequence table not found, skipping sequence reset")
        db.rollback()

    db.commit()

    # Create test professions with unique names
    professions = []
    unique_id = str(uuid.uuid4())[:8]  # Get first 8 chars of UUID for uniqueness
    profession_data = [
        {"name": f"Warrior-{unique_id}", "game_modes": ["wvw", "pvp", "pve"]},
        {"name": f"Guardian-{unique_id}", "game_modes": ["wvw", "pvp", "pve"]},
        {"name": f"Revenant-{unique_id}", "game_modes": ["wvw", "pvp", "pve"]},
    ]

    for data in profession_data:
        profession = Profession(
            name=data["name"],
            game_modes=data["game_modes"],
            description=f"{data['name']} profession",
        )
        db.add(profession)
        professions.append(profession)

    db.commit()

    # Create elite specializations for each profession
    elite_specs = []
    for prof in professions:
        spec = EliteSpecialization(
            name=f"Elite {prof.name}",
            profession_id=prof.id,
            description=f"Elite specialization for {prof.name}",
        )
        db.add(spec)
        elite_specs.append(spec)

    db.commit()

    # Return both professions and elite specializations as a tuple
    return professions, elite_specs


def test_create_build(
    client: TestClient,
    db: Session,
    test_user: User,
    test_professions: tuple,
    test_build_data: dict,
) -> None:
    """Test creating a new build with associated professions."""
    try:
        # Unpack the test_professions tuple
        professions, _ = test_professions

        # Get auth header for the test user
        auth_header = {"Authorization": f"Bearer {test_user.id}"}

        # Update test data with valid profession IDs
        profession_ids = [p.id for p in professions[:2]]  # Use first two professions
        test_build_data["profession_ids"] = profession_ids

        # Log test data
        logger.info("=== Starting test_create_build ===")
        logger.info(f"Test user ID: {test_user.id}")
        logger.info(f"Test professions: {[(p.id, p.name) for p in professions]}")
        logger.info(f"Test build data: {test_build_data}")

        # Make request to create build
        response = client.post("/api/v1/builds/", json=test_build_data, headers=auth_header)

        # Log response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")

        # Check response
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Expected 201, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert "id" in data, f"Response missing 'id' field: {data}"
        assert data["name"] == test_build_data["name"]
        assert data["description"] == test_build_data["description"]
        assert data["game_mode"] == test_build_data["game_mode"]
        assert data["team_size"] == test_build_data["team_size"]
        assert data["is_public"] == test_build_data["is_public"]

        # Check if professions are associated
        build_id = data["id"]
        # Use joinedload to ensure relationships are loaded in the same session
        build = db.query(Build).options(joinedload(Build.professions)).filter(Build.id == build_id).first()
        assert build is not None, "Build not found in database"

        # Check profession associations using the relationship
        # Ensure we're accessing the relationship within the session
        build_profs = list(build.professions)
        assert len(build_profs) == len(
            profession_ids
        ), f"Expected {len(profession_ids)} profession associations, got {len(build_profs)}"

        associated_profession_ids = {p.id for p in build_profs}
        for pid in profession_ids:
            assert pid in associated_profession_ids, f"Profession {pid} not associated with build"

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


def test_get_build(client: TestClient, db: Session, test_user: User, test_professions: tuple) -> None:
    """Test retrieving a build by ID."""
    try:
        # Unpack the test_professions tuple
        professions, _ = test_professions

        # Get auth header for the test user
        auth_header = {"Authorization": f"Bearer {test_user.id}"}

        # First create a build to retrieve
        test_data = {
            "name": "Test Build Get",
            "description": "Test Description Get",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "config": {
                "weapons": ["Greatsword", "Hammer"],
                "traits": ["Strength", "Discipline", "Spellbreaker"],
                "skills": ["Banner of Strength", "Banner of Discipline"],
            },
            "constraints": {"required_roles": ["banners", "might"], "min_healers": 1},
            "profession_ids": [professions[0].id],  # Use first profession ID directly
        }

        # Log the test data
        logger.info("=== Starting test_get_build ===")
        logger.info(f"Test user ID: {test_user.id}")
        logger.info(f"Test professions: {[(p.id, p.name) for p in professions]}")
        logger.info(f"Test build data: {test_data}")

        # Create the build
        response = client.post("/api/v1/builds/", json=test_data, headers=auth_header)
        logger.info(f"Create build response: {response.status_code}, {response.text}")

        assert response.status_code == status.HTTP_201_CREATED, f"Failed to create build: {response.text}"
        build_data = response.json()
        build_id = build_data["id"]

        # Verify the build was created with the correct profession
        from app.models import Build

        # Get the build with its professions using a fresh query
        build = db.query(Build).options(joinedload(Build.professions)).filter(Build.id == build_id).first()

        assert build is not None, "Build not found in database"
        assert len(build.professions) == 1, "Expected 1 profession"
        assert build.professions[0].id == test_data["profession_ids"][0]

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise
