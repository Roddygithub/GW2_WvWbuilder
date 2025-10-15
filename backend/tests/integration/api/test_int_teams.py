"""Integration tests for Teams API endpoints."""

import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models import User, Team, TeamMember, TeamStatus, TeamRole
from datetime import datetime, timezone
from typing import Dict, Any

# Test data
TEST_TEAM_NAME = "Test Team"
TEST_TEAM_DESCRIPTION = "Test Team Description"
TEST_TEAM_UPDATE_NAME = "Updated Test Team"
TEST_TEAM_UPDATE_DESCRIPTION = "Updated Test Team Description"


@pytest.fixture
def team_data() -> Dict[str, Any]:
    """Return test team data."""
    return {
        "name": TEST_TEAM_NAME,
        "description": TEST_TEAM_DESCRIPTION,
        "status": "active",
        "is_public": False,
    }


@pytest.fixture
def update_team_data() -> Dict[str, Any]:
    """Return updated test team data."""
    return {
        "name": TEST_TEAM_UPDATE_NAME,
        "description": TEST_TEAM_UPDATE_DESCRIPTION,
        "status": "inactive",
        "is_public": True,
    }


@pytest_asyncio.fixture
async def test_team(async_db_session: AsyncSession, test_user: User) -> Team:
    """Create a test team."""
    team = Team(
        name=TEST_TEAM_NAME,
        description=TEST_TEAM_DESCRIPTION,
        status=TeamStatus.ACTIVE,
        owner_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_public=False,
    )
    async_db_session.add(team)
    await async_db_session.commit()
    await async_db_session.refresh(team)

    # Add the owner as a team member
    team_member = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role=TeamRole.LEADER,
        is_admin=True,
        joined_at=datetime.now(timezone.utc),
        is_active=True,
    )
    async_db_session.add(team_member)
    await async_db_session.commit()

    return team


@pytest_asyncio.fixture
async def test_team_member(
    async_db_session: AsyncSession, test_team: Team, test_user: User
) -> TeamMember:
    """Create a test team member."""
    team_member = TeamMember(
        team_id=test_team.id,
        user_id=test_user.id,
        role=TeamRole.MEMBER,
        is_admin=False,
        joined_at=datetime.now(timezone.utc),
        is_active=True,
    )
    async_db_session.add(team_member)
    await async_db_session.commit()
    await async_db_session.refresh(team_member)
    return team_member


class TestTeamsAPI:
    """Test cases for Teams API endpoints."""

    async def test_create_team(
        self, async_client: TestClient, test_user: User, team_data: Dict[str, Any]
    ) -> None:
        """Test creating a new team."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.post(
            "/api/v1/teams/",
            json=team_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["name"] == team_data["name"]
        assert data["description"] == team_data["description"]
        assert data["status"] == team_data["status"]
        assert data["is_public"] == team_data["is_public"]
        assert data["owner_id"] == test_user.id

    async def test_read_teams(
        self, async_client: TestClient, test_user: User, test_team: Team
    ) -> None:
        """Test reading a list of teams."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            "/api/v1/teams/", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(team["id"] == test_team.id for team in data)

    async def test_read_team(
        self, async_client: TestClient, test_user: User, test_team: Team
    ) -> None:
        """Test reading a specific team."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_team.id
        assert data["name"] == test_team.name
        assert data["description"] == test_team.description

    async def test_update_team(
        self,
        async_client: TestClient,
        test_user: User,
        test_team: Team,
        update_team_data: Dict[str, Any],
    ) -> None:
        """Test updating a team."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.put(
            f"/api/v1/teams/{test_team.id}",
            json=update_team_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_team.id
        assert data["name"] == update_team_data["name"]
        assert data["description"] == update_team_data["description"]
        assert data["status"] == update_team_data["status"]
        assert data["is_public"] == update_team_data["is_public"]

    async def test_delete_team(
        self, async_client: TestClient, test_user: User, test_team: Team
    ) -> None:
        """Test deleting a team."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.delete(
            f"/api/v1/teams/{test_team.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Verify the response
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the team was deleted
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_public_teams(
        self, async_client: TestClient, test_user: User, test_team: Team
    ) -> None:
        """Test getting public teams."""
        # Update the test team to be public
        test_team.is_public = True

        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            "/api/v1/teams/public", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(team["id"] == test_team.id for team in data)

    async def test_get_team_members(
        self,
        async_client: TestClient,
        test_user: User,
        test_team: Team,
        test_team_member: TeamMember,
    ) -> None:
        """Test getting team members."""
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)

        # Make the request
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(member["user_id"] == test_user.id for member in data)

    async def test_unauthorized_access(
        self, async_client: TestClient, test_team: Team
    ) -> None:
        """Test unauthorized access to team endpoints."""
        # Try to access team endpoints without authentication
        response = await async_client.get(f"/api/v1/teams/{test_team.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to access team endpoints with an invalid token
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
