"""Tests for elite specialization endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from app.main import app
from app.models import Profession, EliteSpecialization
from app.schemas import EliteSpecializationCreate, EliteSpecializationUpdate

@pytest.fixture
def admin_token_headers(async_client: AsyncClient):
    """Get admin token headers for authentication."""
    return {"Authorization": "Bearer test_token:1"}  # admin user ID is 1

@pytest.fixture
async def test_profession(async_session: AsyncSession):
    """Create a test profession for elite specialization tests."""
    profession = Profession(
        name="Test Profession",
        description="Test profession for elite specs",
        icon_url="https://example.com/test.png"
    )
    async_session.add(profession)
    await async_session.commit()
    await async_session.refresh(profession)
    return profession

@pytest.mark.asyncio
async def test_create_elite_specialization(async_client: AsyncClient, async_session: AsyncSession, admin_token_headers, test_profession):
    """Test creating a new elite specialization."""
    profession_id = test_profession.id

    payload = {
        "name": "Reaper",
        "profession_id": profession_id,
        "description": "Spécialisation élite du nécromant",
        "weapon_type": "Greatsword",
        "icon_url": "https://example.com/reaper_icon.png",
        "background_url": "https://example.com/reaper_bg.png",
        "is_active": True,
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=payload,
        headers=admin_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["profession_id"] == profession_id
    assert data["weapon_type"] == "Greatsword"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_elite_specialization(async_client: AsyncClient, async_session: AsyncSession, admin_token_headers, test_profession):
    """Test updating an elite specialization."""
    profession_id = test_profession.id

    payload = {
        "name": "Druid",
        "profession_id": profession_id,
        "description": "Spécialisation élite du rôdeur",
        "weapon_type": "Staff",
        "icon_url": "https://example.com/druid_icon.png",
        "background_url": "https://example.com/druid_bg.png",
        "is_active": True,
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=payload,
        headers=admin_token_headers
    )
    elite_id = response.json()["id"]

    update_payload = {
        "is_active": False,
        "weapon_type": "Staff, Astral Wrath"
    }
    response = await async_client.put(
        f"/api/v1/elite-specializations/{elite_id}", 
        json=update_payload,
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["weapon_type"] == "Staff, Astral Wrath"
    assert "updated_at" in data
    assert data["updated_at"] != data["created_at"]


@pytest.mark.asyncio
async def test_read_elite_specialization(async_client: AsyncClient, async_session: AsyncSession, admin_token_headers, test_profession):
    """Test reading an elite specialization."""
    profession_id = test_profession.id

    payload = {
        "name": "Chronomancer",
        "profession_id": profession_id,
        "description": "Spécialisation élite de l'envoûteur",
        "weapon_type": "Shield, Time Warp",
        "icon_url": "https://example.com/chrono_icon.png",
        "background_url": "https://example.com/chrono_bg.png",
        "is_active": True,
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=payload,
        headers=admin_token_headers
    )
    elite_id = response.json()["id"]

    # Test read by ID
    response = await async_client.get(f"/api/v1/elite-specializations/{elite_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chronomancer"
    assert data["weapon_type"] == "Shield, Time Warp"
    assert data["profession_id"] == profession_id

    # Test list all
    response = await async_client.get("/api/v1/elite-specializations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(es["id"] == elite_id for es in data)


@pytest.mark.asyncio
async def test_delete_elite_specialization(async_client: AsyncClient, async_session: AsyncSession, admin_token_headers, test_profession):
    """Test deleting an elite specialization."""
    profession_id = test_profession.id

    payload = {
        "name": "Holosmith",
        "profession_id": profession_id,
        "description": "Spécialisation élite de l'ingénieur",
        "weapon_type": "Sword, Photon Forge",
        "icon_url": "https://example.com/holo_icon.png",
        "background_url": "https://example.com/holo_bg.png",
        "is_active": True,
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=payload,
        headers=admin_token_headers
    )
    elite_id = response.json()["id"]

    # Test delete
    response = await async_client.delete(
        f"/api/v1/elite-specializations/{elite_id}",
        headers=admin_token_headers
    )
    assert response.status_code == 204

    # Verify deletion
    response = await async_client.get(f"/api/v1/elite-specializations/{elite_id}")
    assert response.status_code == 404

    # Test delete non-existent
    response = await async_client.delete(
        "/api/v1/elite-specializations/999999",
        headers=admin_token_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_elite_specialization_validation(async_client: AsyncClient, async_session: AsyncSession, admin_token_headers, test_profession):
    """Test validation of elite specialization data."""
    profession_id = test_profession.id

    # Test missing required fields
    payload = {
        # Missing name and profession_id
        "description": "Test description",
        "is_active": True
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=payload,
        headers=admin_token_headers
    )
    assert response.status_code == 422
    
    # Test invalid profession_id
    invalid_payload = {
        "name": "Test Spec",
        "profession_id": 999999,  # Non-existent profession
        "is_active": True
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=invalid_payload,
        headers=admin_token_headers
    )
    assert response.status_code == 400
    
    # Test valid payload
    valid_payload = {
        "name": "Tempest",
        "profession_id": profession_id,
        "description": "Spécialisation élite de l'élémentaire",
        "weapon_type": "Warhorn",
        "is_active": True,
        "icon_url": "https://example.com/tempest_icon.png"
    }
    response = await async_client.post(
        "/api/v1/elite-specializations/", 
        json=valid_payload,
        headers=admin_token_headers
    )
    assert response.status_code == 201
