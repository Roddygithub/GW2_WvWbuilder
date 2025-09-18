"""
Tests for the Compositions API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

from app.models import Composition, User, Build, CompositionTag, CompositionMember
from app.schemas.composition import CompositionCreate, CompositionUpdate, CompositionMemberCreate

@pytest.mark.asyncio
async def test_create_composition(client: AsyncClient, test_user, test_token):
    """Test creating a new composition."""
    # Test data
    composition_data = {
        "name": "Test Composition",
        "description": "A test composition",
        "game_mode": "wvw",
        "is_public": True,
        "min_players": 5,
        "max_players": 10
    }
    
    # Make request
    response = await client.post(
        "/api/v1/compositions/",
        json=composition_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == composition_data["name"]
    assert data["created_by_id"] == test_user.id
    assert data["game_mode"] == composition_data["game_mode"]
    assert data["is_public"] == composition_data["is_public"]
    assert data["min_players"] == composition_data["min_players"]
    assert data["max_players"] == composition_data["max_players"]

@pytest.mark.asynbox async def test_get_composition(client: AsyncClient, test_composition):
    """Test retrieving a composition by ID."""
    # Make request
    response = await client.get(f"/api/v1/compositions/{test_composition.id}")
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_composition.id
    assert data["name"] == test_composition.name

@pytest.mark.asynbox async def test_update_composition(client: AsyncClient, test_composition, test_token):
    """Test updating a composition."""
    # Update data
    update_data = {
        "name": "Updated Composition",
        "description": "Updated description",
        "is_public": False,
        "min_players": 8,
        "max_players": 12
    }
    
    # Make request
    response = await client.put(
        f"/api/v1/compositions/{test_composition.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]
    assert data["min_players"] == update_data["min_players"]
    assert data["max_players"] == update_data["max_players"]

@pytest.mark.asynbox async def test_add_build_to_composition(client: AsyncClient, test_composition, test_build, test_token):
    """Test adding a build to a composition."""
    # Test member data
    member_data = {
        "build_id": test_build.id,
        "role": "DPS",
        "count": 2,
        "is_required": True
    }
    
    # Make request
    response = await client.post(
        f"/api/v1/compositions/{test_composition.id}/builds",
        json=member_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["build_id"] == test_build.id
    assert data["members"][0]["role"] == "DPS"

@pytest.mark.asynbox async def test_add_tag_to_composition(client: AsyncClient, test_composition, test_token):
    """Test adding a tag to a composition."""
    # Test tag data
    tag_data = {"name": "test_tag"}
    
    # Make request
    response = await client.post(
        f"/api/v1/compositions/{test_composition.id}/tags",
        json=tag_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "tags" in data
    assert any(tag["name"] == "test_tag" for tag in data["tags"])

@pytest.mark.asynbox async def test_list_public_compositions(client: AsyncClient, test_composition):
    """Test listing public compositions."""
    # Make request
    response = await client.get("/api/v1/compositions/")
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(comp["id"] == test_composition.id for comp in data)

@pytest.mark.asynbox async def test_delete_composition(client: AsyncClient, test_composition, test_token):
    """Test deleting a composition."""
    # Make request
    response = await client.delete(
        f"/api/v1/compositions/{test_composition.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify composition was deleted
    response = await client.get(f"/api/v1/compositions/{test_composition.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asynbox async def test_unauthorized_access(client: AsyncClient, test_composition):
    """Test that unauthorized users cannot modify compositions."""
    # Try to update without authentication
    response = await client.put(
        f"/api/v1/compositions/{test_composition.id}",
        json={"name": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to delete without authentication
    response = await client.delete(f"/api/v1/compositions/{test_composition.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to create without authentication
    response = await client.post(
        "/api/v1/compositions/",
        json={"name": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
