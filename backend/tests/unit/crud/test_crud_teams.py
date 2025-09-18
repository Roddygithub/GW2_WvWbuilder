"""Tests for team CRUD operations."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from app.crud.crud_team import team as crud_team, CRUDTeam
from app.models import Team, User, Build, Composition, Profession, Role
from app.schemas.team import (
    TeamCreate, 
    TeamUpdate, 
    TeamMemberCreate,
    TeamRole,
    TeamStatus
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException,
    UnauthorizedException
)

# Test data
TEST_TEAM_NAME = "Test Team"
TEST_DESCRIPTION = "Test Team Description"
TEST_GAME_MODE = "wvw"
TEST_MAX_MEMBERS = 10
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
    return {
        "name": TEST_TEAM_NAME,
        "description": TEST_DESCRIPTION,
        "game_mode": TEST_GAME_MODE,
        "max_members": TEST_MAX_MEMBERS,
        "status": TeamStatus.ACTIVE,
    }

@pytest.fixture
def mock_team():
    """Create a mock team object."""
    return Team(
        id=TEST_TEAM_ID,
        name=TEST_TEAM_NAME,
        description=TEST_DESCRIPTION,
        game_mode=TEST_GAME_MODE,
        max_members=TEST_MAX_MEMBERS,
        status=TeamStatus.ACTIVE,
        created_by_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    return User(
        id=TEST_USER_ID,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_build():
    """Create a mock build object."""
    return Build(
        id=TEST_BUILD_ID,
        name="Test Build",
        description="Test Build Description",
        game_mode=TEST_GAME_MODE,
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
class TestCRUDTeam:
    """Test cases for CRUDTeam class."""

    @pytest.mark.asyncio
    async def test_create_team_success(self, db_session: AsyncSession, test_user: User):
        """Test creating a team with valid data."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create test data
        team_in = TeamCreate(
            name=TEST_TEAM_NAME,
            description=TEST_DESCRIPTION,
            game_mode=TEST_GAME_MODE,
            max_members=TEST_MAX_MEMBERS,
            status=TeamStatus.ACTIVE,
        )
        
        # Create a real instance of CRUDTeam for testing
        crud = CRUDTeam(Team)
        
        # Mock the session's execute method to return our test user for the owner
        async def mock_execute(stmt):
            if hasattr(stmt, 'scalars'):
                mock_result = MagicMock()
                mock_result.scalars.return_value.first.return_value = test_user
                return mock_result
            return MagicMock()
        
        mock_db.execute.side_effect = mock_execute
        
        # Create the team
        team = await crud.create_with_owner(
            mock_db, 
            obj_in=team_in, 
            owner_id=test_user.id
        )
        
        # Verify the result
        assert team is not None
        assert team.name == TEST_TEAM_NAME
        assert team.description == TEST_DESCRIPTION
        assert team.game_mode == TEST_GAME_MODE
        assert team.max_members == TEST_MAX_MEMBERS
        assert team.status == TeamStatus.ACTIVE
        assert team.created_by_id == test_user.id
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_team(self, db_session: AsyncSession, mock_team: Team):
        """Test getting a team by ID."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_team
        mock_db.execute.return_value = mock_result
        
        # Get the team
        crud = CRUDTeam(Team)
        team = await crud.get(mock_db, id=TEST_TEAM_ID)
        
        # Verify the result
        assert team is not None
        assert team.id == TEST_TEAM_ID
        assert team.name == TEST_TEAM_NAME
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("SELECT") >= 0
        assert str(query).find("WHERE") > 0
        assert str(query).find("team.id") > 0

    @pytest.mark.asyncio
    async def test_get_teams_by_owner(self, db_session: AsyncSession, test_user: User):
        """Test getting teams by owner ID."""
        # Mock teams
        mock_teams = [
            Team(
                id=i,
                name=f"Team {i}",
                game_mode=TEST_GAME_MODE,
                max_members=5,
                created_by_id=test_user.id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ) for i in range(1, 4)
        ]
        
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_teams
        mock_db.execute.return_value = mock_result
        
        # Get teams by owner
        crud = CRUDTeam(Team)
        teams = await crud.get_multi_by_owner(
            mock_db, 
            owner_id=test_user.id,
            skip=0,
            limit=10
        )
        
        # Verify the result
        assert len(teams) == 3
        assert all(team.created_by_id == test_user.id for team in teams)
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("WHERE team.created_by_id") > 0

    @pytest.mark.asyncio
    async def test_update_team(self, db_session: AsyncSession, mock_team: Team):
        """Test updating a team."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Update data
        update_data = TeamUpdate(
            name="Updated Team",
            description="Updated Description",
            game_mode="pvp",
            max_members=15,
            status=TeamStatus.INACTIVE,
        )
        
        # Mock the query result for getting the team
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_team
        mock_db.execute.return_value = mock_result
        
        # Perform the update
        crud = CRUDTeam(Team)
        updated_team = await crud.update(
            mock_db, 
            db_obj=mock_team, 
            obj_in=update_data
        )
        
        # Verify the result
        assert updated_team is not None
        assert updated_team.name == "Updated Team"
        assert updated_team.description == "Updated Description"
        assert updated_team.game_mode == "pvp"
        assert updated_team.max_members == 15
        assert updated_team.status == TeamStatus.INACTIVE
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_team(self, db_session: AsyncSession, mock_team: Team):
        """Test removing a team."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result for getting the team
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_team
        mock_db.execute.return_value = mock_result
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Delete the team
        crud = CRUDTeam(Team)
        deleted = await crud.remove(mock_db, id=TEST_TEAM_ID)
        
        # Verify the result
        assert deleted == 1  # Number of rows affected
        
        # Verify the database interactions
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()
        
        # Verify the delete query was built correctly
        delete_call = None
        for call in mock_db.execute.call_args_list:
            if 'DELETE' in str(call[0][0]):
                delete_call = call
                break
                
        assert delete_call is not None
        assert 'DELETE FROM team' in str(delete_call[0][0])
        assert 'WHERE team.id' in str(delete_call[0][0])

    @pytest.mark.asyncio
    async def test_add_member_to_team(self, db_session: AsyncSession, mock_team: Team, mock_user: User):
        """Test adding a member to a team."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create test member data
        member_data = TeamMemberCreate(
            user_id=mock_user.id,
            role=TeamRole.MEMBER,
            profession_id=TEST_PROFESSION_ID,
            is_commander=False,
            is_secondary_commander=False,
        )
        
        # Mock the query result for getting the user
        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_user_result
        
        # Add the member to the team
        crud = CRUDTeam(Team)
        team = await crud.add_member(
            mock_db, 
            team=mock_team, 
            member_data=member_data
        )
        
        # Verify the result
        assert team is not None
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_from_team(self, db_session: AsyncSession, mock_team: Team, mock_user: User):
        """Test removing a member from a team."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Remove the member from the team
        crud = CRUDTeam(Team)
        result = await crud.remove_member(
            mock_db, 
            team_id=TEST_TEAM_ID, 
            user_id=mock_user.id
        )
        
        # Verify the result
        assert result is True
        
        # Verify the database interactions
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()
        
        # Verify the delete query was built correctly
        delete_call = None
        for call in mock_db.execute.call_args_list:
            if 'DELETE' in str(call[0][0]):
                delete_call = call
                break
                
        assert delete_call is not None
        assert 'DELETE FROM team_members' in str(delete_call[0][0])
        assert 'WHERE team_members.team_id' in str(delete_call[0][0])
        assert 'AND team_members.user_id' in str(delete_call[0][0])

# Test the team instance
class TestTeamInstance:
    """Test cases for the team instance."""
    
    @pytest.mark.asyncio
    async def test_team_instance_creation(self):
        """Test that the team instance is created correctly."""
        from app.crud.crud_team import team
        assert isinstance(team, CRUDTeam)
        assert team.model == Team

    @pytest.mark.asyncio
    async def test_team_instance_methods(self):
        """Test that the team instance has the expected methods."""
        from app.crud.crud_team import team
        assert hasattr(team, "create_with_owner")
        assert hasattr(team, "get_multi_by_owner")
        assert hasattr(team, "add_member")
        assert hasattr(team, "remove_member")
        assert hasattr(team, "add_composition")
        assert hasattr(team, "remove_composition")
