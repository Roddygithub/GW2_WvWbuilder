"""
Comprehensive tests for the Compositions API endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Composition, User, Build

pytestmark = pytest.mark.asyncio


class TestCompositionsAPI:
    """Test suite for Compositions API endpoints."""

    async def test_create_composition_success(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_build: Build,
        db: AsyncSession,
    ):
        """Test creating a new composition with valid data."""
        composition_data = {
            "name": "Test Composition",
            "description": "A test composition",
            "squad_size": 10,
            "is_public": True,
            "build_ids": [test_build.id],
            "tags": ["wvw", "gvg"],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/",
            json=composition_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == composition_data["name"]
        assert data["created_by"] == test_user.id
        assert len(data["builds"]) == 1
        assert data["builds"][0]["id"] == test_build.id

    async def test_get_composition_success(
        self, async_client: AsyncClient, test_composition: Composition, test_user: User
    ):
        """Test retrieving a composition by ID."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/{test_composition.id}",
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_composition.id
        assert data["name"] == test_composition.name

    async def test_update_composition_success(
        self, async_client: AsyncClient, test_composition: Composition, test_user: User
    ):
        """Test updating a composition with valid data."""
        update_data = {
            "name": "Updated Composition Name",
            "description": "Updated description",
            "is_public": False,
            "tags": ["updated", "tags"],
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/compositions/{test_composition.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_public"] == update_data["is_public"]
        assert set(data["tags"]) == set(update_data["tags"])

    async def test_list_compositions(
        self, async_client: AsyncClient, test_composition: Composition, test_user: User
    ):
        """Test listing compositions with pagination."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/",
            params={"skip": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(comp["id"] == test_composition.id for comp in data)

    async def test_filter_compositions_by_tag(
        self, async_client: AsyncClient, test_composition: Composition, test_user: User
    ):
        """Test filtering compositions by tag."""
        # First, ensure the test composition has the expected tag
        if not test_composition.tags or "wvw" not in [
            t.name for t in test_composition.tags
        ]:
            update_data = {"tags": ["wvw", "test"]}
            await async_client.put(
                f"{settings.API_V1_STR}/compositions/{test_composition.id}",
                json=update_data,
                headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
            )

        # Now test the filter
        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/",
            params={"tag": "wvw"},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(comp["id"] == test_composition.id for comp in data)
        assert all("wvw" in comp.get("tags", []) for comp in data)
