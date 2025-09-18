"""Tests for team management routes."""
import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.composition import Composition
from app.schemas.composition import CompositionCreate, CompositionUpdate

pytestmark = pytest.mark.asyncio

async def test_create_team(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict,
    test_build: dict
):
    """Test creating a new team composition."""
    team_data = {
        "name": "Test Team",
        "description": "A test team composition",
        "game_mode": "wvw",
        "is_public": True,
        "builds": [test_build["id"]]
    }
    
    response = await async_client.post(
        "/api/v1/teams/",
        json=team_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["created_by"] == test_user["id"]
    assert data["is_public"] is True
    assert len(data["builds"]) == 1
    assert data["builds"][0]["id"] == test_build["id"]

async def test_get_team(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict
):
    """Test retrieving a team composition by ID."""
    response = await async_client.get(
        f"/api/v1/teams/{test_team['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_team["id"]
    assert data["name"] == test_team["name"]
    assert len(data["builds"]) > 0

async def test_update_team(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict,
    test_build: dict
):
    """Test updating a team composition."""
    update_data = {
        "name": "Updated Team Name",
        "description": "Updated description",
        "is_public": False,
        "builds": [test_build["id"]]
    }
    
    response = await async_client.put(
        f"/api/v1/teams/{test_team['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]
    assert len(data["builds"]) == 1
    assert data["builds"][0]["id"] == test_build["id"]

async def test_delete_team(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict
):
    """Test deleting a team composition."""
    # First, create a team to delete
    create_response = await async_client.post(
        "/api/v1/teams/",
        json={
            "name": "Team to delete",
            "game_mode": "pve",
            "builds": [test_team["builds"][0]["id"]]
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    team_id = create_response.json()["id"]
    
    # Now delete it
    delete_response = await async_client.delete(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    get_response = await async_client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

async def test_list_teams(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict
):
    """Test listing team compositions with filtering."""
    response = await async_client.get(
        "/api/v1/teams/",
        params={"skip": 0, "limit": 10, "game_mode": "wvw"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(team["game_mode"] == "wvw" for team in data)

async def test_unauthorized_access(
    async_client: AsyncClient,
    test_team: dict
):
    """Test that protected team endpoints require authentication."""
    # Try to access without token
    response = await async_client.get(f"/api/v1/teams/{test_team['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = await async_client.post("/api/v1/teams/", json={"name": "Test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_forbidden_actions(
    async_client: AsyncClient,
    test_team: dict,
    another_user_token: str
):
    """Test that users can't modify other users' teams."""
    # Try to update another user's team
    response = await async_client.put(
        f"/api/v1/teams/{test_team['id']}",
        json={"name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Try to delete another user's team
    response = await async_client.delete(
        f"/api/v1/teams/{test_team['id']}",
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_team_invalid_build(
    async_client: AsyncClient,
    test_token: str,
    test_user: dict
):
    """Test creating a team with an invalid build ID."""
    team_data = {
        "name": "Team with Invalid Build",
        "game_mode": "wvw",
        "builds": [99999]  # Non-existent build
    }
    
    response = await async_client.post(
        "/api/v1/teams/",
        json=team_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid build ID" in response.json()["detail"]

async def test_create_team_invalid_game_mode(
    async_client: AsyncClient,
    test_token: str,
    test_build: dict
):
    """Test creating a team with an invalid game mode."""
    team_data = {
        "name": "Team with Invalid Game Mode",
        "game_mode": "invalid_mode",
        "builds": [test_build["id"]]
    }
    
    response = await async_client.post(
        "/api/v1/teams/",
        json=team_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in str(response.content)

async def test_get_nonexistent_team(
    async_client: AsyncClient,
    test_token: str
):
    """Test retrieving a team that doesn't exist."""
    response = await async_client.get(
        "/api/v1/teams/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Team not found" in response.json()["detail"]

async def test_list_teams_filtering(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict,
    test_user: dict,
    test_build: dict
):
    """Test filtering teams by various criteria."""
    # Create a second team with different attributes
    another_team = {
        "name": "Another Test Team",
        "game_mode": "pve",
        "is_public": False,
        "builds": [test_build["id"]]
    }
    create_response = await async_client.post(
        "/api/v1/teams/",
        json=another_team,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    another_team_id = create_response.json()["id"]
    
    try:
        # Test filtering by game_mode
        response = await async_client.get(
            "/api/v1/teams/",
            params={"game_mode": "pve"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(team["game_mode"] == "pve" for team in data)
        
        # Test filtering by is_public
        response = await async_client.get(
            "/api/v1/teams/",
            params={"is_public": "false"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(not team["is_public"] for team in data)
        
        # Test filtering by created_by
        response = await async_client.get(
            "/api/v1/teams/",
            params={"created_by": test_user["id"]},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(team["created_by"] == test_user["id"] for team in data)
        
    finally:
        # Clean up
        await async_client.delete(
            f"/api/v1/teams/{another_team_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )

async def test_update_team_nonexistent(
    async_client: AsyncClient,
    test_token: str
):
    """Test updating a team that doesn't exist."""
    update_data = {
        "name": "Nonexistent Team",
        "description": "This team doesn't exist"
    }
    
    response = await async_client.put(
        "/api/v1/teams/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Team not found" in response.json()["detail"]

async def test_update_team_invalid_build(
    async_client: AsyncClient,
    test_token: str,
    test_team: dict
):
    """Test updating a team with an invalid build ID."""
    update_data = {
        "name": "Updated Team with Invalid Build",
        "builds": [99999]  # Non-existent build
    }
    
    response = await async_client.put(
        f"/api/v1/teams/{test_team['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid build ID" in response.json()["detail"]
