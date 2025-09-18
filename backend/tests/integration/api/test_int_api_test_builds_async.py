"""Integration tests for the Builds API endpoints using async/await.

This module contains comprehensive tests for the Builds API endpoints, including:
- CRUD operations (Create, Read, Update, Delete)
- Authentication and authorization
- Data validation and error handling
- Edge cases and boundary conditions
- Performance and concurrency

All tests use async/await patterns and the async test client for maximum
performance and reliability.
"""
import asyncio
import json
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

import pytest
from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient, Response
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.crud import build as crud_build, user as crud_user, profession as crud_profession, role as crud_role
from app.models import Build, Profession, Role, User, build_profession, user_roles
from app.schemas.build import BuildCreate, BuildUpdate, GameMode, RoleType, BuildInDB
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from app.schemas.role import RoleCreate, RoleUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for testing
TEST_PASSWORD = "testpass123"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_USERNAME = "testuser"
ADMIN_EMAIL = "admin@example.com"
ADMIN_USERNAME = "admin"

# Test data templates
# Using fixtures from conftest.py instead of direct factory calls
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "A test build for WvW",
    "game_mode": GameMode.WVW,
    "team_size": 5,
    "is_public": True,
    "config": {"roles": ["heal", "dps", "support"]},
    "constraints": {"max_duplicates": 2},
}

# Helper functions
def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string of specified length."""
    return "".join(random.choices(string.ascii_lowercase, k=length))

def random_email() -> str:
    """Generate a random email address for testing."""
    return f"{random_lower_string(8)}@example.com"

def random_username() -> str:
    """Generate a random username for testing."""
    return f"user_{random_lower_string(6)}"

# Fixtures for test data
@pytest.fixture(scope="function")
async def test_role(role_factory: Callable) -> Role:
    """Create a test role."""
    return await role_factory()

@pytest.fixture(scope="function")
async def test_professions(profession_factory: Callable) -> List[Profession]:
    """Create test professions with different roles."""
    return [
        await profession_factory(name="Guardian", role="Support", icon="guardian.png"),
        await profession_factory(name="Warrior", role="Damage", icon="warrior.png"),
        await profession_factory(name="Engineer", role="Support", icon="engineer.png"),
        await profession_factory(name="Ranger", role="Damage", icon="ranger.png"),
        await profession_factory(name="Thief", role="Damage", icon="thief.png"),
    ]

@pytest.fixture(scope="function")
async def test_user(user_factory: Callable) -> User:
    """Create a test user."""
    return await user_factory()

@pytest.fixture(scope="function")
async def admin_user(user_factory: Callable) -> User:
    """Create an admin user."""
    return await user_factory(is_superuser=True)

@pytest.fixture(scope="function")
async def other_test_user(user_factory: Callable) -> User:
    """Create another test user for testing authorization."""
    return await user_factory(email="other@example.com", username="otheruser")

@pytest.fixture(scope="function")
async def test_build(build_factory: Callable, test_user: User, test_professions: List[Profession]) -> Build:
    """Create a test build."""
    return await build_factory(
        created_by_id=test_user.id,
        profession_ids=[p.id for p in test_professions[:2]]
    )

@pytest.fixture(scope="function")
async def test_private_build(build_factory: Callable, test_user: User, test_professions: List[Profession]) -> Build:
    """Create a private test build."""
    return await build_factory(
        name="Private Test Build",
        is_public=False,
        created_by_id=test_user.id,
        profession_ids=[p.id for p in test_professions[:2]]
    )

# Helper functions for authentication
async def get_auth_headers(
    user_id: int, 
    expires_delta: Optional[timedelta] = None
) -> Dict[str, str]:
    """Generate authentication headers for test requests."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    token = create_access_token(
        subject=str(user_id),
        expires_delta=expires_delta
    )
    return {"Authorization": f"Bearer {token}"}

async def get_auth_headers_for_user(
    user: User,
    expires_delta: Optional[timedelta] = None
) -> Dict[str, str]:
    """Generate authentication headers for a user."""
    return await get_auth_headers(user.id, expires_delta)

# Helper functions for API requests
async def create_build_via_api(
    client: AsyncClient, 
    build_data: Dict[str, Any], 
    user: User
) -> Tuple[Dict[str, Any], int]:
    """Helper to create a build via the API."""
    headers = await get_auth_headers_for_user(user)
    response = await client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers=headers
    )
    return response.json(), response.status_code

async def get_build_via_api(
    client: AsyncClient, 
    build_id: int, 
    user: Optional[User] = None
) -> Tuple[Dict[str, Any], int]:
    """Helper to get a build via the API."""
    headers = {}
    if user:
        headers = await get_auth_headers_for_user(user)
        
    response = await client.get(
        f"{settings.API_V1_STR}/builds/{build_id}",
        headers=headers
    )
    
    if response.status_code == status.HTTP_200_OK:
        return response.json(), response.status_code
    return {}, response.status_code

# Validation helpers
def assert_build_data_matches(
    build_data: Dict[str, Any], 
    build_in_db: Build
) -> None:
    """Assert that build data matches the database record."""
    for key, value in build_data.items():
        if key == "profession_ids":
            # Check profession associations
            profession_ids = [p.id for p in build_in_db.professions]
            assert set(value) == set(profession_ids), \
                f"Mismatch in profession IDs for build {build_in_db.id}"
        else:
            assert getattr(build_in_db, key) == value, \
                f"Mismatch in {key} for build {build_in_db.id}"

# Test classes
@pytest.mark.asyncio
class TestBuildsAPI:
    """Test suite for the Builds API endpoints."""
    
    # Test data setup
    @pytest.fixture(autouse=True)
    async def setup_data(self, async_db: AsyncSession, test_user: User, test_professions: List[Profession]):
        """Setup test data for the test class."""
        self.db = async_db
        self.test_user = test_user
        self.test_professions = test_professions
        self.profession_ids = [p.id for p in test_professions]
        
        # Create some test builds
        self.public_build = Build(
            name="Public Build",
            description="A public test build",
            is_public=True,
            owner_id=test_user.id,
            created_by_id=test_user.id,
            game_mode=GameMode.WVW,
            team_size=5,
            config={"roles": ["heal", "dps", "support"]},
            constraints={"max_duplicates": 2}
        )
        
        self.private_build = Build(
            name="Private Build",
            description="A private test build",
            is_public=False,
            owner_id=test_user.id,
            created_by_id=test_user.id,
            game_mode=GameMode.WVW,
            team_size=5,
            config={"roles": ["heal", "dps", "support"]},
            constraints={"max_duplicates": 2}
        )
        
        # Add professions to builds
        for build in [self.public_build, self.private_build]:
            for prof in test_professions[:3]:
                build.professions.append(prof)
            self.db.add(build)
        
        await self.db.commit()
        await self.db.refresh(self.public_build)
        await self.db.refresh(self.private_build)
        
        yield
        
        # Cleanup is handled by the async_db fixture
    
    # Helper methods
    async def _create_test_build(self, **overrides) -> Build:
        """Helper to create a test build."""
        build_data = {
            "name": f"Test Build {random_lower_string(4)}",
            "description": f"A test build {random_lower_string(10)}",
            "is_public": True,
            "owner_id": self.test_user.id,
            "created_by_id": self.test_user.id,
            "game_mode": GameMode.WVW,
            "team_size": 5,
            "config": {"roles": ["heal", "dps", "support"]},
            "constraints": {"max_duplicates": 2},
            "profession_ids": self.profession_ids[:3],
            **overrides
        }
        
        build = Build(**{k: v for k, v in build_data.items() if k != 'profession_ids'})
        
        # Add professions
        for prof_id in build_data['profession_ids']:
            prof = await self.db.get(Profession, prof_id)
            if prof:
                build.professions.append(prof)
        
        self.db.add(build)
        await self.db.commit()
        await self.db.refresh(build)
        return build
    
    # Test cases
    async def test_create_build_success(
        self, 
        async_client: AsyncClient, 
        test_user: User
    ):
        """Test creating a build with valid data."""
        # Prepare build data
        build_data = {
            "name": "New Test Build",
            "description": "A new test build",
            "is_public": True,
            "game_mode": GameMode.WVW.value,
            "team_size": 5,
            "config": {"roles": ["heal", "dps", "support"]},
            "constraints": {"max_duplicates": 2},
            "profession_ids": self.profession_ids[:3]
        }
        
        # Make request
        headers = await get_auth_headers_for_user(test_user)
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=headers
        )
        
        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Assert response data
        assert "id" in data
        assert data["name"] == build_data["name"]
        assert data["description"] == build_data["description"]
        assert data["is_public"] == build_data["is_public"]
        assert data["game_mode"] == build_data["game_mode"]
        assert data["team_size"] == build_data["team_size"]
        assert data["owner_id"] == test_user.id
        
        # Assert build was created in the database
        build = await self.db.get(Build, data["id"])
        assert build is not None
        assert build.name == build_data["name"]
        assert build.description == build_data["description"]
        assert build.is_public == build_data["is_public"]
        assert build.game_mode.value == build_data["game_mode"]
        assert build.team_size == build_data["team_size"]
        assert build.owner_id == test_user.id
        
        # Assert profession associations
        assert len(build.professions) == len(build_data["profession_ids"])
        assert {p.id for p in build.professions} == set(build_data["profession_ids"])
    
    async def test_get_build_success(
        self, 
        async_client: AsyncClient, 
        test_user: User
    ):
        """Test retrieving a build by ID."""
        # Get auth headers
        headers = await get_auth_headers_for_user(test_user)
        
        # Test getting public build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{self.public_build.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == self.public_build.id
        assert data["name"] == self.public_build.name
        assert data["is_public"] == self.public_build.is_public
        assert len(data["professions"]) == 3  # We added 3 professions in setup
        
        # Test getting private build (should work for owner)
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{self.private_build.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == self.private_build.id
    
    async def test_unauthorized_access(
        self, 
        async_client: AsyncClient, 
        other_test_user: User
    ):
        """Test unauthorized access to builds."""
        # Get auth headers for a different user
        other_headers = await get_auth_headers_for_user(other_test_user)
        
        # 1. Test unauthenticated access to private build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{self.private_build.id}"
        )
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,  # If auth is required
            status.HTTP_404_NOT_FOUND      # If we hide existence of private builds
        ]
        
        # 2. Test non-owner access to private build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{self.private_build.id}",
            headers=other_headers
        )
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,    # If user is authenticated but not owner
            status.HTTP_404_NOT_FOUND     # If we hide existence of private builds
        ]
        
        # 3. Test non-owner access to public build (should work)
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{self.public_build.id}",
            headers=other_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_update_build_success(
        self, 
        async_client: AsyncClient, 
        test_user: User,
        test_professions: List[Profession]
    ):
        """Test updating a build with valid data."""
        # Prepare update data
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
            "is_public": False,
            "team_size": 10,
            "config": {"roles": ["heal", "dps"]},
            "constraints": {"max_duplicates": 1},
            "profession_ids": [p.id for p in test_professions[3:6]]  # Different professions
        }
        
        # Make request
        headers = await get_auth_headers_for_user(test_user)
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{self.public_build.id}",
            json=update_data,
            headers=headers
        )
        
        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Assert response data
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_public"] == update_data["is_public"]
        assert data["team_size"] == update_data["team_size"]
        
        # Assert build was updated in the database
        await self.db.refresh(self.public_build)
        assert self.public_build.name == update_data["name"]
        assert self.public_build.description == update_data["description"]
        assert self.public_build.is_public == update_data["is_public"]
        assert self.public_build.team_size == update_data["team_size"]
        
        # Assert profession associations were updated
        assert {p.id for p in self.public_build.professions} == set(update_data["profession_ids"])
    
    async def test_delete_build_success(
        self, 
        async_client: AsyncClient, 
        test_user: User
    ):
        """Test deleting a build."""
        # Create a build to delete
        build = await self._create_test_build()
        build_id = build.id
        
        # Make delete request
        headers = await get_auth_headers_for_user(test_user)
        response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers=headers
        )
        
        # Assert response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Assert build was deleted from the database
        deleted_build = await self.db.get(Build, build_id)
        assert deleted_build is None
        
        # Assert build-profession associations were deleted
        result = await self.db.execute(
            select(BuildProfession).where(BuildProfession.build_id == build_id)
        )
        assert result.scalars().first() is None
    
    async def test_list_builds(
        self, 
        async_client: AsyncClient, 
        test_user: User,
        other_test_user: User
    ):
        """Test listing builds with various filters."""
        # Create some test builds
        build1 = await self._create_test_build(
            name="WvW Build 1",
            game_mode=GameMode.WVW,
            is_public=True
        )
        
        build2 = await self._create_test_build(
            name="PvP Build 1",
            game_mode=GameMode.PVP,
            is_public=True
        )
        
        build3 = await self._create_test_build(
            name="Private WvW Build",
            game_mode=GameMode.WVW,
            is_public=False
        )
        
        # Test 1: List all public builds (unauthenticated)
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Should only see public builds
        build_ids = {b["id"] for b in data}
        assert build1.id in build_ids
        assert build2.id in build_ids
        assert build3.id not in build_ids  # Private
        
        # Test 2: List builds with game_mode filter
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"game_mode": GameMode.WVW.value}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(b["game_mode"] == GameMode.WVW.value for b in data)
        
        # Test 3: List builds as authenticated user (should see own private builds)
        headers = await get_auth_headers_for_user(test_user)
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        build_ids = {b["id"] for b in data}
        
        # Should see public builds and own private builds
        assert build1.id in build_ids
        assert build2.id in build_ids
        assert build3.id in build_ids  # Own private build
        
        # Test 4: List builds as another user (shouldn't see other's private builds)
        other_headers = await get_auth_headers_for_user(other_test_user)
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            headers=other_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        build_ids = {b["id"] for b in data}
        
        # Should only see public builds
        assert build1.id in build_ids
        assert build2.id in build_ids
        assert build3.id not in build_ids  # Other user's private build

    # Edge case tests
    async def test_create_build_with_invalid_data(
        self, 
        async_client: AsyncClient, 
        test_user: User
    ):
        """Test creating a build with invalid data."""
        headers = await get_auth_headers_for_user(test_user)
        
        # Test 1: Missing required fields
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={"name": "Incomplete Build"},  # Missing required fields
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test 2: Invalid profession IDs
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                "name": "Invalid Professions",
                "description": "Build with invalid profession IDs",
                "is_public": True,
                "game_mode": GameMode.WVW.value,
                "team_size": 5,
                "profession_ids": [99999, 100000]  # Non-existent IDs
            },
            headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test 3: Invalid game mode
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                "name": "Invalid Game Mode",
                "description": "Build with invalid game mode",
                "is_public": True,
                "game_mode": "invalid_mode",
                "team_size": 5,
                "profession_ids": self.profession_ids[:2]
            },
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Concurrency tests
    async def test_concurrent_updates(
        self, 
        async_client: AsyncClient, 
        test_user: User
    ):
        """Test concurrent updates to the same build."""
        # Create a build to update
        build = await self._create_test_build()
        
        # Simulate concurrent updates
        async def update_build(build_id: int, name: str) -> Tuple[bool, str]:
            try:
                headers = await get_auth_headers_for_user(test_user)
                response = await async_client.put(
                    f"{settings.API_V1_STR}/builds/{build_id}",
                    json={"name": name},
                    headers=headers
                )
                return response.status_code == status.HTTP_200_OK, ""
            except Exception as e:
                return False, str(e)
        
        # Run concurrent updates
        tasks = [
            update_build(build.id, f"Build Update {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Verify exactly one update succeeded
        success_count = sum(1 for success, _ in results if success)
        assert success_count == 1, f"Expected exactly one successful update, got {success_count}"
        
        # Verify the build was updated
        await self.db.refresh(build)
        assert build.name.startswith("Build Update ")
