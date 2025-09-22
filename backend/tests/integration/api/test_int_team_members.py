"""Integration tests for Team Members API endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models import User, Team, TeamMember, TeamRole, TeamStatus
from datetime import datetime, timezone
from typing import Dict, Any

# Test data
TEST_MEMBER_EMAIL = "member@example.com"
TEST_MEMBER_USERNAME = "testmember"
TEST_MEMBER_FULL_NAME = "Test Member"


@pytest.fixture
async def test_member_user(async_db_session: AsyncSession) -> User:
    """Create a test member user."""
    from app.core.security import get_password_hash
    
    user = User(
        username=TEST_MEMBER_USERNAME,
        email=TEST_MEMBER_EMAIL,
        hashed_password=get_password_hash("testpassword"),
        full_name=TEST_MEMBER_FULL_NAME,
        is_active=True,
        is_superuser=False,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def test_team(async_db_session: AsyncSession, test_user: User) -> Team:
    """Create a test team."""
    team = Team(
        name="Test Team",
        description="Test Team Description",
        status=TeamStatus.ACTIVE,
        owner_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_public=False
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
        is_active=True
    )
    async_db_session.add(team_member)
    await async_db_session.commit()
    
    return team


class TestTeamMembersAPI:
    """Test cases for Team Members API endpoints."""

    async def test_add_team_member(
        self, 
        async_client: TestClient, 
        test_user: User,
        test_member_user: User,
        test_team: Team
    ) -> None:
        """Test adding a member to a team."""
        # Create an access token for the test user (team owner/admin)
        access_token = create_access_token(subject=test_user.id)
        
        # Prepare the request data
        member_data = {
            "user_id": test_member_user.id,
            "role": "member",
            "is_admin": False
        }
        
        # Make the request
        response = await async_client.post(
            f"/api/v1/teams/{test_team.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["team_id"] == test_team.id
        assert data["user_id"] == test_member_user.id
        assert data["role"] == member_data["role"]
        assert data["is_admin"] == member_data["is_admin"]
        assert data["is_active"] is True

    async def test_get_team_member(
        self, 
        async_client: TestClient, 
        test_user: User,
        test_team: Team,
        test_member_user: User,
        async_db_session: AsyncSession
    ) -> None:
        """Test getting a team member."""
        # Add the test member to the team
        team_member = TeamMember(
            team_id=test_team.id,
            user_id=test_member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True
        )
        async_db_session.add(team_member)
        await async_db_session.commit()
        
        # Create an access token for the test user
        access_token = create_access_token(subject=test_user.id)
        
        # Make the request
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}/members/{test_member_user.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["team_id"] == test_team.id
        assert data["user_id"] == test_member_user.id
        assert data["role"] == "member"
        assert data["is_admin"] is False
        assert data["is_active"] is True

    async def test_update_team_member(
        self, 
        async_client: TestClient, 
        test_user: User,
        test_team: Team,
        test_member_user: User,
        async_db_session: AsyncSession
    ) -> None:
        """Test updating a team member."""
        # Add the test member to the team
        team_member = TeamMember(
            team_id=test_team.id,
            user_id=test_member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True
        )
        async_db_session.add(team_member)
        await async_db_session.commit()
        
        # Create an access token for the test user (admin/owner)
        access_token = create_access_token(subject=test_user.id)
        
        # Prepare the update data
        update_data = {
            "role": "officer",
            "is_admin": True
        }
        
        # Make the request
        response = await async_client.put(
            f"/api/v1/teams/{test_team.id}/members/{test_member_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["team_id"] == test_team.id
        assert data["user_id"] == test_member_user.id
        assert data["role"] == update_data["role"]
        assert data["is_admin"] == update_data["is_admin"]
        assert data["is_active"] is True

    async def test_remove_team_member(
        self, 
        async_client: TestClient, 
        test_user: User,
        test_team: Team,
        test_member_user: User,
        async_db_session: AsyncSession
    ) -> None:
        """Test removing a team member."""
        # Add the test member to the team
        team_member = TeamMember(
            team_id=test_team.id,
            user_id=test_member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True
        )
        async_db_session.add(team_member)
        await async_db_session.commit()
        
        # Create an access token for the test user (admin/owner)
        access_token = create_access_token(subject=test_user.id)
        
        # Make the request to remove the member
        response = await async_client.delete(
            f"/api/v1/teams/{test_team.id}/members/{test_member_user.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the member was removed
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}/members/{test_member_user.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_unauthorized_access(
        self, 
        async_client: TestClient, 
        test_team: Team,
        test_member_user: User
    ) -> None:
        """Test unauthorized access to team member endpoints."""
        # Try to access team member endpoints without authentication
        response = await async_client.get(f"/api/v1/teams/{test_team.id}/members")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try to access team member endpoints with an invalid token
        response = await async_client.get(
            f"/api/v1/teams/{test_team.id}/members",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
