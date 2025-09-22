"""
Tests for the Roles API endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_role(client: AsyncClient, admin_token):
    """Test creating a new role (admin only)."""
    # Test data
    role_data = {
        "name": "test_role",
        "description": "A test role",
        "permissions": ["read", "write"],
    }

    # Make request as admin
    response = await client.post(
        "/api/v1/roles/",
        json=role_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == role_data["name"]
    assert data["description"] == role_data["description"]
    assert set(data["permissions"]) == set(role_data["permissions"])


@pytest.mark.asyncio
async def test_get_role(client: AsyncClient, test_role):
    """Test retrieving a role by ID."""
    # Make request
    response = await client.get(f"/api/v1/roles/{test_role.id}")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_role.id
    assert data["name"] == test_role.name


@pytest.mark.asyncio
async def test_list_roles(client: AsyncClient, test_role):
    """Test listing all roles."""
    # Make request
    response = await client.get("/api/v1/roles/")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(role["id"] == test_role.id for role in data)


@pytest.mark.asyncio
async def test_add_user_to_role(client: AsyncClient, test_role, test_user, admin_token):
    """Test adding a user to a role (admin only)."""
    # Make request as admin
    response = await client.post(
        f"/api/v1/roles/{test_role.id}/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "users" in data
    assert any(user["id"] == test_user.id for user in data["users"])


@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, test_role, admin_token):
    """Test updating a role (admin only)."""
    # Update data
    update_data = {
        "description": "Updated description",
        "permissions": ["read", "write", "delete"],
    }

    # Make request as admin
    response = await client.put(
        f"/api/v1/roles/{test_role.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == update_data["description"]
    assert set(data["permissions"]) == set(update_data["permissions"])


@pytest.mark.asyncio
async def test_remove_user_from_role(
    client: AsyncClient, test_role, test_user, admin_token
):
    """Test removing a user from a role (admin only)."""
    # First add the user to the role
    await client.post(
        f"/api/v1/roles/{test_role.id}/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Now remove the user
    response = await client.delete(
        f"/api/v1/roles/{test_role.id}/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "users" in data
    assert all(user["id"] != test_user.id for user in data["users"])


@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, test_role, admin_token):
    """Test deleting a role (admin only)."""
    # Make request as admin
    response = await client.delete(
        f"/api/v1/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify role was deleted
    response = await client.get(f"/api/v1/roles/{test_role.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient, test_role, test_token):
    """Test that non-admin users cannot modify roles."""
    # Try to create (non-admin)
    response = await client.post(
        "/api/v1/roles/",
        json={"name": "test_role_2"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Try to update (non-admin)
    response = await client.put(
        f"/api/v1/roles/{test_role.id}",
        json={"description": "Should Fail"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete (non-admin)
    response = await client.delete(
        f"/api/v1/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
