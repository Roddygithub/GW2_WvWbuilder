"""
Tests for the Tags API endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
class TestTagsAPI:
    """Test suite for Tags API endpoints."""

    async def test_create_tag(self, async_client: AsyncClient, auth_headers):
        """Test creating a new tag (admin only)."""
        admin_headers = await auth_headers(username="tag_admin", is_superuser=True)
        tag_data = {"name": "WvW", "description": "World vs World content"}

        response = await async_client.post(f"{settings.API_V1_STR}/tags/", json=tag_data, headers=admin_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "WvW"
        assert data["description"] == "World vs World content"

    async def test_create_tag_unauthorized(self, async_client: AsyncClient, auth_headers):
        """Test that a non-admin user cannot create a tag."""
        user_headers = await auth_headers(username="tag_user")
        tag_data = {"name": "Unauthorized Tag"}

        response = await async_client.post(f"{settings.API_V1_STR}/tags/", json=tag_data, headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_tag_edge_cases(self, async_client: AsyncClient, auth_headers):
        """Test creating a tag with edge case names."""
        admin_headers = await auth_headers(username="tag_admin_edge", is_superuser=True)

        # Test avec un nom très long (devrait échouer à la validation Pydantic)
        long_name_data = {"name": "a" * 51, "description": "This name is too long"}
        response_long = await async_client.post(
            f"{settings.API_V1_STR}/tags/", json=long_name_data, headers=admin_headers
        )
        assert response_long.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test avec des caractères spéciaux (devrait réussir)
        special_char_data = {"name": "Tag with !@#$%^&*()", "description": "Special characters test"}
        response_special = await async_client.post(
            f"{settings.API_V1_STR}/tags/", json=special_char_data, headers=admin_headers
        )
        assert response_special.status_code == status.HTTP_201_CREATED
        data = response_special.json()
        assert data["name"] == "Tag with !@#$%^&*()"

        # Test avec un nom vide (devrait échouer)
        empty_name_data = {"name": "", "description": "Empty name"}
        response_empty = await async_client.post(
            f"{settings.API_V1_STR}/tags/", json=empty_name_data, headers=admin_headers
        )
        assert response_empty.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_read_tags(self, async_client: AsyncClient, tag_factory, auth_headers):
        """Test reading a list of tags."""
        await tag_factory(name="Tag1")
        await tag_factory(name="Tag2")
        headers = await auth_headers(username="tag_reader")

        response = await async_client.get(f"{settings.API_V1_STR}/tags/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_read_tag(self, async_client: AsyncClient, tag_factory, auth_headers):
        """Test reading a single tag by its ID."""
        tag = await tag_factory(name="ReadableTag")
        headers = await auth_headers(username="single_tag_reader")

        response = await async_client.get(f"{settings.API_V1_STR}/tags/{tag.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == tag.id
        assert data["name"] == "ReadableTag"

    async def test_read_nonexistent_tag(self, async_client: AsyncClient, auth_headers):
        """Test retrieving a non-existent tag by ID."""
        headers = await auth_headers()
        response = await async_client.get(f"{settings.API_V1_STR}/tags/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        # Accept both English and French error messages
        detail_lower = error_data["detail"].lower()
        assert "not found" in detail_lower or "non trouvé" in detail_lower or "trouvé" in detail_lower

    async def test_update_tag(self, async_client: AsyncClient, tag_factory, auth_headers):
        """Test updating a tag (admin only)."""
        tag = await tag_factory(name="Old Name")
        admin_headers = await auth_headers(username="tag_updater", is_superuser=True)
        update_data = {"name": "New Name", "description": "Updated description"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/tags/{tag.id}", json=update_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Updated description"

    async def test_update_nonexistent_tag(self, async_client: AsyncClient, auth_headers):
        """Test updating a non-existent tag (admin only)."""
        admin_headers = await auth_headers(username="tag_updater", is_superuser=True)
        update_data = {"name": "This will fail"}

        response = await async_client.put(f"{settings.API_V1_STR}/tags/999999", json=update_data, headers=admin_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_tag(self, async_client: AsyncClient, tag_factory, auth_headers):
        """Test deleting a tag (admin only)."""
        tag = await tag_factory(name="ToDelete")
        admin_headers = await auth_headers(username="tag_deleter", is_superuser=True)

        response = await async_client.delete(f"{settings.API_V1_STR}/tags/{tag.id}", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Tag supprimé avec succès" in response.json()["msg"]

        # Verify it's gone
        response = await async_client.get(f"{settings.API_V1_STR}/tags/{tag.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
