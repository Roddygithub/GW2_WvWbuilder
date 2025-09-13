"""Tests for the Builds API endpoints."""
import json
from typing import Dict, Any, List

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.build import BuildCreate, BuildUpdate, BuildGenerationRequest
from app.models import User, Build, Profession
from app.crud import build as build_crud
from app.core.security import create_access_token

pytestmark = pytest.mark.asyncio


class TestBuildsAPI:
    """Test suite for Builds API endpoints."""
    
    @pytest.fixture(autouse=True)
    async def setup_teardown(self, async_db: AsyncSession, test_user: Dict[str, Any]):
        """Setup and teardown for each test."""
        self.user_id = test_user["id"]
        self.access_token = test_user["access_token"]
        self.db = async_db
        
        # Create test professions if needed
        self.professions = []
        for name in ["Guardian", "Warrior", "Elementalist"]:
            profession = Profession(name=name, description=f"{name} profession")
            self.db.add(profession)
            await self.db.commit()
            await self.db.refresh(profession)
            self.professions.append(profession)
            
        yield
        
        # Cleanup
        await self.db.execute("DELETE FROM build_profession_association")
        await self.db.execute("DELETE FROM builds")
        await self.db.execute("DELETE FROM professions")
        await self.db.commit()

    async def test_create_build_success(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_profession: Dict[str, Any]
    ):
        """Test creating a new build with valid data."""
        # Test with minimal required fields
        minimal_build_data = {
            "name": "Minimal Build",
            "game_mode": "wvw",
            "team_size": 5,
            "profession_ids": [test_profession["id"]]
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=minimal_build_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == minimal_build_data["name"]
        assert data["created_by_id"] == test_user["id"]
        assert data["professions"][0]["id"] == test_profession["id"]
        assert data["is_public"] is False  # Default value
        
        # Test with all fields
        full_build_data = {
            "name": "Full Build",
            "description": "A detailed test build",
            "game_mode": "wvw",
            "team_size": 10,
            "is_public": True,
            "profession_ids": [p.id for p in self.professions],
            "config": {
                "weapons": ["Greatsword", "Staff"],
                "traits": [1, 2, 3],
                "skills": ["Merciful Intervention", "Sword of Justice"]
            },
            "constraints": {
                "min_healers": 2,
                "min_dps": 5,
                "min_support": 2
            }
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=full_build_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == full_build_data["name"]
        assert data["description"] == full_build_data["description"]
        assert data["game_mode"] == full_build_data["game_mode"]
        assert data["team_size"] == full_build_data["team_size"]
        assert data["is_public"] == full_build_data["is_public"]
        assert data["config"] == full_build_data["config"]
        assert data["constraints"] == full_build_data["constraints"]
        assert len(data["professions"]) == len(self.professions)

    async def test_create_build_unauthorized(self, async_client: AsyncClient, test_profession: Dict[str, Any]):
        """Test creating a build without authentication."""
        build_data = {
            "name": "Unauthorized Build",
            "game_mode": "wvw",
            "profession_ids": [test_profession["id"]]
        }
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    async def test_create_build_with_invalid_profession(self, async_client: AsyncClient, test_user: Dict[str, Any]):
        """Test creating a build with non-existent profession IDs."""
        build_data = {
            "name": "Invalid Profession Build",
            "game_mode": "wvw",
            "profession_ids": [99999]  # Non-existent profession ID
        }
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Profession not found" in response.json()["detail"]

    async def test_get_build_success(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test retrieving a build by ID."""
        # Test getting a public build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{test_build['id']}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_build["id"]
        assert data["name"] == test_build["name"]
        assert "created_by" in data
        assert data["created_by"]["id"] == test_user["id"]
        assert "professions" in data
        assert len(data["professions"]) > 0
        
        # Create a private build and test access control
        private_build = Build(
            name="Private Build",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            created_by_id=test_user["id"],
            config={"traits": [1, 2, 3]}
        )
        self.db.add(private_build)
        await self.db.commit()
        await self.db.refresh(private_build)
        
        # Owner should be able to access their own private build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Create another user and try to access the private build
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(other_user)
        await self.db.commit()
        other_token = create_access_token(subject=other_user.id)
        
        # Other user should not be able to access private build
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_nonexistent_build(
        self, async_client: AsyncClient, test_user: Dict[str, Any]
    ):
        """Test retrieving a non-existent build."""
        # Test with non-existent ID
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/999999",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test with invalid ID format
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/not_an_id",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_build_success(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test updating a build with valid data."""
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
            "is_public": False,
            "profession_ids": [p.id for p in self.professions[:2]]  # Update with first two professions
        }
        
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_public"] == update_data["is_public"]
        assert len(data["professions"]) == 2
        
    async def test_update_nonexistent_build(self, async_client: AsyncClient, test_user: Dict[str, Any]):
        """Test updating a non-existent build."""
        update_data = {
            "name": "Nonexistent Build",
            "description": "This build doesn't exist"
        }
        
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/999999",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    async def test_update_build_unauthorized(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test updating a build without proper authorization."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(other_user)
        await self.db.commit()
        await self.db.refresh(other_user)
        
        # Try to update the build with the other user's token
        other_token = create_access_token(subject=other_user.id)
        
        update_data = {"name": "Unauthorized Update"}
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_build_success(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test deleting a build."""
        # Create a build to delete with multiple professions
        build_data = {
            "name": "Build to Delete",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "profession_ids": [p.id for p in self.professions],
            "config": {"traits": [1, 2, 3]}
        }
        
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        build_id = create_response.json()["id"]
        
        # Verify it was created with the correct number of professions
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert len(get_response.json()["professions"]) == len(self.professions)
        
        # Now delete it
        delete_response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify the build_profession associations were also deleted
        # This would be verified by the database constraints, but we can check the count
        result = await self.db.execute(
            "SELECT COUNT(*) FROM build_profession_association WHERE build_id = :build_id",
            {"build_id": build_id}
        )
        count = result.scalar()
        assert count == 0
        
    async def test_delete_nonexistent_build(self, async_client: AsyncClient, test_user: Dict[str, Any]):
        """Test deleting a non-existent build."""
        response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/999999",
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    async def test_delete_build_unauthorized(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test deleting a build without proper authorization."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(other_user)
        await self.db.commit()
        
        # Try to delete the build with the other user's token
        other_token = create_access_token(subject=other_user.id)
        
        response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{test_build['id']}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_builds(
        self, async_client: AsyncClient, test_user: Dict[str, Any], test_build: Dict[str, Any]
    ):
        """Test listing builds with pagination."""
        # Create a few more test builds
        for i in range(5):
            build = Build(
                name=f"Test Build {i}",
                game_mode="wvw",
                team_size=5,
                is_public=True,
                created_by_id=test_user["id"],
                config={"traits": [1, 2, 3]}
            )
            self.db.add(build)
        await self.db.commit()
        
        # Test pagination
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"skip": 1, "limit": 3},
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Should have 3 items due to limit=3
        
        # Test filtering by game_mode
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"game_mode": "wvw"},
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(build["game_mode"] == "wvw" for build in data)
        
        # Test listing without authentication (should only show public builds)
        public_build = Build(
            name="Public Build",
            game_mode="wvw",
            team_size=5,
            is_public=True,
            created_by_id=test_user["id"],
            config={}
        )
        private_build = Build(
            name="Private Build",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            created_by_id=test_user["id"],
            config={}
        )
        self.db.add_all([public_build, private_build])
        await self.db.commit()
        
        # Unauthenticated request should only show public builds
        response = await async_client.get(f"{settings.API_V1_STR}/builds/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(build["is_public"] for build in data)
        assert not any(build["name"] == "Private Build" for build in data)

    async def test_create_build_with_invalid_data(
        self, async_client: AsyncClient, test_user: Dict[str, Any]
    ):
        """Test creating a build with invalid data."""
        # Test with missing required fields
        invalid_data = {
            "name": "",  # Empty name
            "game_mode": "invalid_mode",  # Invalid game mode
            "team_size": 0,  # Invalid team size
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        
        # Check for validation errors
        error_fields = [
            str(error.get("loc", [""])[1])
            for error in errors
            if len(error.get("loc", [])) > 1
        ]
        
        assert "name" in error_fields
        assert "game_mode" in error_fields
        assert "team_size" in error_fields
        
        # Test with invalid profession IDs
        invalid_profession_data = {
            "name": "Test Build",
            "game_mode": "wvw",
            "team_size": 5,
            "profession_ids": ["not_an_integer"]  # Invalid type
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=invalid_profession_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
