"""Integration tests for Team Members API endpoints."""

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import create_access_token
from app.models import User, Team, TeamMember, TeamRole, TeamStatus
from datetime import datetime, timezone

# Test data
TEST_MEMBER_EMAIL = "member@example.com"
TEST_MEMBER_USERNAME = "testmember"
TEST_MEMBER_FULL_NAME = "Test Member"

# Use the async_client fixture from conftest.py instead of redefining it


@pytest_asyncio.fixture
async def test_member_user(db: AsyncSession) -> User:
    """Create a test member user in the database."""
    from app.models import User

    # Create test member user with pre-hashed password
    # This is a pre-hashed version of "test123"
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

    user = User(
        username=TEST_MEMBER_USERNAME,
        email=TEST_MEMBER_EMAIL,
        hashed_password=hashed_password,
        full_name=TEST_MEMBER_FULL_NAME,
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_team(db: AsyncSession, test_user) -> Team:
    """Create a test team in the database."""
    from app.models import Team
    from datetime import datetime, timezone

    # Make sure test_user is awaited if it's a coroutine
    user = await test_user if hasattr(test_user, "__await__") else test_user

    # Create team
    team = Team(
        name="Test Team",
        description="Test Team Description",
        status=TeamStatus.ACTIVE,
        owner_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_public=False,
    )

    db.add(team)
    await db.commit()
    await db.refresh(team)

    return team


class TestTeamMembersAPI:
    """Test cases for Team Members API endpoints."""

    @pytest.mark.asyncio
    async def test_add_team_member(
        self, async_client: AsyncClient, test_user: User, test_team: Team, test_member_user: User, db: AsyncSession
    ) -> None:
        """Test adding a team member."""
        # Add the test member to the team
        user = await test_user if hasattr(test_user, "__await__") else test_user
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user

        access_token = create_access_token(subject=str(user.id))
        response = await async_client.post(
            f"/api/v1/teams/{team.id}/members",
            json={"user_id": str(member_user.id), "role": "member"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == str(test_member_user.id)
        assert data["team_id"] == str(test_team.id)
        assert data["role"] == "member"
        assert data["is_admin"] is False
        assert data["is_active"] is True

        # Verify the member was added to the database
        result = await db.execute(
            select(TeamMember).where((TeamMember.team_id == team.id) & (TeamMember.user_id == member_user.id))
        )
        member = result.scalar_one_or_none()
        assert member is not None
        assert member.role == TeamRole.MEMBER
        assert member.is_admin is False
        assert member.is_active is True

    @pytest.mark.asyncio
    async def test_get_team_member(
        self, async_client: AsyncClient, test_user: User, test_team: Team, test_member_user: User, db: AsyncSession
    ) -> None:
        """Test getting a team member."""
        # Get the team and user objects
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user

        # Add the test member to the team
        team_member = TeamMember(
            team_id=team.id,
            user_id=member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(team_member)
        await db.commit()
        await db.refresh(team_member)

        # Get the team member
        user = await test_user if hasattr(test_user, "__await__") else test_user
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user

        access_token = create_access_token(subject=str(user.id))
        response = await async_client.get(
            f"/api/v1/teams/{team.id}/members/{member_user.id}", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_member_user.id)
        assert data["team_id"] == str(test_team.id)
        assert data["role"] == "member"
        assert data["is_admin"] is False
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_update_team_member(
        self, async_client: AsyncClient, test_user: User, test_team: Team, test_member_user: User, db: AsyncSession
    ) -> None:
        """Test updating a team member."""
        # Get the team and user objects
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user

        # Add the test member to the team
        team_member = TeamMember(
            team_id=team.id,
            user_id=member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(team_member)
        await db.commit()
        await db.refresh(team_member)

        # Update the team member
        user = await test_user if hasattr(test_user, "__await__") else test_user
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user

        update_data = {"role": "officer", "is_admin": True}
        access_token = create_access_token(subject=str(user.id))
        response = await async_client.put(
            f"/api/v1/teams/{team.id}/members/{member_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "officer"
        assert data["is_admin"] is True

        # Verify the member was updated in the database
        await db.refresh(team_member)
        assert team_member.role == TeamRole.OFFICER
        assert team_member.is_admin is True
        assert team_member.is_active is True

    @pytest.mark.asyncio
    async def test_remove_team_member(
        self, async_client: AsyncClient, test_user: User, test_team: Team, test_member_user: User, db: AsyncSession
    ) -> None:
        """Test removing a team member."""
        # Get the team and user objects
        team = await test_team if hasattr(test_team, "__await__") else test_team
        member_user = await test_member_user if hasattr(test_member_user, "__await__") else test_member_user
        user = await test_user if hasattr(test_user, "__await__") else test_user

        # Add the test member to the team
        team_member = TeamMember(
            team_id=team.id,
            user_id=member_user.id,
            role=TeamRole.MEMBER,
            is_admin=False,
            joined_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(team_member)
        await db.commit()
        await db.refresh(team_member)

        access_token = create_access_token(subject=str(user.id))
        response = await async_client.delete(
            f"/api/v1/teams/{team.id}/members/{member_user.id}", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the member was removed from the database
        result = await db.execute(
            select(TeamMember).where((TeamMember.team_id == team.id) & (TeamMember.user_id == member_user.id))
        )
        member = result.scalar_one_or_none()
        assert member is None or member.is_active is False

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self, async_client: AsyncClient, test_team: Team, test_user: User, db: AsyncSession
    ) -> None:
        """Test unauthorized access to team member endpoints."""
        # Get the team and user objects
        team = await test_team if hasattr(test_team, "__await__") else test_team
        user = await test_user if hasattr(test_user, "__await__") else test_user

        # Use the team ID from the created team
        team_id = str(team.id)

        # Define the test cases
        test_cases = [
            # (endpoint, method, data)
            (f"/api/v1/teams/{team_id}/members", "GET", None),
            (f"/api/v1/teams/{team_id}/members/123", "GET", None),
            (f"/api/v1/teams/{team_id}/members/123", "PUT", {"role": "member"}),
            (f"/api/v1/teams/{team_id}/members/123", "DELETE", None),
        ]

        # Test without authentication
        for endpoint, method, data in test_cases:
            if method == "GET":
                response = await async_client.get(endpoint)
            elif method == "POST":
                response = await async_client.post(endpoint, json=data)
            elif method == "PUT":
                response = await async_client.put(endpoint, json=data)
            elif method == "DELETE":
                response = await async_client.delete(endpoint)

            assert (
                response.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Expected 401 for {method} {endpoint} without auth, got {response.status_code}"

        # Test with invalid token
        for endpoint, method, data in test_cases:
            headers = {"Authorization": "Bearer invalid_token"}
            if method == "GET":
                response = await async_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await async_client.post(endpoint, json=data, headers=headers)
            elif method == "PUT":
                response = await async_client.put(endpoint, json=data, headers=headers)
            elif method == "DELETE":
                response = await async_client.delete(endpoint, headers=headers)

            assert (
                response.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Expected 401 for {method} {endpoint} with invalid token, got {response.status_code}"

        # Test with valid token but no permissions
        another_user_id = "11111111-1111-1111-1111-111111111111"
        access_token = create_access_token(subject=another_user_id)

        # Get the team object if it hasn't been retrieved yet
        if "team" not in locals():
            team = await test_team if hasattr(test_team, "__await__") else test_team

        for endpoint, method, data in test_cases:
            headers = {"Authorization": f"Bearer {access_token}"}
            if method == "GET":
                response = await async_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await async_client.post(endpoint, json=data, headers=headers)
            elif method == "PUT":
                response = await async_client.put(endpoint, json=data, headers=headers)
            elif method == "DELETE":
                response = await async_client.delete(endpoint, headers=headers)

            # The endpoint might return 403 (Forbidden) or 404 (Not Found) depending on the implementation
            assert response.status_code in (
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ), f"Expected 403 or 404 for {method} {endpoint} with no permissions, got {response.status_code}"
