"""Integration tests for Tags API endpoints."""

import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models import User, Tag, Composition, CompositionTag, Team, TeamStatus
from datetime import datetime, timezone
from typing import Dict, Any

# Test data
TEST_TAG_NAME = "Test Tag"
TEST_TAG_DESCRIPTION = "Test Tag Description"
TEST_TAG_UPDATE_NAME = "Updated Test Tag"
TEST_TAG_UPDATE_DESCRIPTION = "Updated Test Tag Description"
TEST_COMPOSITION_NAME = "Test Composition"
TEST_COMPOSITION_DESCRIPTION = "Test Composition Description"


@pytest.fixture
def tag_data() -> Dict[str, Any]:
    """Return test tag data."""
    return {"name": TEST_TAG_NAME, "description": TEST_TAG_DESCRIPTION, "color": "#FF0000"}


@pytest.fixture
def update_tag_data() -> Dict[str, Any]:
    """Return updated test tag data."""
    return {"name": TEST_TAG_UPDATE_NAME, "description": TEST_TAG_UPDATE_DESCRIPTION, "color": "#00FF00"}


@pytest_asyncio.fixture
async def test_tag(async_db_session: AsyncSession, test_user: User) -> Tag:
    """Create a test tag."""
    tag = Tag(
        name=TEST_TAG_NAME,
        description=TEST_TAG_DESCRIPTION,
        color="#FF0000",
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    async_db_session.add(tag)
    await async_db_session.commit()
    await async_db_session.refresh(tag)
    return tag


@pytest_asyncio.fixture
async def test_team(async_db_session: AsyncSession, test_user: User) -> Team:
    """Create a test team."""
    team = Team(
        name="Test Team",
        description="Test Team Description",
        status=TeamStatus.ACTIVE,
        owner_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_public=True,
    )
    async_db_session.add(team)
    await async_db_session.commit()
    await async_db_session.refresh(team)
    return team


@pytest_asyncio.fixture
async def test_composition(async_db_session: AsyncSession, test_user: User, test_team: Team) -> Composition:
    """Create a test composition."""
    composition = Composition(
        name=TEST_COMPOSITION_NAME,
        description=TEST_COMPOSITION_DESCRIPTION,
        squad_size=5,
        is_public=True,
        created_by=test_user.id,
        team_id=test_team.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    async_db_session.add(composition)
    await async_db_session.commit()
    await async_db_session.refresh(composition)
    return composition


@pytest_asyncio.fixture
async def test_composition_tag(
    async_db_session: AsyncSession, test_tag: Tag, test_composition: Composition
) -> CompositionTag:
    """Create a test composition tag association."""
    composition_tag = CompositionTag(
        composition_id=test_composition.id, tag_id=test_tag.id, created_at=datetime.now(timezone.utc)
    )
    async_db_session.add(composition_tag)
    await async_db_session.commit()
    await async_db_session.refresh(composition_tag)
    return composition_tag


class TestTagsAPI:
    """Test cases for Tags API endpoints."""

    async def test_create_tag(self, async_client: TestClient, test_user: User, tag_data: Dict[str, Any]) -> None:
        """Test creating a new tag."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.post(
            "/api/v1/tags/", json=tag_data, headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["name"] == tag_data["name"]
        assert data["description"] == tag_data["description"]
        assert data["color"] == tag_data["color"]
        assert data["created_by"] == test_user.id

    async def test_read_tags(self, async_client: TestClient, test_user: User, test_tag: Tag) -> None:
        """Test reading a list of tags."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get("/api/v1/tags/", headers={"Authorization": f"Bearer {access_token}"})

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(tag["id"] == test_tag.id for tag in data)

    async def test_read_tag(self, async_client: TestClient, test_user: User, test_tag: Tag) -> None:
        """Test reading a specific tag."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            f"/api/v1/tags/{test_tag.id}", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_tag.id
        assert data["name"] == test_tag.name
        assert data["description"] == test_tag.description

    async def test_update_tag(
        self, async_client: TestClient, test_user: User, test_tag: Tag, update_tag_data: Dict[str, Any]
    ) -> None:
        """Test updating a tag."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.put(
            f"/api/v1/tags/{test_tag.id}", json=update_tag_data, headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_tag.id
        assert data["name"] == update_tag_data["name"]
        assert data["description"] == update_tag_data["description"]
        assert data["color"] == update_tag_data["color"]

    async def test_delete_tag(self, async_client: TestClient, test_user: User, test_tag: Tag) -> None:
        """Test deleting a tag."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.delete(
            f"/api/v1/tags/{test_tag.id}", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the tag was deleted
        response = await async_client.get(
            f"/api/v1/tags/{test_tag.id}", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_most_used_tags(
        self, async_client: TestClient, test_user: User, test_tag: Tag, test_composition_tag: CompositionTag
    ) -> None:
        """Test getting the most used tags."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            "/api/v1/tags/stats/most-used", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(tag["id"] == test_tag.id for tag in data)

        # Verify the tag has the correct usage count
        tag_data = next(tag for tag in data if tag["id"] == test_tag.id)
        assert tag_data["usage_count"] == 1

    async def test_unauthorized_access(self, async_client: TestClient, test_tag: Tag) -> None:
        """Test unauthorized access to tag endpoints."""
        # Try to access tag endpoints without authentication
        response = await async_client.get(f"/api/v1/tags/{test_tag.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to access tag endpoints with an invalid token
        response = await async_client.get(
            f"/api/v1/tags/{test_tag.id}", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
