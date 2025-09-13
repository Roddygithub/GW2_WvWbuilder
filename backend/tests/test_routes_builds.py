"""Tests for build routes."""
import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.build import Build
from app.schemas.build import BuildCreate, BuildUpdate

pytestmark = pytest.mark.asyncio

async def test_create_build(
    async_client: AsyncClient,
    test_token: str,
    test_profession: dict,
    test_user: dict
):
    """Test creating a new build."""
    build_data = {
        "name": "Test Build",
        "description": "A test build",
        "profession_id": test_profession["id"],
        "game_mode": "pvp",
        "is_public": True,
        "build_link": "http://example.com/build"
    }
    
    response = await async_client.post(
        "/api/v1/builds/",
        json=build_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == build_data["name"]
    assert data["created_by"] == test_user["id"]
    assert data["is_public"] is True

async def test_get_build(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict
):
    """Test retrieving a build by ID."""
    response = await async_client.get(
        f"/api/v1/builds/{test_build['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_build["id"]
    assert data["name"] == test_build["name"]

async def test_update_build(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict
):
    """Test updating a build."""
    update_data = {
        "name": "Updated Build Name",
        "description": "Updated description",
        "is_public": False
    }
    
    response = await async_client.put(
        f"/api/v1/builds/{test_build['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]

async def test_delete_build(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict
):
    """Test deleting a build."""
    # First, create a build to delete
    create_response = await async_client.post(
        "/api/v1/builds/",
        json={
            "name": "Build to delete",
            "profession_id": test_build["profession_id"],
            "game_mode": "pve"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    build_id = create_response.json()["id"]
    
    # Now delete it
    delete_response = await async_client.delete(
        f"/api/v1/builds/{build_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    get_response = await async_client.get(
        f"/api/v1/builds/{build_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

async def test_list_builds(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict
):
    """Test listing builds with pagination and filtering."""
    response = await async_client.get(
        "/api/v1/builds/",
        params={"skip": 0, "limit": 10},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(build["id"] == test_build["id"] for build in data)

async def test_unauthorized_access(
    async_client: AsyncClient,
    test_build: dict
):
    """Test that protected build endpoints require authentication."""
    # Try to access without token
    response = await async_client.get(f"/api/v1/builds/{test_build['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to create without token
    response = await async_client.post("/api/v1/builds/", json={"name": "Test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_forbidden_actions(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict,
    another_user_token: str
):
    """Test that users can't modify other users' builds."""
    # Try to update another user's build
    response = await async_client.put(
        f"/api/v1/builds/{test_build['id']}",
        json={"name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Try to delete another user's build
    response = await async_client.delete(
        f"/api/v1/builds/{test_build['id']}",
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_build_invalid_profession(
    async_client: AsyncClient,
    test_token: str
):
    """Test creating a build with an invalid profession ID."""
    build_data = {
        "name": "Invalid Profession Build",
        "profession_id": 99999,  # Non-existent profession
        "game_mode": "pvp"
    }
    
    response = await async_client.post(
        "/api/v1/builds/",
        json=build_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid profession ID" in response.json()["detail"]

async def test_create_build_invalid_game_mode(
    async_client: AsyncClient,
    test_token: str,
    test_profession: dict
):
    """Test creating a build with an invalid game mode."""
    build_data = {
        "name": "Invalid Game Mode Build",
        "profession_id": test_profession["id"],
        "game_mode": "invalid_mode"
    }
    
    response = await async_client.post(
        "/api/v1/builds/",
        json=build_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in str(response.content)

async def test_get_nonexistent_build(
    async_client: AsyncClient,
    test_token: str
):
    """Test retrieving a build that doesn't exist."""
    response = await async_client.get(
        "/api/v1/builds/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Build not found" in response.json()["detail"]

async def test_list_builds_filtering(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict,
    test_user: dict
):
    """Test filtering builds by various criteria."""
    # Create a second build with different attributes
    another_build = {
        "name": "Another Test Build",
        "profession_id": test_build["profession_id"],
        "game_mode": "wvw",
        "is_public": False
    }
    create_response = await async_client.post(
        "/api/v1/builds/",
        json=another_build,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    another_build_id = create_response.json()["id"]
    
    try:
        # Test filtering by game_mode
        response = await async_client.get(
            "/api/v1/builds/",
            params={"game_mode": "wvw"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(build["game_mode"] == "wvw" for build in data)
        
        # Test filtering by is_public
        response = await async_client.get(
            "/api/v1/builds/",
            params={"is_public": "false"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(not build["is_public"] for build in data)
        
        # Test filtering by created_by
        response = await async_client.get(
            "/api/v1/builds/",
            params={"created_by": test_user["id"]},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(build["created_by"] == test_user["id"] for build in data)
        
    finally:
        # Clean up
        await async_client.delete(
            f"/api/v1/builds/{another_build_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )

async def test_update_build_nonexistent(
    async_client: AsyncClient,
    test_token: str
):
    """Test updating a build that doesn't exist."""
    update_data = {
        "name": "Nonexistent Build",
        "description": "This build doesn't exist"
    }
    
    response = await async_client.put(
        "/api/v1/builds/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Build not found" in response.json()["detail"]
