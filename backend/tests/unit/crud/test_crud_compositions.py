"""Tests for composition CRUD operations."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock, call
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy import select, and_

from app.crud.crud_composition import composition as crud_composition, CRUDComposition
from app.models import Composition, User, Build, CompositionTag, Profession, Role, composition_members
from app.schemas.composition import (
    CompositionCreate, 
    CompositionUpdate, 
    CompositionMemberCreate,
    CompositionStatus,
    GameMode,
    CompositionMemberRole
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException,
    UnauthorizedException
)

# Test data
TEST_COMPOSITION_NAME = "Test Composition"
TEST_DESCRIPTION = "Test Composition Description"
TEST_SQUAD_SIZE = 10
TEST_IS_PUBLIC = True
TEST_COMPOSITION_ID = 1
TEST_USER_ID = 1
TEST_USER2_ID = 2
TEST_BUILD_ID = 1
TEST_TAG_ID = 1
TEST_PROFESSION_ID = 1
TEST_ROLE_ID = 1
TEST_NOTE = "Test note"

# Fixtures
@pytest.fixture
def composition_data():
    """Return test composition data."""
    return {
        "name": TEST_COMPOSITION_NAME,
        "description": TEST_DESCRIPTION,
        "squad_size": TEST_SQUAD_SIZE,
        "is_public": TEST_IS_PUBLIC,
        "status": CompositionStatus.DRAFT,
        "game_mode": GameMode.WVW,
    }

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    return User(
        id=TEST_USER_ID,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )

@pytest.fixture
def mock_build():
    """Create a mock build object."""
    return Build(
        id=TEST_BUILD_ID,
        name="Test Build",
        description="Test Build Description",
        game_mode=GameMode.WVW,
        team_size=5,
        is_public=True,
        created_by_id=TEST_USER_ID,
    )

@pytest.fixture
def mock_role():
    """Create a mock role object."""
    return Role(
        id=TEST_ROLE_ID,
        name="Commander",
        description="Team Commander",
        permission_level=100,
    )

@pytest.fixture
def mock_profession():
    """Create a mock profession object."""
    return Profession(
        id=TEST_PROFESSION_ID,
        name="Guardian",
        icon_url="guardian.png",
    )

@pytest.fixture
def mock_composition():
    """Create a mock composition object."""
    return Composition(
        id=TEST_COMPOSITION_ID,
        name=TEST_COMPOSITION_NAME,
        description=TEST_DESCRIPTION,
        squad_size=TEST_SQUAD_SIZE,
        is_public=TEST_IS_PUBLIC,
        status=CompositionStatus.DRAFT,
        game_mode=GameMode.WVW,
        created_by=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_composition_with_members(mock_composition, mock_user, mock_role, mock_profession):
    """Create a mock composition with members."""
    mock_composition.members = [mock_user]
    mock_composition.member_roles = {str(mock_user.id): {"role": mock_role, "profession": mock_profession}}
    return mock_composition

# Test CRUDComposition class
class TestCRUDComposition:
    """Test cases for CRUDComposition class."""

    @pytest.mark.asyncio
    async def test_create_composition_success(self, db_session: AsyncSession, mock_user):
        """Test creating a composition with valid data."""
        # Arrange
        crud = CRUDComposition(Composition)
        composition_in = CompositionCreate(
            name=TEST_COMPOSITION_NAME,
            description=TEST_DESCRIPTION,
            squad_size=TEST_SQUAD_SIZE,
            is_public=TEST_IS_PUBLIC,
            status=CompositionStatus.DRAFT,
            game_mode=GameMode.WVW,
        )
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query to return the user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        # Act
        composition = await crud.create_with_owner(
            mock_db, 
            obj_in=composition_in, 
            owner_id=mock_user.id
        )
        
        # Assert
        assert composition is not None
        assert composition.name == TEST_COMPOSITION_NAME
        assert composition.description == TEST_DESCRIPTION
        assert composition.squad_size == TEST_SQUAD_SIZE
        assert composition.is_public == TEST_IS_PUBLIC
        assert composition.status == CompositionStatus.DRAFT
        assert composition.game_mode == GameMode.WVW
        assert composition.created_by == mock_user.id
        
        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_composition(self, db_session: AsyncSession, mock_composition):
        """Test retrieving a composition by ID."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result
        
        # Act
        composition = await crud.get(mock_db, id=TEST_COMPOSITION_ID)
        
        # Assert
        assert composition is not None
        assert composition.id == TEST_COMPOSITION_ID
        assert composition.name == TEST_COMPOSITION_NAME
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("SELECT") >= 0
        assert str(query).find("WHERE") > 0
        assert str(query).find("compositions.id") > 0

    @pytest.mark.asyncio
    async def test_get_composition_not_found(self, db_session: AsyncSession):
        """Test retrieving a non-existent composition returns None."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result to return None
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        composition = await crud.get(mock_db, id=999)
        
        # Assert
        assert composition is None

    @pytest.mark.asyncio
    async def test_get_multi_by_owner(self, db_session: AsyncSession, mock_user):
        """Test retrieving multiple compositions by owner."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Create test compositions
        compositions = [
            Composition(
                id=i,
                name=f"Composition {i}",
                description=f"Description {i}",
                squad_size=5,
                is_public=True,
                status=CompositionStatus.DRAFT,
                game_mode=GameMode.WVW,
                created_by=mock_user.id,
            ) for i in range(1, 6)
        ]
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = compositions
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await crud.get_multi_by_owner(
            mock_db, 
            owner_id=mock_user.id,
            skip=0,
            limit=10
        )
        
        # Assert
        assert len(result) == 5
        assert all(comp.created_by == mock_user.id for comp in result)
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("WHERE compositions.created_by") > 0

    @pytest.mark.asyncio
    async def test_update_composition(self, db_session: AsyncSession, mock_composition):
        """Test updating a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Update data
        update_data = CompositionUpdate(
            name="Updated Composition",
            description="Updated Description",
            squad_size=15,
            is_public=False,
            status=CompositionStatus.PUBLISHED,
            game_mode=GameMode.PVP,
        )
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act
        updated_composition = await crud.update(
            mock_db, 
            db_obj=mock_composition, 
            obj_in=update_data
        )
        
        # Assert
        assert updated_composition is not None
        assert updated_composition.name == "Updated Composition"
        assert updated_composition.description == "Updated Description"
        assert updated_composition.squad_size == 15
        assert updated_composition.is_public is False
        assert updated_composition.status == CompositionStatus.PUBLISHED
        assert updated_composition.game_mode == GameMode.PVP
        
        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_composition(self, db_session: AsyncSession, mock_composition):
        """Test removing a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result for getting the composition
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Act
        deleted = await crud.remove(mock_db, id=TEST_COMPOSITION_ID)
        
        # Assert
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
        assert 'DELETE FROM compositions' in str(delete_call[0][0])
        assert 'WHERE compositions.id' in str(delete_call[0][0])

    @pytest.mark.asyncio
    async def test_add_member_to_composition(self, db_session: AsyncSession, mock_composition, mock_user, mock_role, mock_profession):
        """Test adding a member to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Create test member data
        member_data = CompositionMemberCreate(
            user_id=mock_user.id,
            role=CompositionMemberRole.COMMANDER,
            profession_id=mock_profession.id,
            note=TEST_NOTE,
        )
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query results
        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = mock_user
        
        mock_role_result = MagicMock()
        mock_role_result.scalars.return_value.first.return_value = mock_role
        
        mock_profession_result = MagicMock()
        mock_profession_result.scalars.return_value.first.return_value = mock_profession
        
        mock_db.execute.side_effect = [
            mock_user_result,
            mock_role_result,
            mock_profession_result,
            MagicMock(),  # For the insert statement
        ]
        
        # Act
        composition = await crud.add_member(
            mock_db, 
            composition=mock_composition, 
            member_data=member_data
        )
        
        # Assert
        assert composition is not None
        
        # Verify database interactions
        assert mock_db.execute.call_count >= 3  # At least 3 queries: get user, get role, get profession
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_from_composition(self, db_session: AsyncSession, mock_composition, mock_user):
        """Test removing a member from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Act
        result = await crud.remove_member(
            mock_db, 
            composition_id=TEST_COMPOSITION_ID, 
            user_id=mock_user.id
        )
        
        # Assert
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
        assert 'DELETE FROM composition_members' in str(delete_call[0][0])
        assert 'WHERE composition_members.composition_id' in str(delete_call[0][0])
        assert 'AND composition_members.user_id' in str(delete_call[0][0])

    @pytest.mark.asyncio
    async def test_add_build_to_composition(self, db_session: AsyncSession, mock_composition, mock_build):
        """Test adding a build to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result for getting the build
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_build
        mock_db.execute.return_value = mock_result
        
        # Act
        composition = await crud.add_build(
            mock_db, 
            composition=mock_composition, 
            build_id=mock_build.id
        )
        
        # Assert
        assert composition is not None
        assert composition.build_id == mock_build.id
        
        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_build_from_composition(self, db_session: AsyncSession, mock_composition):
        """Test removing a build from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Set a build ID on the composition
        mock_composition.build_id = TEST_BUILD_ID
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act
        composition = await crud.remove_build(
            mock_db, 
            composition=mock_composition
        )
        
        # Assert
        assert composition is not None
        assert composition.build_id is None
        
        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_tag_to_composition(self, db_session: AsyncSession, mock_composition):
        """Test adding a tag to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        tag_name = "Test Tag"
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result for checking if tag exists
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        composition = await crud.add_tag(
            mock_db, 
            composition=mock_composition, 
            tag_name=tag_name
        )
        
        # Assert
        assert composition is not None
        
        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_tag_from_composition(self, db_session: AsyncSession, mock_composition):
        """Test removing a tag from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        tag_name = "Test Tag"
        
        # Create a mock tag
        mock_tag = CompositionTag(
            id=TEST_TAG_ID,
            name=tag_name,
            composition_id=TEST_COMPOSITION_ID,
        )
        
        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock the query result for getting the tag
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_tag
        mock_db.execute.return_value = mock_result
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Act
        result = await crud.remove_tag(
            mock_db, 
            composition_id=TEST_COMPOSITION_ID, 
            tag_name=tag_name
        )
        
        # Assert
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
        assert 'DELETE FROM composition_tags' in str(delete_call[0][0])
        assert 'WHERE composition_tags.composition_id' in str(delete_call[0][0])
        assert 'AND composition_tags.name' in str(delete_call[0][0])

# Test the composition instance
class TestCompositionInstance:
    """Test cases for the composition instance."""
    
    @pytest.mark.asyncio
    async def test_composition_instance_creation(self):
        """Test that the composition instance is created correctly."""
        from app.crud.crud_composition import composition
        assert isinstance(composition, CRUDComposition)
        assert composition.model == Composition
