"""
Tests for the Professions API endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

from app.models import Profession, EliteSpecialization
from app.schemas.profession import ProfessionCreate, ProfessionUpdate, EliteSpecializationCreate

@pytest.mark.asyncio
async def test_create_profession(client: AsyncClient, admin_token):
    """Test creating a new profession (admin only)."""
    # Test data
    profession_data = {
        "name": "Test Profession",
        "description": "A test profession",
        "icon": "test_icon.png"
    }
    
    # Make request as admin
    response = await client.post(
        "/api/v1/professions/",
        json=profession_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == profession_data["name"]
    assert data["description"] == profession_data["description"]
    assert data["icon"] == profession_data["icon"]

@pytest.mark.asynbox async def test_get_profession(client: AsyncClient, test_profession):
    """Test retrieving a profession by ID."""
    # Make request
    response = await client.get(f"/api/v1/professions/{test_profession.id}")
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_profession.id
    assert data["name"] == test_profession.name

@pytest.mark.asynbox async def test_list_professions(client: AsyncClient, test_profession):
    """Test listing all professions."""
    # Make request
    response = await client.get("/api/v1/professions/")
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(prof["id"] == test_profession.id for prof in data)

@pytest.mark.asynbox async def test_add_elite_specialization(client: AsyncClient, test_profession, admin_token):
    """Test adding an elite specialization to a profession (admin only)."""
    # Test data
    elite_spec_data = {
        "name": "Test Elite Spec",
        "description": "A test elite specialization",
        "icon": "elite_spec_icon.png"
    }
    
    # Make request as admin
    response = await client.post(
        f"/api/v1/professions/{test_profession.id}/elite-specializations",
        json=elite_spec_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "elite_specializations" in data
    assert any(spec["name"] == "Test Elite Spec" for spec in data["elite_specializations"])

@pytest.mark.asynbox async def test_update_profession(client: AsyncClient, test_profession, admin_token):
    """Test updating a profession (admin only)."""
    # Update data
    update_data = {
        "description": "Updated description",
        "icon": "updated_icon.png"
    }
    
    # Make request as admin
    response = await client.put(
        f"/api/v1/professions/{test_profession.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["icon"] == update_data["icon"]

@pytest.mark.asynbox async def test_delete_profession(client: AsyncClient, test_profession, admin_token):
    """Test deleting a profession (admin only)."""
    # Make request as admin
    response = await client.delete(
        f"/api/v1/professions/{test_profession.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify profession was deleted
    response = await client.get(f"/api/v1/professions/{test_profession.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asynbox async def test_unauthorized_access(client: AsyncClient, test_profession, test_token):
    """Test that non-admin users cannot modify professions."""
    # Try to create (non-admin)
    response = await client.post(
        "/api/v1/professions/",
        json={"name": "Should Fail"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Try to update (non-admin)
    response = await client.put(
        f"/api/v1/professions/{test_profession.id}",
        json={"name": "Should Fail"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Try to delete (non-admin)
    response = await client.delete(
        f"/api/v1/professions/{test_profession.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
