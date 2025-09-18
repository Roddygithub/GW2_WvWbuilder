import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.build import CRUDBuild
from app.models import Build, User, Profession, EliteSpecialization
from app.schemas.build import BuildCreate, BuildUpdate

# Create an instance of CRUDBuild for testing
build_crud = CRUDBuild(Build)

# Fixtures
@pytest.fixture
def mock_build():
    return Build(
        id=1,
        name="Test Build",
        description="Test Description",
        is_public=True,
        created_by=1,
        profession_id=1,
        elite_specialization_id=1
    )

@pytest.fixture
def mock_build_create():
    return BuildCreate(
        name="New Build",
        description="New Build Description",
        is_public=True,
        profession_id=1,
        elite_specialization_id=1
    )

@pytest.fixture
def mock_build_update():
    return BuildUpdate(
        name="Updated Build",
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
class TestCRUDBuild:
    @pytest.mark.asyncio
    async def test_create_build_success(self, mock_build, mock_build_create):
        """Test creating a build with valid data"""
        db = AsyncMock(spec=AsyncSession)
        db.scalar.return_value = mock_build
        
        result = await build_crud.create_async(db, obj_in=mock_build_create, created_by=1)
        
        assert result.name == mock_build_create.name
        assert result.description == mock_build_create.description
        assert result.is_public == mock_build_create.is_public
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_build_by_id(self, mock_build):
        """Test retrieving a build by ID"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_build)
        
        result = await build_crud.get_async(db, 1)
        
        assert result.id == 1
        assert result.name == "Test Build"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_build(self, mock_build, mock_build_update):
        """Test updating a build"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_build)
        
        result = await build_crud.update_async(db, db_obj=mock_build, obj_in=mock_build_update)
        
        assert result.name == "Updated Build"
        assert result.description == "Updated Description"
        assert result.is_public is False
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_build(self, mock_build):
        """Test removing a build"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_build)
        
        result = await build_crud.remove_async(db, id=1)
        
        assert result.name == "Test Build"
        db.delete.assert_called_once_with(mock_build)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_builds_by_creator(self, mock_build):
        """Test retrieving builds by creator"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_build], is_list=True)
        
        result = await build_crud.get_multi_by_creator_async(db, creator_id=1)
        
        assert len(result) == 1
        assert result[0].name == "Test Build"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_builds(self, mock_build):
        """Test retrieving public builds"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_build], is_list=True)
        
        result = await build_crud.get_multi_public_async(db)
        
        assert len(result) == 1
        assert result[0].is_public is True
        db.execute.assert_called_once()
