import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.composition import CRUDComposition
from app.models import Composition, User, Build, CompositionMember
from app.schemas.composition import CompositionCreate, CompositionUpdate

# Create an instance of CRUDComposition for testing
composition_crud = CRUDComposition(Composition)

# Fixtures
@pytest.fixture
def mock_composition():
    return Composition(
        id=1,
        name="Test Composition",
        description="Test Description",
        squad_size=10,
        is_public=True,
        created_by=1,
        build_id=1
    )

@pytest.fixture
def mock_composition_create():
    return CompositionCreate(
        name="New Composition",
        description="New Composition Description",
        squad_size=10,
        is_public=True,
        build_id=1
    )

@pytest.fixture
def mock_composition_update():
    return CompositionUpdate(
        name="Updated Composition",
        description="Updated Description",
        is_public=False
    )

# Helper function to create a mock result
def create_mock_result(return_value, is_list=False):
    mock_result = MagicMock()
    if is_list:
        mock_result.scalars.return_value.all.return_value = return_value
    else:
        mock_result.scalars.return_value.first.return_value = return_value
    return mock_result

# Tests
class TestCRUDComposition:
    @pytest.mark.asyncio
    async def test_create_composition_success(self, mock_composition, mock_composition_create):
        """Test creating a composition with valid data"""
        db = AsyncMock(spec=AsyncSession)
        db.scalar.return_value = mock_composition
        
        result = await composition_crud.create_async(db, obj_in=mock_composition_create, created_by=1)
        
        assert result.name == mock_composition_create.name
        assert result.description == mock_composition_create.description
        assert result.is_public == mock_composition_create.is_public
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_composition_by_id(self, mock_composition):
        """Test retrieving a composition by ID"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_composition)
        
        result = await composition_crud.get_async(db, 1)
        
        assert result.id == 1
        assert result.name == "Test Composition"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_composition(self, mock_composition, mock_composition_update):
        """Test updating a composition"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_composition)
        
        result = await composition_crud.update_async(
            db, db_obj=mock_composition, obj_in=mock_composition_update
        )
        
        assert result.name == "Updated Composition"
        assert result.description == "Updated Description"
        assert result.is_public is False
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_composition(self, mock_composition):
        """Test removing a composition"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_composition)
        
        result = await composition_crud.remove_async(db, id=1)
        
        assert result.name == "Test Composition"
        db.delete.assert_called_once_with(mock_composition)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_compositions_by_creator(self, mock_composition):
        """Test retrieving compositions by creator"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_composition], is_list=True)
        
        result = await composition_crud.get_multi_by_creator_async(db, creator_id=1)
        
        assert len(result) == 1
        assert result[0].name == "Test Composition"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_compositions(self, mock_composition):
        """Test retrieving public compositions"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_composition], is_list=True)
        
        result = await composition_crud.get_multi_public_async(db)
        
        assert len(result) == 1
        assert result[0].is_public is True
        db.execute.assert_called_once()
