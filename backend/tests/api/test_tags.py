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

    async def test_update_tag(self, async_client: AsyncClient, tag_factory, auth_headers):
        """Test updating a tag (admin only)."""
        tag = await tag_factory(name="Old Name")
        admin_headers = await auth_headers(username="tag_updater", is_superuser=True)
        update_data = {"name": "New Name", "description": "Updated description"}

        response = await async_client.put(f"{settings.API_V1_STR}/tags/{tag.id}", json=update_data, headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Updated description"

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