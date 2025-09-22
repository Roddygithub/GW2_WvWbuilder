"""
Tests for the Compositions API endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Composition, composition_members


@pytest.mark.asyncio
async def test_create_composition(async_client, test_user, test_tokens, db_session):
    """Test creating a new composition."""
    # Utiliser les fixtures test_user et test_tokens
    test_token = test_tokens["user"]

    # S'assurer que la session est valide
    await db_session.execute("SELECT 1")

    # Afficher les tables disponibles pour le débogage
    result = await db_session.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    tables = [row[0] for row in result.fetchall()]
    print(f"Tables disponibles dans la base de données: {tables}")

    # Rafraîchir l'utilisateur pour s'assurer qu'il est lié à la session
    await db_session.refresh(test_user)

    # Test data
    composition_data = {
        "name": "Test Composition",
        "description": "A test composition",
        "game_mode": "wvw",
        "is_public": True,
        "squad_size": 10,
        "min_players": 5,
        "max_players": 10,
    }

    # Make request
    response = await async_client.post(
        "/api/v1/compositions/",
        json=composition_data,
        headers={"Authorization": f"Bearer {test_token}"},
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

    # Verify composition was created in database
    result = await db_session.execute(
        select(Composition).filter_by(name="Test Composition")
    )
    composition = result.scalar_one_or_none()
    assert composition is not None
    assert composition.description == "A test composition"
    assert composition.game_mode == "wvw"


@pytest.mark.asyncio(scope="function")
async def test_get_composition(async_client: AsyncClient, test_composition):
    """Test retrieving a composition by ID."""
    # Make request
    response = await async_client.get(f"/api/v1/compositions/{test_composition.id}")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_composition.id
    assert data["name"] == test_composition.name


@pytest.mark.asyncio
async def test_update_composition(
    async_client: AsyncClient, test_composition, test_token, db_session
):
    """Test updating a composition."""
    # Update data
    update_data = {
        "name": "Updated Composition",
        "description": "Updated description",
        "is_public": False,
        "squad_size": 15,
        "min_players": 8,
        "max_players": 12,
    }

    # Make request
    response = await async_client.put(
        f"/api/v1/compositions/{test_composition.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_public"] == update_data["is_public"]
    assert data["min_players"] == update_data["min_players"]
    assert data["max_players"] == update_data["max_players"]

    # Verify update in database
    result = await db_session.execute(
        select(Composition).filter_by(id=test_composition.id)
    )
    updated = result.scalar_one_or_none()
    assert updated is not None
    assert updated.name == "Updated Composition"
    assert updated.description == "Updated description"


@pytest.mark.asyncio
async def test_add_build_to_composition(
    async_client: AsyncClient,
    test_composition,
    test_build,
    test_user,
    test_token,
    db_session,
):
    """Test adding a build to a composition."""
    # Test member data
    member_data = {
        "user_id": test_user.id,
        "role_id": 1,  # Assuming role with ID 1 exists
        "profession_id": 1,  # Assuming profession with ID 1 exists
        "elite_specialization_id": 1,  # Assuming elite spec with ID 1 exists
        "role_type": "DPS",
        "is_commander": False,
        "is_secondary_commander": False,
        "priority": 1,
    }

    # Make request
    response = await async_client.post(
        f"/api/v1/compositions/{test_composition.id}/members",
        json=member_data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["composition_id"] == test_composition.id
    assert data["user_id"] == test_user.id

    # Verify member was added in database
    result = await db_session.execute(
        select(composition_members)
        .where(composition_members.c.composition_id == test_composition.id)
        .where(composition_members.c.user_id == test_user.id)
    )
    member = result.fetchone()
    assert member is not None
    assert member.role_id == 1  # Vérifie que le rôle a bien été défini

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["build_id"] == test_build.id
    assert data["members"][0]["role"] == "DPS"


@pytest.mark.asyncio(scope="function")
async def test_add_tag_to_composition(
    client: AsyncClient, test_composition, test_token
):
    """Test adding a tag to a composition."""
    # Test tag data
    tag_data = {"name": "test_tag"}

    # Make request
    response = await client.post(
        f"/api/v1/compositions/{test_composition.id}/tags",
        json=tag_data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "tags" in data
    assert any(tag["name"] == "test_tag" for tag in data["tags"])


@pytest.mark.asyncio(scope="function")
async def test_list_public_compositions(client: AsyncClient, test_composition):
    """Test listing public compositions."""
    # Make request
    response = await client.get("/api/v1/compositions/")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(comp["id"] == test_composition.id for comp in data)


@pytest.mark.asyncio(scope="function")
async def test_delete_composition(client: AsyncClient, test_composition, test_token):
    """Test deleting a composition."""
    # Make request
    response = await client.delete(
        f"/api/v1/compositions/{test_composition.id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # Verify response
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify composition was deleted
    response = await client.get(f"/api/v1/compositions/{test_composition.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(scope="function")
async def test_unauthorized_access(client: AsyncClient, test_composition):
    """Test that unauthorized users cannot modify compositions."""
    # Try to update without authentication
    response = await client.put(
        f"/api/v1/compositions/{test_composition.id}", json={"name": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to delete without authentication
    response = await client.delete(f"/api/v1/compositions/{test_composition.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to create without authentication
    response = await client.post("/api/v1/compositions/", json={"name": "Should Fail"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
