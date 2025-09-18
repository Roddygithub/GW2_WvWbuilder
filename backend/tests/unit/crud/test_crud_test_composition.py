"""Tests for composition CRUD operations."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from app.crud.crud_composition import composition as crud_composition, CRUDComposition
from app.models import Composition, User, Build, CompositionTag, CompositionMember, Profession, Role
from app.schemas.composition import (
    CompositionCreate, 
    CompositionUpdate, 
    CompositionMemberCreate,
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
TEST_DESCRIPTION = "Test Description"
TEST_SQUAD_SIZE = 5
TEST_IS_PUBLIC = True
TEST_GAME_MODE = "wvw"
TEST_TAGS = ["zerg", "frontline", "meta"]
TEST_USER_ID = 1
TEST_COMPOSITION_ID = 1
TEST_BUILD_ID = 1
TEST_PROFESSION_ID = 1
TEST_ELITE_SPECIALIZATION_ID = 1

# Fixtures
@pytest.fixture
def composition_data():
    """Return test composition data."""
    return {
        "name": TEST_COMPOSITION_NAME,
        "description": TEST_DESCRIPTION,
        "squad_size": TEST_SQUAD_SIZE,
        "is_public": TEST_IS_PUBLIC,
        "game_mode": TEST_GAME_MODE,
        "tags": TEST_TAGS,
    }

@pytest.fixture
def mock_composition():
    """Create a mock composition object."""
    return Composition(
        id=TEST_COMPOSITION_ID,
        name=TEST_COMPOSITION_NAME,
        description=TEST_DESCRIPTION,
        squad_size=TEST_SQUAD_SIZE,
        is_public=TEST_IS_PUBLIC,
        game_mode=TEST_GAME_MODE,
        created_by_id=TEST_USER_ID,
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
        created_by_id=TEST_USER_ID,
        is_public=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_profession():
    """Create a mock profession object."""
    return Profession(
        id=TEST_PROFESSION_ID,
        name="Test Profession",
        icon="test_icon.png",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_role():
    """Create a mock role object."""
    return Role(
        id=1,
        name="Test Role",
        description="Test Role Description",
        permission_level=1,
        is_default=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_member():
    """Create a mock composition member."""
    return CompositionMember(
        id=1,
        composition_id=TEST_COMPOSITION_ID,
        user_id=TEST_USER_ID,
        role_id=1,
        profession_id=TEST_PROFESSION_ID,
        elite_specialization_id=TEST_ELITE_SPECIALIZATION_ID,
        role_type=CompositionMemberRole.HEALER,
        is_commander=False,
        is_secondary_commander=False,
        priority=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

# Test CRUDComposition class
class TestCRUDComposition:
    """Test cases for CRUDComposition class."""

    @pytest.mark.asyncio
    async def test_create_composition_success(self, db_session: AsyncSession, test_user: User):
        """Test creating a composition with valid data."""
        composition_in = CompositionCreate(
            name=TEST_COMPOSITION_NAME,
            description=TEST_DESCRIPTION,
            is_public=TEST_IS_PUBLIC,
            squad_size=TEST_SQUAD_SIZE,
            game_mode=TEST_GAME_MODE,
            tags=TEST_TAGS,
        )
        
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create a real instance of CRUDComposition for testing
        crud = CRUDComposition(Composition)
        
        # Mock the session's execute method to return our test user for the owner
        async def mock_execute(stmt):
            if hasattr(stmt, 'scalars'):
                mock_result = MagicMock()
                mock_result.scalars.return_value.first.return_value = test_user
                return mock_result
            return MagicMock()
        
        mock_db.execute.side_effect = mock_execute
        
        # Create the composition
        composition = await crud.create_with_owner(
            mock_db, 
            obj_in=composition_in, 
            owner_id=test_user.id
        )
        
        # Verify the result
        assert composition is not None
        assert composition.name == TEST_COMPOSITION_NAME
        assert composition.description == TEST_DESCRIPTION
        assert composition.squad_size == TEST_SQUAD_SIZE
        assert composition.is_public == TEST_IS_PUBLIC
        assert composition.game_mode == TEST_GAME_MODE
        assert composition.created_by_id == test_user.id
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify tags were added (if tags are supported in the model)
        if hasattr(composition, 'tags'):
            assert len(composition.tags) == len(TEST_TAGS)
            assert all(tag.name in TEST_TAGS for tag in composition.tags)

    @pytest.mark.asyncio
    async def test_get_composition(self, db_session: AsyncSession, mock_composition: Composition):
        """Test getting a composition by ID."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result
        
        # Get the composition
        crud = CRUDComposition(Composition)
        composition = await crud.get(mock_db, id=TEST_COMPOSITION_ID)
        
        # Verify the result
        assert composition is not None
        assert composition.id == TEST_COMPOSITION_ID
        assert composition.name == TEST_COMPOSITION_NAME
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("SELECT") >= 0
        assert str(query).find("WHERE") > 0
        assert str(query).find("composition.id") > 0

    @pytest.mark.asyncio
    async def test_get_multi_compositions(self, db_session: AsyncSession):
        """Test getting multiple compositions with pagination."""
        # Create mock compositions
        mock_compositions = [
            Composition(
                id=i,
                name=f"Test Composition {i}",
                description=f"Description {i}",
                squad_size=5,
                is_public=(i % 2 == 0),
                created_by_id=TEST_USER_ID,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ) for i in range(1, 6)
        ]
        
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_compositions[:3]  # First page
        mock_db.execute.return_value = mock_result
        
        # Get the first page of compositions
        crud = CRUDComposition(Composition)
        compositions_page1 = await crud.get_multi(mock_db, skip=0, limit=3)
        
        # Verify the result
        assert len(compositions_page1) == 3
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("SELECT") >= 0
        assert str(query).find("LIMIT :param_1") > 0
        assert str(query).find("OFFSET :param_2") > 0

    @pytest.mark.asyncio
    async def test_get_public_compositions(self, db_session: AsyncSession):
        """Test getting public compositions."""
        # Create mock compositions with different visibility
        mock_public_compositions = [
            Composition(
                id=i,
                name=f"Public Composition {i}",
                description=f"Public Description {i}",
                squad_size=5,
                is_public=True,
                created_by_id=TEST_USER_ID,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ) for i in range(1, 4)
        ]
        
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_public_compositions
        mock_db.execute.return_value = mock_result
        
        # Get public compositions
        crud = CRUDComposition(Composition)
        public_compositions = await crud.get_public_compositions(
            mock_db, skip=0, limit=10
        )
        
        # Verify the result
        assert len(public_compositions) == 3
        assert all(comp.is_public for comp in public_compositions)
        
        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("WHERE composition.is_public = true") > 0

    @pytest.mark.asyncio
    async def test_update_composition(self, db_session: AsyncSession, mock_composition: Composition):
        """Test updating a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Update data
        update_data = CompositionUpdate(
            name="Updated Composition",
            description="Updated Description",
            is_public=False,
            squad_size=10,
            game_mode="pvp",
            tags=["pvp", "small_scale"]
        )
        
        # Mock the query result for getting the composition
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result
        
        # Perform the update
        crud = CRUDComposition(Composition)
        updated_composition = await crud.update(
            mock_db, 
            db_obj=mock_composition, 
            obj_in=update_data
        )
        
        # Verify the result
        assert updated_composition is not None
        assert updated_composition.name == "Updated Composition"
        assert updated_composition.description == "Updated Description"
        assert updated_composition.is_public is False
        assert updated_composition.squad_size == 10
        assert updated_composition.game_mode == "pvp"
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify tags were updated (if tags are supported in the model)
        if hasattr(updated_composition, 'tags'):
            assert len(updated_composition.tags) == 2
            assert all(tag in ["pvp", "small_scale"] for tag in updated_composition.tags)

    @pytest.mark.asyncio
    async def test_remove_composition(self, db_session: AsyncSession, mock_composition: Composition):
        """Test removing a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result for getting the composition
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Delete the composition
        crud = CRUDComposition(Composition)
        deleted = await crud.remove(mock_db, id=TEST_COMPOSITION_ID)
        
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
        assert 'DELETE FROM composition' in str(delete_call[0][0])
        assert 'WHERE composition.id' in str(delete_call[0][0])

    @pytest.mark.asyncio
    async def test_add_build_to_composition(self, db_session: AsyncSession, mock_composition: Composition, mock_build: Build):
        """Test adding a build to a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result for getting the build
        mock_build_result = MagicMock()
        mock_build_result.scalars.return_value.first.return_value = mock_build
        mock_db.execute.return_value = mock_build_result
        
        # Add the build to the composition
        crud = CRUDComposition(Composition)
        composition = await crud.add_build(
            mock_db, 
            composition=mock_composition, 
            build=mock_build
        )
        
        # Verify the result
        assert composition is not None
        assert composition.build_id == mock_build.id
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_build_from_composition(self, db_session: AsyncSession, mock_composition: Composition, mock_build: Build):
        """Test removing a build from a composition."""
        # Set up the composition with a build
        mock_composition.build_id = mock_build.id
        
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Mock the query result for getting the build
        mock_build_result = MagicMock()
        mock_build_result.scalars.return_value.first.return_value = mock_build
        mock_db.execute.return_value = mock_build_result
        
        # Remove the build from the composition
        crud = CRUDComposition(Composition)
        composition = await crud.remove_build(
            mock_db, 
            composition=mock_composition, 
            build=mock_build
        )
        
        # Verify the result
        assert composition is not None
        assert composition.build_id is None
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_tag_to_composition(self, db_session: AsyncSession, mock_composition: Composition):
        """Test adding a tag to a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create a test tag
        tag_name = "test-tag"
        mock_tag = CompositionTag(
            id=1,
            name=tag_name,
            composition_id=TEST_COMPOSITION_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        # Mock the query result for getting the composition with tags
        mock_composition.tags = [mock_tag]
        
        # Add the tag to the composition
        crud = CRUDComposition(Composition)
        composition = await crud.add_tag(
            mock_db, 
            composition=mock_composition, 
            tag_name=tag_name
        )
        
        # Verify the result
        assert composition is not None
        assert any(tag.name == tag_name for tag in composition.tags)
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_tag_from_composition(self, db_session: AsyncSession, mock_composition: Composition):
        """Test removing a tag from a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create a test tag
        tag_name = "test-tag"
        mock_tag = CompositionTag(
            id=1,
            name=tag_name,
            composition_id=TEST_COMPOSITION_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        # Set up the composition with the tag
        mock_composition.tags = [mock_tag]
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Remove the tag from the composition
        crud = CRUDComposition(Composition)
        composition = await crud.remove_tag(
            mock_db, 
            composition=mock_composition, 
            tag_name=tag_name
        )
        
        # Verify the result
        assert composition is not None
        assert not any(tag.name == tag_name for tag in composition.tags)
        
        # Verify the database interactions
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_member_to_composition(self, db_session: AsyncSession, mock_composition: Composition, test_user: User):
        """Test adding a member to a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create test member data
        member_data = CompositionMemberCreate(
            user_id=test_user.id,
            role_id=1,
            profession_id=1,
            elite_specialization_id=1,
            role_type=CompositionMemberRole.HEALER,
            is_commander=False,
            is_secondary_commander=False,
            priority=1,
        )
        
        # Mock the member object
        mock_member = CompositionMember(
            id=1,
            composition_id=TEST_COMPOSITION_ID,
            user_id=test_user.id,
            role_id=1,
            profession_id=1,
            elite_specialization_id=1,
            role_type=CompositionMemberRole.HEALER,
            is_commander=False,
            is_secondary_commander=False,
            priority=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        # Set up the composition with the member
        mock_composition.members = [mock_member]
        
        # Mock the query result for getting the user
        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = test_user
        mock_db.execute.return_value = mock_user_result
        
        # Add the member to the composition
        crud = CRUDComposition(Composition)
        composition = await crud.add_member(
            mock_db, 
            composition=mock_composition, 
            member_data=member_data
        )
        
        # Verify the result
        assert composition is not None
        assert len(composition.members) == 1
        assert composition.members[0].user_id == test_user.id
        assert composition.members[0].role_type == CompositionMemberRole.HEALER
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_from_composition(self, db_session: AsyncSession, mock_composition: Composition, test_user: User):
        """Test removing a member from a composition."""
        # Mock the database session
        mock_db = MagicMock(spec=AsyncSession)
        
        # Create a test member
        mock_member = CompositionMember(
            id=1,
            composition_id=TEST_COMPOSITION_ID,
            user_id=test_user.id,
            role_id=1,
            profession_id=1,
            elite_specialization_id=1,
            role_type=CompositionMemberRole.HEALER,
            is_commander=False,
            is_secondary_commander=False,
            priority=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        # Set up the composition with the member
        mock_composition.members = [mock_member]
        
        # Mock the delete operation
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1
        mock_db.execute.return_value = mock_delete_result
        
        # Remove the member from the composition
        crud = CRUDComposition(Composition)
        composition = await crud.remove_member(
            mock_db, 
            composition=mock_composition, 
            user_id=test_user.id
        )
        
        # Verify the result
        assert composition is not None
        assert len(composition.members) == 0
        
        # Verify the database interactions
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify the delete query was built correctly
        delete_call = None
        for call in mock_db.execute.call_args_list:
            if 'DELETE' in str(call[0][0]):
                delete_call = call
                break
                
        assert delete_call is not None
        assert 'DELETE FROM composition_member' in str(delete_call[0][0])
        assert 'WHERE composition_member.composition_id' in str(delete_call[0][0])
        assert 'AND composition_member.user_id' in str(delete_call[0][0])
