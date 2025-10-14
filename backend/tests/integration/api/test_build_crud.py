"""Tests for build CRUD operations."""

import logging
import sys
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import settings first to ensure environment is set up correctly
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.profession import Profession

# Import test utilities
from tests.integration.fixtures.factories import BuildFactory, UserFactory, ProfessionFactory

# Import CRUD operations
from app.crud.build import build as build_crud

# Import schemas

# Import test client

# Create a new test database session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    from sqlalchemy import event

    # Create all tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Create a new database session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction
    connection.begin_nested()

    # If the application code calls commit, it will end the nested transaction
    # So we need to start a new one
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    logger.info("Database session created")

    # Yield the session for testing
    yield session

    # Cleanup
    logger.info("Cleaning up database...")
    session.close()
    transaction.rollback()
    connection.close()
    logger.info("Database cleanup complete")


@pytest.mark.asyncio
async def test_create_build(async_client, async_session) -> None:
    """Test creating a new build with associated professions."""
    logger.info("=== Starting test_create_build ===")

    try:
        # Get the async session
        db = async_session

        # Create a test user
        test_user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            full_name="Test User",
        )

        # Add and commit the user
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)

        logger.info(f"Created test user with ID: {test_user.id}")

        # Create test professions
        logger.info("Creating test professions...")
        professions = []
        for i in range(3):
            prof = Profession(
                name=f"Test Profession {i}",
                description=f"Test Description {i}",
                icon_url=f"http://example.com/icon{i}.png",
            )
            db.add(prof)
            await db.commit()
            await db.refresh(prof)
            professions.append(prof)

        logger.info(f"Created {len(professions)} test professions with IDs: {[p.id for p in professions]}")

        # Create test build data with the profession IDs
        profession_ids = [p.id for p in professions]

        # Test data - match the expected schema in BuildCreate and BUILD_CREATE_EXAMPLE
        build_data = {
            "name": "Test Build CRUD",
            "description": "A test build for CRUD operations",
            "game_mode": "wvw",  # Required field
            "team_size": 5,  # Required field
            "is_public": True,
            "profession_ids": profession_ids,
            "config": {
                "weapons": ["Greatsword", "Staff"],
                "traits": ["Dragonhunter", "Zeal", "Radiance"],
                "skills": ["Merciful Intervention", "Sword of Justice"],
            },
            "constraints": {"min_healers": 1, "min_dps": 3, "min_support": 1},
            "created_by_id": test_user.id,
        }

        # Commit the current transaction to ensure professions are visible
        db.commit()

        # Log the build data being sent
        logger.info("=== Build creation request data ===")
        import json

        logger.info(json.dumps(build_data, indent=2))

        # Create an authentication token for the test user
        from app.core.security import create_access_token

        token = create_access_token(subject=test_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        # Send the request to create a new build
        logger.info("Sending POST request to /api/v1/builds/")
        response = await async_client.post("/api/v1/builds/", json=build_data, headers=headers)

        # Check the response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")

        # Verify the response
        assert (
            response.status_code == 201
        ), f"Expected status code 201, got {response.status_code}. Response: {response.text}"

        # Parse the response
        created_build = response.json()
        logger.info(f"Created build: {json.dumps(created_build, indent=2)}")

        # Verify the build was created with the correct data
        assert created_build["name"] == build_data["name"]
        assert created_build["description"] == build_data["description"]
        assert created_build["game_mode"] == build_data["game_mode"]
        assert created_build["is_public"] == build_data["is_public"]
        assert created_build["created_by"]["id"] == str(test_user.id)

        # Verify the professions were associated correctly
        assert len(created_build["professions"]) == len(profession_ids)
        created_profession_ids = [str(p["id"]) for p in created_build["professions"]]
        for pid in profession_ids:
            assert str(pid) in created_profession_ids, f"Profession {pid} not found in created build"

        logger.info("=== Test test_create_build completed successfully ===")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        logger.exception("Error details:")
        raise
    finally:
        # Clean up test data
        try:
            # Delete test build if it was created
            if "created_build" in locals():
                await async_client.delete(f"/api/v1/builds/{created_build['id']}", headers=headers)

            # Delete test professions
            for prof in professions:
                await db.delete(prof)

            # Delete test user
            if "test_user" in locals():
                await db.delete(test_user)

            await db.commit()
            logger.info("Test data cleanup complete")

        except Exception as cleanup_error:
            logger.error(f"Error during test cleanup: {str(cleanup_error)}")
            logger.exception("Cleanup error details:")
            # Don't raise the cleanup error to avoid masking the original test error

        # Get response data
        try:
            response_data = response.json()
            logger.info("=== Build Creation Response ===")
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Response body: {json.dumps(response_data, indent=2, default=str)}")

            # If the response is an error, log more details
            if response.status_code >= 400:
                logger.error(f"Request failed with status {response.status_code}")
                raise AssertionError(f"API request failed with status {response.status_code}: {response.text}")

        except Exception as e:
            logger.error("\n=== Error during request ===")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        # Verify response status code (201 Created)
        assert (
            response.status_code == 201
        ), f"Expected status code 201, got {response.status_code}. Response: {response.text}"

        # Parse and verify the response
        content = response.json()
        logger.info("\n=== Verifying response structure ===")

        # Basic response validation
        required_fields = ["id", "name", "description", "is_public", "created_by", "professions"]
        for field in required_fields:
            assert field in content, f"Missing required field: {field}"

        # Verify build data matches request
        assert content["name"] == build_data["name"], "Build name mismatch"
        assert content["description"] == build_data["description"], "Build description mismatch"
        assert content["is_public"] == build_data["is_public"], "Build visibility mismatch"

        # Verify creator information
        assert content["created_by"]["id"] == str(test_user.id), "Creator ID mismatch"
        assert content["created_by"]["email"] == test_user.email, "Creator email mismatch"

        # Verify professions
        response_professions = content.get("professions", [])
        logger.info(f"Found {len(response_professions)} professions in response")
        assert len(response_professions) == len(
            professions
        ), f"Expected {len(professions)} professions, got {len(response_professions)}"

        # Verify the build was actually created in the database
        logger.info("\n=== Verifying database state ===")

        # Query the build with all relationships loaded
        from sqlalchemy.orm import joinedload
        from app import models

        try:
            db_build = (
                db.query(models.Build)
                .options(
                    joinedload(models.Build.build_professions).joinedload(models.BuildProfession.profession),
                    joinedload(models.Build.professions),
                )
                .filter(models.Build.id == content["id"])
                .first()
            )

            assert db_build is not None, "Build was not created in the database"
            assert db_build.name == build_data["name"], f"Expected name {build_data['name']}, got {db_build.name}"
            assert (
                db_build.created_by_id == test_user.id
            ), f"Expected created_by_id {test_user.id}, got {db_build.created_by_id}"

            # Log the build object and its relationships
            logger.info(f"Build from DB: id={db_build.id}, name={db_build.name}")

            # Verify build_professions
            assert hasattr(db_build, "build_professions"), "Build has no build_professions attribute"
            logger.info(f"Found {len(db_build.build_professions)} build_professions")

            for bp in db_build.build_professions:
                logger.info(f"  - BuildProfession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                if hasattr(bp, "profession") and bp.profession:
                    logger.info(f"    - Profession: id={bp.profession.id}, name={bp.profession.name}")

            # Verify professions
            assert hasattr(db_build, "professions"), "Build has no professions attribute"
            logger.info(f"Found {len(db_build.professions)} professions")

            for p in db_build.professions:
                logger.info(f"  - Profession: id={p.id}, name={p.name}")

            # Verify the professions are associated correctly
            assert len(db_build.professions) == len(
                professions
            ), f"Expected {len(professions)} professions, got {len(db_build.professions)}"

            # Verify the profession IDs match
            db_profession_ids = {p.id for p in db_build.professions}
            expected_profession_ids = {p.id for p in professions}
            assert (
                db_profession_ids == expected_profession_ids
            ), f"Expected profession IDs {expected_profession_ids}, got {db_profession_ids}"

            logger.info("=== Test completed successfully ===")

        except Exception as e:
            logger.error("\n=== Error during database verification ===")
            logger.error(f"Error: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise  # Re-raise the exception to fail the test


def test_get_build(client: TestClient, db: Session) -> None:
    """Test retrieving a build by ID."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)

        # Set the current user for the test client
        client.set_current_user(test_user)

        # Test
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")

        # Verify
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()
        assert content["id"] == build.id
        assert content["owner_id"] == test_user.id, f"Expected owner_id {test_user.id}, got {content.get('owner_id')}"

    except Exception as e:
        print(f"Error in test_get_build: {str(e)}")
        if "response" in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_list_builds(client: TestClient, db: Session) -> None:
    """Test listing builds with different visibility settings."""
    try:
        # Setup users
        test_user = client._test_user
        other_user = UserFactory()

        # Create builds with different visibility
        public_build = BuildFactory(created_by_id=test_user.id, is_public=True)
        private_build = BuildFactory(created_by_id=test_user.id, is_public=False)
        other_public_build = BuildFactory(created_by_id=other_user.id, is_public=True)

        db.add_all([other_user, public_build, private_build, other_public_build])
        db.commit()

        # Test as authenticated user - should see their builds plus public ones
        client.set_current_user(test_user)
        response = client.get(f"{settings.API_V1_STR}/builds/")

        # Verify authenticated user can see their builds and public ones
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        build_ids = {b["id"] for b in builds}

        assert public_build.id in build_ids, "User should see their own public builds"
        assert private_build.id in build_ids, "User should see their own private builds"
        assert other_public_build.id in build_ids, "User should see public builds from other users"

        # Test as anonymous user - should only see public builds
        client.clear_auth()
        response = client.get(f"{settings.API_V1_STR}/builds/")

        # Verify anonymous user can only see public builds
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        build_ids = {b["id"] for b in builds}

        assert public_build.id in build_ids, "Public builds should be visible to anonymous users"
        assert private_build.id not in build_ids, "Private builds should not be visible to anonymous users"
        assert other_public_build.id in build_ids, "Public builds from other users should be visible to anonymous users"

    except Exception as e:
        print(f"Error in test_list_builds: {str(e)}")
        if "response" in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_update_build(client: TestClient, db: Session) -> None:
    """Test updating a build."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)

        # Create some test professions for the update
        new_professions = [ProfessionFactory() for _ in range(2)]
        db.add_all(new_professions)
        db.commit()

        # Set the current user for the test client
        client.set_current_user(test_user)

        # Test data for update
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
            "is_public": True,
            "config": {"roles": ["support", "dps"]},
            "constraints": {"max_duplicates": 3},
            "profession_ids": [p.id for p in new_professions],
        }

        # Test update
        response = client.put(f"{settings.API_V1_STR}/builds/{build.id}", json=update_data)

        # Verify response
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()

        # Verify response data
        assert content["name"] == update_data["name"]
        assert content["description"] == update_data["description"]
        assert content["is_public"] is True
        assert content["config"] == update_data["config"]
        assert content["constraints"] == update_data["constraints"]
        assert len(content["professions"]) == len(new_professions)

        # Verify database was updated
        db.refresh(build)
        assert build.name == update_data["name"]
        assert build.description == update_data["description"]
        assert build.is_public is True
        assert build.config == update_data["config"]
        assert build.constraints == update_data["constraints"]
        assert {p.id for p in build.professions} == {p.id for p in new_professions}

    except Exception as e:
        print(f"Error in test_update_build: {str(e)}")
        if "response" in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_delete_build(client: TestClient, db: Session) -> None:
    """Test deleting a build."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)

        # Set the current user for the test client
        client.set_current_user(test_user)

        # Test delete
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")

        # Verify response
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()
        assert content["id"] == build.id
        assert content["is_deleted"] is True

        # Verify soft delete in database
        db.refresh(build)
        assert build.is_deleted is True
        assert build.deleted_at is not None

        # Verify the build is not returned in list
        response = client.get(f"{settings.API_V1_STR}/builds/")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        assert all(b["id"] != build.id for b in builds), "Deleted build should not appear in list"

    except Exception as e:
        print(f"Error in test_delete_build: {str(e)}")
        if "response" in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_unauthorized_access(client: TestClient, db: Session) -> None:
    """Test unauthorized access to build operations."""
    try:
        # Setup users
        owner = UserFactory()
        other_user = UserFactory()
        build = BuildFactory(created_by_id=owner.id, is_public=False)
        db.add_all([owner, other_user, build])
        db.commit()
        db.refresh(build)

        # Test 1: Other user cannot access private build
        client.set_current_user(other_user)
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 403, "Other users should not be able to access private builds"

        # Test 2: Other user cannot update build
        response = client.put(f"{settings.API_V1_STR}/builds/{build.id}", json={"name": "Unauthorized Update"})
        assert response.status_code == 403, "Other users should not be able to update builds"

        # Test 3: Other user cannot delete build
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 403, "Other users should not be able to delete builds"

        # Test 4: Anonymous user cannot access private build
        client.clear_auth()
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code in [401, 403], "Anonymous users should not be able to access private builds"

        # Test 5: Owner can access their private build
        client.set_current_user(owner)
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 200, "Owners should be able to access their private builds"

        # Test 6: Owner can update their build
        update_data = {"name": "Authorized Update"}
        response = client.put(f"{settings.API_V1_STR}/builds/{build.id}", json=update_data)
        assert response.status_code == 200, "Owners should be able to update their builds"

        # Test 7: Owner can delete their build
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 200, "Owners should be able to delete their builds"

        # Verify build was actually deleted
        db_build = build_crud.get(db, id=build.id)
        assert db_build is None or db_build.is_deleted is True, "Build should be deleted or marked as deleted"

    except Exception as e:
        print(f"Error in test_unauthorized_access: {str(e)}")
        if "response" in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test
    assert response.status_code in [401, 403], "Anonymous users should not be able to access private builds"

    # Test 5: Owner can access their private build
    client.set_current_user(owner)
    response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
    assert response.status_code == 200, "Owners should be able to access their private builds"

    # Test 6: Owner can update their build
    update_data = {"name": "Authorized Update"}
    response = client.put(f"{settings.API_V1_STR}/builds/{build.id}", json=update_data)
    assert response.status_code == 200, "Owners should be able to update their builds"

    # Test 7: Owner can delete their build
    response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
    assert response.status_code == 200, "Owners should be able to delete their builds"

    # Verify build was actually deleted
    from app.crud.build import build as build_crud

    db_build = build_crud.get(db, id=build.id)
    assert db_build is None, "Build should be deleted from the database"
