"""
Tests for the Roles API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient

from app.models import Role
from app.core.config import settings
from app.models import Role, User

# Constantes pour les données de test
TEST_ROLE_DATA = {
    "name": "New Role",
    "description": "A test role",
    "permission_level": 5
}

@pytest.mark.asyncio
class TestRolesAPI:
    """Test suite for Roles API endpoints."""

    async def test_create_role(self, async_client: AsyncClient, auth_headers):
        """Test creating a new role (admin only)."""
        admin_headers = await auth_headers(username="admin1", is_superuser=True)

        response = await async_client.post(f"{settings.API_V1_STR}/roles/", json=TEST_ROLE_DATA, headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == TEST_ROLE_DATA["name"]
        assert data["permission_level"] == 5

    async def test_create_role_duplicate_name(self, async_client: AsyncClient, role_factory, auth_headers):
        """Test creating a role with a duplicate name fails."""
        await role_factory(name="Existing Role")
        admin_headers = await auth_headers(username="admin2", is_superuser=True)
        role_data = {"name": "Existing Role", "description": "A test role", "permission_level": 5}

        response = await async_client.post(f"{settings.API_V1_STR}/roles/", json=role_data, headers=admin_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    async def test_get_role(self, async_client: AsyncClient, role_factory, auth_headers):
        """Test retrieving a role by ID."""
        role = await role_factory(name="Readable Role")
        headers = await auth_headers()
        response = await async_client.get(f"{settings.API_V1_STR}/roles/{role.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == role.id
        assert data["name"] == "Readable Role"

    async def test_get_nonexistent_role(self, async_client: AsyncClient, auth_headers):
        """Test retrieving a non-existent role by ID."""
        headers = await auth_headers()
        response = await async_client.get(f"{settings.API_V1_STR}/roles/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_list_roles(self, async_client: AsyncClient, role_factory, auth_headers):
        """Test listing all roles."""
        await role_factory(name="Role 1")
        await role_factory(name="Role 2")
        headers = await auth_headers(username="lister")

        response = await async_client.get(f"{settings.API_V1_STR}/roles/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_update_role(self, async_client: AsyncClient, role_factory, auth_headers):
        """Test updating a role (admin only)."""
        role = await role_factory()
        admin_headers = await auth_headers(username="admin3", is_superuser=True)
        update_data = {"description": "Updated description", "permission_level": 10}

        response = await async_client.put(
            f"{settings.API_V1_STR}/roles/{role.id}", json=update_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["permission_level"] == 10

    async def test_update_nonexistent_role(self, async_client: AsyncClient, auth_headers):
        """Test updating a non-existent role fails."""
        admin_headers = await auth_headers(username="admin_updater", is_superuser=True)
        update_data = {"description": "Updated description"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/roles/99999", json=update_data, headers=admin_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_role(self, async_client: AsyncClient, role_factory, auth_headers):
        """Test deleting a role (admin only)."""
        role = await role_factory()
        admin_headers = await auth_headers(username="admin4", is_superuser=True)

        response = await async_client.delete(f"{settings.API_V1_STR}/roles/{role.id}", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK

        # Verify role was deleted
        response = await async_client.get(f"{settings.API_V1_STR}/roles/{role.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_nonexistent_role(self, async_client: AsyncClient, auth_headers):
        """Test deleting a non-existent role fails."""
        admin_headers = await auth_headers(username="admin_deleter", is_superuser=True)

        response = await async_client.delete(f"{settings.API_V1_STR}/roles/99999", headers=admin_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_unauthorized_create_role(self, async_client: AsyncClient, auth_headers):
        """Test that non-admin users cannot create roles."""
        user_headers = await auth_headers(username="non_admin")
        role_data = {"name": "Unauthorized Role"}

        response = await async_client.post(f"{settings.API_V1_STR}/roles/", json=role_data, headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
class TestUserRolesAPI:
    """Test suite for assigning roles to users."""

    async def test_add_role_to_user(self, async_client: AsyncClient, user_factory, role_factory, auth_headers):
        """Test adding a role to a user."""
        user = await user_factory(username="user_with_role")
        role = await role_factory()
        admin_headers = await auth_headers(username="admin_assigner", is_superuser=True)

        response = await async_client.post(
            f"{settings.API_V1_STR}/users/{user.id}/roles/{role.id}", headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        # Re-fetch user to check roles
        updated_user_response = await async_client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=admin_headers)
        updated_user_data = updated_user_response.json()
        assert any(r['id'] == role.id for r in updated_user_data.get('roles', []))

    async def test_remove_role_from_user(self, async_client: AsyncClient, user_factory, role_factory, auth_headers):
        """Test removing a role from a user."""
        role = await role_factory()
        user = await user_factory(roles=[role])
        admin_headers = await auth_headers(username="admin_remover", is_superuser=True)

        # Remove the role
        response = await async_client.delete(
            f"{settings.API_V1_STR}/users/{user.id}/roles/{role.id}", headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # Re-fetch user to check roles
        updated_user_response = await async_client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=admin_headers)
        updated_user_data = updated_user_response.json()
        assert not any(r['id'] == role.id for r in updated_user_data.get('roles', []))
