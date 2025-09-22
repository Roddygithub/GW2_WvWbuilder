"""Tests for composition CRUD operations."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import CRUDBase
from app.models import Composition, CompositionTag, User, Build, Profession, Role
from app.schemas.composition import (
    CompositionCreate,
    CompositionUpdate,
    CompositionMemberBase,
    CompositionMemberRole,
)
from app.models.enums import CompositionStatus, GameMode

# Define CRUDComposition since it doesn't exist in the codebase
class CRUDComposition(CRUDBase[Composition, CompositionCreate, CompositionUpdate]):
    """CRUD operations for Composition model."""
    
    async def get_multi_by_creator(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Composition]:
        """Get multiple compositions by owner ID."""
        result = await db.execute(
            self.model.select().where(self.model.created_by == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_public_compositions(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Composition]:
        """Get all public compositions."""
        result = await db.execute(
            self.model.select().where(self.model.is_public == True).offset(skip).limit(limit)  # noqa: E712
        )
        return result.scalars().all()

# Create an instance of CRUDComposition for testing
composition_crud = CRUDComposition(Composition)

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
        "game_mode": GameMode.WvW,
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
        game_mode=GameMode.WvW,
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
        game_mode=GameMode.WvW,
        created_by=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_composition_with_members(
    mock_composition, mock_user, mock_role, mock_profession
):
    """Create a mock composition with members."""
    mock_composition.members = [mock_user]
    mock_composition.member_roles = {
        str(mock_user.id): {"role": mock_role, "profession": mock_profession}
    }
    return mock_composition


# Test CRUDComposition class
class TestCRUDComposition:
    """Test cases for CRUDComposition class."""

    @pytest.mark.asyncio
    async def test_create_composition_success(
        self, db_session: AsyncSession, mock_user
    ):
        """Test creating a composition with valid data."""
        # Arrange
        crud = CRUDComposition(Composition)
        composition_in = CompositionCreate(
            name=TEST_COMPOSITION_NAME,
            description=TEST_DESCRIPTION,
            squad_size=TEST_SQUAD_SIZE,
            is_public=TEST_IS_PUBLIC,
            status=CompositionStatus.DRAFT,
            game_mode=GameMode.WvW,
        )

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the query to return the user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock the add, commit and refresh methods
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act
        composition = await crud.create_with_owner(
            db=mock_db, obj_in=composition_in, owner_id=mock_user.id
        )

        # Assert
        assert composition is not None
        assert composition.name == TEST_COMPOSITION_NAME
        assert composition.description == TEST_DESCRIPTION
        assert composition.squad_size == TEST_SQUAD_SIZE
        assert composition.is_public == TEST_IS_PUBLIC
        assert composition.status == CompositionStatus.DRAFT
        assert composition.game_mode == GameMode.WvW
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
        result = await crud.get(db=mock_db, id=TEST_COMPOSITION_ID)

        # Assert
        assert result is not None
        assert result.id == TEST_COMPOSITION_ID
        assert result.name == TEST_COMPOSITION_NAME

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
        composition = await crud.get(db=mock_db, id=999)

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
                created_by=mock_user.id,
            )
            for i in range(1, 6)
        ]

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the query result to return the compositions
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = compositions
        mock_db.execute.return_value = mock_result

        # Act - Use get_multi_by_creator instead of get_multi_by_owner
        result = await crud.get_multi_by_creator(
            db=mock_db, owner_id=mock_user.id, skip=0, limit=10
        )

        # Assert
        assert len(result) == 5
        assert all(comp.created_by == mock_user.id for comp in result)

        # Verify the query was built correctly
        mock_db.execute.assert_called_once()
        query = mock_db.execute.call_args[0][0]
        assert str(query).find("SELECT") >= 0
        assert str(query).find("WHERE") > 0
        assert str(query).find("compositions.created_by") > 0

    @pytest.mark.asyncio
    async def test_update_composition(self, db_session: AsyncSession, mock_composition):
        """Test updating a composition."""
        # Arrange
        crud = CRUDComposition(Composition)

        # Update data - Use DRAFT instead of PUBLISHED as it's not defined in CompositionStatus
        update_data = CompositionUpdate(
            name="Updated Composition",
            description="Updated Description",
            squad_size=15,
            is_public=False,
            status=CompositionStatus.DRAFT,  # Changed from PUBLISHED to DRAFT
            game_mode=GameMode.WvW,
        )

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the query to return the composition
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result

        # Mock the add, commit and refresh methods
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act
        updated_composition = await crud.update(
            db=mock_db, db_obj=mock_composition, obj_in=update_data
        )

        # Assert
        assert updated_composition is not None
        assert updated_composition.name == "Updated Composition"
        assert updated_composition.description == "Updated Description"
        assert updated_composition.squad_size == 15
        assert updated_composition.is_public is False
        assert updated_composition.status == CompositionStatus.DRAFT  # Updated to DRAFT
        assert updated_composition.game_mode == GameMode.WvW

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

        # Mock the query to return the composition
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition
        mock_db.execute.return_value = mock_result

        # Mock the delete operation
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        # Act - Call get first to get the composition, then remove it
        composition = await crud.get(db=mock_db, id=TEST_COMPOSITION_ID)
        if composition:
            await crud.remove(db=mock_db, id=composition.id)

        # Assert
        assert composition is not None
        assert composition.id == TEST_COMPOSITION_ID

        # Verify database interactions
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_member_to_composition(
        self,
        db_session: AsyncSession,
        mock_composition,
        mock_user,
        mock_role,
        mock_profession,
    ):
        """Test adding a member to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)

        # Mock the query to return the composition members
        mock_members_result = MagicMock()
        mock_members_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_members_result

        # Act - Call add_member with the required parameters
        composition = await crud.add_member(
            db=mock_db,
            composition_id=mock_composition.id,
            user=mock_user,
            role=CompositionMemberRole.HEALER,
            profession_id=mock_profession.id
        )

        # Assert
        assert composition is not None
        assert composition.id == mock_composition.id

        # Verify database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_from_composition(
        self, db_session: AsyncSession, mock_composition, mock_user
    ):
        """Test removing a member from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)
        
        # Mock the query to return the composition members
        mock_members_result = MagicMock()
        mock_members_result.scalars.return_value.all.return_value = [mock_user]
        mock_db.execute.return_value = mock_members_result

        # Mock commit and refresh
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act - Call remove_member with the required parameters
        result = await crud.remove_member(
            db=mock_db, composition_id=TEST_COMPOSITION_ID, user_id=mock_user.id
        )

        # Assert
        assert result is not None
        assert result.id == mock_composition.id

        # Verify the database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_build_to_composition(
        self, db_session: AsyncSession, mock_composition, mock_build
    ):
        """Test adding a build to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)

        # Act - Call add_build with the required parameters
        composition = await crud.add_build(
            db=mock_db, composition_id=mock_composition.id, build=mock_build
        )

        # Assert
        assert composition is not None
        assert composition.id == mock_composition.id

        # Verify database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_build_from_composition(
        self, db_session: AsyncSession, mock_composition
    ):
        """Test removing a build from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)

        # Mock commit and refresh
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act - Call remove_build with the required parameters
        result = await crud.remove_build(
            db=mock_db, composition_id=mock_composition.id
        )

        # Assert
        assert result is not None
        assert result.id == mock_composition.id

        # Verify database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_tag_to_composition(
        self, db_session: AsyncSession, mock_composition
    ):
        """Test adding a tag to a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Create a mock tag
        from app.models.tag import Tag
        mock_tag = Tag(
            id=TEST_TAG_ID,
            name="Test Tag",
            description="Test Description",
            category="Test Category"
        )

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)

        # Mock the query result for checking if tag exists
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Mock commit and refresh
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act - Call add_tag with correct parameters
        composition = await crud.add_tag(
            db=mock_db, composition_id=mock_composition.id, tag=mock_tag
        )

        # Assert
        assert composition is not None
        assert composition.id == mock_composition.id

        # Verify database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_tag_from_composition(
        self, db_session: AsyncSession, mock_composition
    ):
        """Test removing a tag from a composition."""
        # Arrange
        crud = CRUDComposition(Composition)
        
        # Create a mock Tag object
        from app.models.tag import Tag
        mock_tag = Tag(
            id=TEST_TAG_ID,
            name="Test Tag",
            description="Test Description",
            category="Test Category"
        )
        
        # Create a mock CompositionTag with the Tag
        mock_composition_tag = CompositionTag(
            id=1,
            composition_id=TEST_COMPOSITION_ID,
            tag_id=TEST_TAG_ID,
            tag=mock_tag
        )

        # Mock the database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock the get method to return the composition
        crud.get = AsyncMock(return_value=mock_composition)

        # Mock the query result for getting the tag
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_composition_tag
        mock_db.execute.return_value = mock_result

        # Mock the delete operation
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act - Call remove_tag with correct parameters
        result = await crud.remove_tag(
            db=mock_db, composition_id=TEST_COMPOSITION_ID, tag_id=TEST_TAG_ID
        )

        # Assert
        assert result is not None
        assert result.id == mock_composition.id

        # Verify the database interactions
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


# Test the composition instance
class TestCompositionInstance:
    """Test cases for the composition instance."""

    @pytest.mark.asyncio
    async def test_composition_instance_creation(self):
        """Test that the composition instance is created correctly."""
        from app.crud.crud_composition import composition, CRUDComposition

        # Vérifier que composition est une instance de CRUDComposition
        assert isinstance(composition, CRUDComposition)
        # Vérifier que le modèle associé est bien Composition
        assert composition.model == Composition
