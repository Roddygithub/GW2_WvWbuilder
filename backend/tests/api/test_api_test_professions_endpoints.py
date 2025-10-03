"""
Tests for the Professions API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from app.models import Profession


from app.core.config import settings


@pytest.mark.asyncio
class TestProfessionsAPI:
    """Test suite for Professions API endpoints."""

    async def test_create_profession(self, async_client: AsyncClient, auth_headers):
        """Test creating a new profession (admin only)."""
        admin_headers = await auth_headers(username="admin", is_superuser=True)
        profession_data = {
            "name": "Test Profession",
            "description": "A test profession",
            "icon_url": "http://example.com/icon.png",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/professions/", json=profession_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == profession_data["name"]
        assert data["description"] == profession_data["description"]

    async def test_get_profession(self, async_client: AsyncClient, profession_factory, auth_headers):
        """Test retrieving a profession by ID."""
        profession = await profession_factory(name="Readable Profession")
        headers = await auth_headers()

        response = await async_client.get(f"{settings.API_V1_STR}/professions/{profession.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == profession.id
        assert data["name"] == "Readable Profession"

    async def test_get_nonexistent_profession(self, async_client: AsyncClient, auth_headers):
        """Test retrieving a non-existent profession by ID."""
        headers = await auth_headers()
        response = await async_client.get(f"{settings.API_V1_STR}/professions/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_list_professions(self, async_client: AsyncClient, profession_factory, auth_headers):
        """Test listing all professions."""
        await profession_factory(name="Profession 1")
        await profession_factory(name="Profession 2")
        headers = await auth_headers()

        response = await async_client.get(f"{settings.API_V1_STR}/professions/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_update_profession(self, async_client: AsyncClient, profession_factory, auth_headers):
        """Test updating a profession (admin only)."""
        profession = await profession_factory()
        admin_headers = await auth_headers(username="admin", is_superuser=True)
        update_data = {"description": "Updated description", "icon_url": "http://new.icon/url.png"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/professions/{profession.id}", json=update_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["icon_url"] == "http://new.icon/url.png"

    async def test_update_nonexistent_profession(self, async_client: AsyncClient, auth_headers):
        """Test updating a non-existent profession (admin only)."""
        admin_headers = await auth_headers(username="admin", is_superuser=True)
        update_data = {"description": "This will fail"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/professions/999999", json=update_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_profession(self, async_client: AsyncClient, profession_factory, auth_headers):
        """Test deleting a profession (admin only)."""
        profession = await profession_factory()
        admin_headers = await auth_headers(username="admin", is_superuser=True)

        response = await async_client.delete(f"{settings.API_V1_STR}/professions/{profession.id}", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK

        # Verify it was deleted
        response = await async_client.get(f"{settings.API_V1_STR}/professions/{profession.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_nonexistent_profession(self, async_client: AsyncClient, auth_headers):
        """Test deleting a non-existent profession (admin only)."""
        admin_headers = await auth_headers(username="admin", is_superuser=True)

        response = await async_client.delete(f"{settings.API_V1_STR}/professions/999999", headers=admin_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()

    async def test_unauthorized_create_profession(self, async_client: AsyncClient, auth_headers):
        """Test that non-admin users cannot create professions."""
        user_headers = await auth_headers()
        profession_data = {"name": "Unauthorized Profession"}

        response = await async_client.post(
            f"{settings.API_V1_STR}/professions/", json=profession_data, headers=user_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
class TestEliteSpecializationsAPI:
    """Test suite for Elite Specializations API endpoints."""

    async def test_create_elite_specialization(self, async_client: AsyncClient, profession_factory, auth_headers):
        """Test adding an elite specialization to a profession (admin only)."""
        profession = await profession_factory()
        admin_headers = await auth_headers(username="admin", is_superuser=True)
        elite_spec_data = {
            "name": "Test Elite Spec",
            "description": "A test elite specialization",
            "weapon_type": "Scepter",
            "profession_id": profession.id,
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/professions/elite-specializations/",
            json=elite_spec_data,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Elite Spec"
        assert data["profession_id"] == profession.id
