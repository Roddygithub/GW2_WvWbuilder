"""Tests for the Builds API endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models import Build
from app.schemas.build import GameMode


@pytest.mark.asyncio
async def test_create_build(client: AsyncClient, test_user, test_profession):
    """Test creating a new build."""
    # Get auth token for test user
    auth_token = await test_user.get_auth_token()

    # Build data
    build_data = {
        "name": "Test Build API",
        "description": "Created via API test",
        "game_mode": GameMode.WVW.value,
        "is_public": True,
        "profession_ids": [test_profession.id],
        "config": {"skills": [], "traits": []},
    }

    # Make request
    response = await client.post(
        "/api/v1/builds/",
        json=build_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Build API"
    assert data["created_by_id"] == test_user.id
    assert len(data["professions"]) == 1
    assert data["professions"][0]["id"] == test_profession.id


@pytest.mark.asyncio
async def test_get_build(client: AsyncClient, test_build):
    """Test retrieving a build by ID."""
    # Make request
    response = await client.get(f"/api/v1/builds/{test_build.id}")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_build.id
    assert data["name"] == test_build.name


@pytest.mark.asyncio
async def test_update_build(client: AsyncClient, test_build, test_user):
    """Test updating a build."""
    # Get auth token for test user
    auth_token = await test_user.get_auth_token()

    # Update data
    update_data = {
        "name": "Updated Build Name",
        "description": "Updated via API",
        "is_public": False,
    }

    # Make request
    response = await client.put(
        f"/api/v1/builds/{test_build.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Build Name"
    assert data["description"] == "Updated via API"
    assert data["is_public"] is False


@pytest.mark.asyncio
async def test_delete_build(client: AsyncClient, test_build, test_user):
    """Test deleting a build."""
    # Get auth token for test user
    auth_token = await test_user.get_auth_token()

    # Make request
    response = await client.delete(
        f"/api/v1/builds/{test_build.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify build was deleted
    response = await client.get(f"/api/v1/builds/{test_build.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_builds(client: AsyncClient, test_build, test_user):
    """Test listing builds with filters."""
    # Create a second build
    other_build = await Build.create(
        name="Other Build",
        game_mode=GameMode.PVE.value,
        created_by_id=test_user.id,
        is_public=True,
    )

    # Test unfiltered list
    response = await client.get("/api/v1/builds/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # At least our two test builds

    # Test filtering by game mode
    response = await client.get("/api/v1/builds/?game_mode=wvw")
    data = response.json()
    assert all(b["game_mode"] == "wvw" for b in data)

    # Test filtering by author
    response = await client.get(f"/api/v1/builds/?author_id={test_user.id}")
    data = response.json()
    assert all(b["created_by_id"] == test_user.id for b in data)


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient, test_build):
    """Test that unauthorized users cannot modify builds."""
    # Try to update without authentication
    response = await client.put(
        f"/api/v1/builds/{test_build.id}", json={"name": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to delete without authentication
    response = await client.delete(f"/api/v1/builds/{test_build.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to create without authentication
    response = await client.post("/api/v1/builds/", json={"name": "Should Fail"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
