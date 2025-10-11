"""Additional error tests for Builds API endpoints."""

from typing import Dict, Any
import pytest
from fastapi import status
from httpx import AsyncClient
from app.core.config import settings
from app.models import User, Build

pytestmark = pytest.mark.asyncio


class TestBuildsErrorHandling:
    """Test error handling for Builds API endpoints."""

    async def test_get_private_build_unauthorized(
        self,
        async_client: AsyncClient,
        test_user: Dict[str, Any],
        async_db,
    ):
        """Test retrieving a private build without proper authorization."""
        other_user = User(
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )
        async_db.add(other_user)
        await async_db.commit()

        private_build = Build(
            name="Private Build",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            created_by_id=other_user.id,
            config={},
        )
        async_db.add(private_build)
        await async_db.commit()

        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    async def test_update_build_with_invalid_data(
        self,
        async_client: AsyncClient,
        test_user: Dict[str, Any],
        test_build: Dict[str, Any],
    ):
        """Test updating a build with invalid data."""
        # Test with invalid data
        invalid_data = {
            "name": "",  # Empty name
            "game_mode": "invalid_mode",  # Invalid game mode
            "team_size": 0,  # Invalid team size
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build['id']}",
            json=invalid_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]

        # Check for validation errors
        error_fields = [str(error.get("loc", [""])[1]) for error in errors if len(error.get("loc", [])) > 1]

        assert "name" in error_fields
        assert "game_mode" in error_fields
        assert "team_size" in error_fields

    async def test_create_build_with_invalid_constraints(self, async_client: AsyncClient, test_user: Dict[str, Any]):
        """Test creating a build with invalid constraints."""
        invalid_constraints = {
            "name": "Test Build with Invalid Constraints",
            "game_mode": "wvw",
            "team_size": 5,
            "constraints": {
                "min_healers": -1,  # Invalid: negative value
                "min_dps": 10,  # Invalid: sum > team_size
                "min_support": 10,  # Invalid: sum > team_size
            },
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=invalid_constraints,
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("constraints" in str(error.get("loc", [])) for error in errors)

    async def test_list_builds_with_invalid_pagination(self, async_client: AsyncClient, test_user: Dict[str, Any]):
        """Test listing builds with invalid pagination parameters."""
        # Test with negative skip
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"skip": -1},
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with zero limit
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"limit": 0},
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with non-integer values
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"skip": "not_an_integer", "limit": "also_not_an_integer"},
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
