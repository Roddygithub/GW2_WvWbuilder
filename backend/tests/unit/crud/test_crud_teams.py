"""Tests for team CRUD operations."""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_team import CRUDTeam
from app.models import Team, TeamStatus, User, Build, Composition, Profession, Role
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamRole,
    TeamStatus as TeamStatusEnum,
)

# Create an instance of CRUDTeam for testing
team_crud = CRUDTeam(Team)

# Test data
TEST_TEAM_NAME = "Test Team"
TEST_DESCRIPTION = "Test Team Description"
TEST_STATUS = "active"
TEST_TEAM_ID = 1
TEST_USER_ID = 1
TEST_BUILD_ID = 1
TEST_COMPOSITION_ID = 1
TEST_PROFESSION_ID = 1
TEST_ROLE_ID = 1


# Fixtures
@pytest.fixture
def team_data():
    """Return test team data."""
    from app.schemas.team import TeamCreate

    return TeamCreate(
        name=TEST_TEAM_NAME,
        description=TEST_DESCRIPTION,
        status=TeamStatusEnum.ACTIVE,
    )


@pytest.fixture
def mock_team():
    """Create a mock team object."""
    return Team(
        id=TEST_TEAM_ID,
        name=TEST_TEAM_NAME,
        description=TEST_DESCRIPTION,
        status=TeamStatus.ACTIVE,
        owner_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession):
    """Create a test user with a unique username and email."""
    from app.core.security import get_password_hash
    import uuid

    # Generate a unique identifier for this test user
    unique_id = str(uuid.uuid4())[:8]  # Take first 8 chars of UUID
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash("testpassword"),
        full_name=f"Test User {unique_id}",
        is_active=True,
        is_superuser=False,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
def mock_build():
    """Create a mock build object."""
    return Build(
        id=TEST_BUILD_ID,
        name="Test Build",
        description="Test Build Description",
        game_mode="pvp",
        team_size=5,
        is_public=True,
        created_by_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_composition():
    """Create a mock composition object."""
    return Composition(
        id=TEST_COMPOSITION_ID,
        name="Test Composition",
        description="Test Composition Description",
        squad_size=5,
        is_public=True,
        created_by=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_profession():
    """Create a mock profession object."""
    return Profession(
        id=TEST_PROFESSION_ID,
        name="Test Profession",
        icon_url="test_icon.png",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_role():
    """Create a mock role object."""
    return Role(
        id=TEST_ROLE_ID,
        name="Test Role",
        description="Test Role Description",
        permission_level=1,
        is_default=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# Test CRUDTeam class
@pytest.mark.asyncio
class TestCRUDTeam:
    """Test cases for CRUDTeam class."""

    @pytest.mark.asyncio
    async def test_create_team_success(self, async_db_session: AsyncSession, test_user: User):
        """Test creating a team with valid data."""
        # Create test data
        team_data = TeamCreate(
            name="Test Team",
            description="Test Team Description",
            status=TeamStatusEnum.ACTIVE,
        )

        # Create the team
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Verify the team was created
        assert team.id is not None
        assert team.name == team_data.name
        assert team.description == team_data.description
        assert team.owner_id == test_user.id
        assert team.status == TeamStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_get_team(self, async_db_session: AsyncSession, test_user: User):
        """Test getting a team by ID."""
        # Create a test team
        team_data = TeamCreate(
            name="Test Team",
            description="Test Team Description",
            status=TeamStatusEnum.ACTIVE,
        )
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Get the team using async method
        retrieved_team = await team_crud.get_async(async_db_session, id=team.id)

        # Verify the team was retrieved
        assert retrieved_team is not None
        assert retrieved_team.id == team.id
        assert retrieved_team.name == team_data.name
        assert retrieved_team.description == team_data.description

    @pytest.mark.asyncio
    async def test_get_teams_by_owner(self, async_db_session: AsyncSession, test_user: User):
        """Test getting teams by owner ID."""
        # Create test teams
        team1_data = TeamCreate(
            name="Team 1",
            description="Team 1 Description",
            status=TeamStatusEnum.ACTIVE,
        )
        team2_data = TeamCreate(
            name="Team 2",
            description="Team 2 Description",
            status=TeamStatusEnum.INACTIVE,
        )

        await team_crud.create_with_owner(db=async_db_session, obj_in=team1_data, owner_id=test_user.id)
        await team_crud.create_with_owner(db=async_db_session, obj_in=team2_data, owner_id=test_user.id)

        # Get teams by owner
        teams = await team_crud.get_multi_by_owner(async_db_session, owner_id=test_user.id)

        # Verify the teams were retrieved
        assert len(teams) == 2
        assert any(t.name == "Team 1" for t in teams)
        assert any(t.name == "Team 2" for t in teams)

    @pytest.mark.asyncio
    async def test_update_team(self, async_db_session: AsyncSession, test_user: User):
        """Test updating a team."""
        # Create a team to update
        team_data = TeamCreate(
            name="Team to Update",
            description="This team will be updated",
            status=TeamStatusEnum.ACTIVE,
        )
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Get the team to update
        db_team = await team_crud.get_async(async_db_session, id=team.id)
        assert db_team is not None

        # Update the team
        update_data = TeamUpdate(
            name="Updated Team Name",
            description="Updated Description",
            status=TeamStatusEnum.INACTIVE,
        )
        updated_team = await team_crud.update_async(async_db_session, db_obj=db_team, obj_in=update_data)

        # Verify the team was updated
        assert updated_team.name == update_data.name
        assert updated_team.description == update_data.description
        assert updated_team.status == update_data.status

    @pytest.mark.asyncio
    async def test_remove_team(self, async_db_session: AsyncSession, test_user: User):
        """Test removing a team."""
        # Create a team to remove
        team_data = TeamCreate(
            name="Team to Remove",
            description="This team will be removed",
            status=TeamStatusEnum.ACTIVE,
        )
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Get the team ID before removal
        team_id = team.id

        # Remove the team using async method
        removed_team = await team_crud.remove_async(db=async_db_session, id=team_id)

        # Verify the team was removed
        assert removed_team is not None
        assert removed_team.id == team_id

        # Verify the team no longer exists
        team = await team_crud.get_async(db=async_db_session, id=team_id)
        assert team is None

    @pytest.mark.asyncio
    async def test_add_member_to_team(self, async_db_session: AsyncSession, test_user: User):
        """Test adding a member to a team."""
        # Create a test team
        team_data = TeamCreate(
            name="Team with Members",
            description="Team for testing member operations",
            status=TeamStatusEnum.ACTIVE,
        )
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Create a test user to add as member
        test_member = User(
            username="testmember",
            email="member@example.com",
            hashed_password="hashedpassword",
            is_active=True,
        )
        async_db_session.add(test_member)
        await async_db_session.commit()
        await async_db_session.refresh(test_member)

        # Add member to team
        success = await team_crud.add_member(
            async_db_session, team_id=team.id, user_id=test_member.id, role=TeamRole.MEMBER
        )

        # Verify the member was added
        assert success is True

        # Get the team with members
        await team_crud.get_async(async_db_session, id=team.id)
        members = await team_crud.get_members(async_db_session, team_id=team.id)

        assert len(members) == 1
        assert members[0].id == test_member.id

    @pytest.mark.asyncio
    async def test_remove_member_from_team(self, async_db_session: AsyncSession, test_user: User):
        """Test removing a member from a team."""
        # Create a team
        team_data = TeamCreate(
            name="Team with Members",
            description="A team with members",
            status=TeamStatusEnum.ACTIVE,
        )
        team = await team_crud.create_with_owner(db=async_db_session, obj_in=team_data, owner_id=test_user.id)

        # Create a test user to add as a member
        from app.core.security import get_password_hash
        from uuid import uuid4

        # Generate unique username and email
        unique_id = str(uuid4())[:8]
        member = User(
            username=f"testmember_{unique_id}",
            email=f"member_{unique_id}@example.com",
            hashed_password=get_password_hash("testpassword"),
            full_name=f"Test Member {unique_id}",
            is_active=True,
        )
        async_db_session.add(member)
        await async_db_session.commit()
        await async_db_session.refresh(member)

        # Add the member to the team
        member_added = await team_crud.add_member(
            db=async_db_session, team_id=team.id, user_id=member.id, role="member"
        )
        assert member_added is True

        # Remove the member from the team
        member_removed = await team_crud.remove_member(db=async_db_session, team_id=team.id, user_id=member.id)
        assert member_removed is True

        # Verify the member is no longer in the team
        members = await team_crud.get_members(db=async_db_session, team_id=team.id)
        assert len(members) == 0


# Test the team instance
class TestTeamInstance:
    """Test cases for the team instance."""

    def test_team_instance_creation(self):
        """Test that the team instance is created correctly."""
        # Test that the team instance is created correctly
        from app.crud.crud_team import CRUDTeam

        assert isinstance(team_crud, CRUDTeam)

    def test_team_instance_methods(self):
        """Test that the team instance has the expected methods."""
        # Test that the team instance has the expected methods
        assert hasattr(team_crud, "get")
        assert hasattr(team_crud, "get_multi")
        assert hasattr(team_crud, "create")
        assert hasattr(team_crud, "update")
        assert hasattr(team_crud, "remove")
        assert hasattr(team_crud, "get_multi_by_owner")
        assert hasattr(team_crud, "add_member")
        assert hasattr(team_crud, "remove_member")
        assert hasattr(team_crud, "get_members")
