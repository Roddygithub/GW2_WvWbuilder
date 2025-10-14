import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_build import CRUDBuild
from app.models import Build
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
        elite_specialization_id=1,
    )


@pytest.fixture
def mock_build_create():
    return BuildCreate(
        name="New Build",
        description="New Build Description",
        is_public=True,
        profession_id=1,
        elite_specialization_id=1,
    )


@pytest.fixture
def mock_build_update():
    return BuildUpdate(name="Updated Build", description="Updated Description", is_public=False)


# Helper function to create a mock result
def create_mock_result(return_value, is_list=False):
    mock_result = MagicMock()
    if is_list:
        mock_result.scalars.return_value.all.return_value = return_value
    else:
        mock_result.scalars.return_value.first.return_value = return_value
    return mock_result


# Tests
@patch("app.crud.crud_build.CRUDBuild.invalidate_cache", new_callable=AsyncMock)
class TestCRUDBuild:
    @pytest.mark.asyncio
    async def test_create_build_success(self, mock_invalidate_cache, mock_build_create):
        """Test creating a build with valid data"""
        db = AsyncMock(spec=AsyncSession)

        result = await build_crud.create(db, obj_in=mock_build_create, created_by=1)

        assert result.name == mock_build_create.name
        assert result.created_by == 1
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        mock_invalidate_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_build_by_id(self, mock_invalidate_cache, mock_build):
        """Test retrieving a build by ID without caching"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_build)

        with patch("app.crud.crud_build.settings.CACHE_ENABLED", False):
            result = await build_crud.get(db, 1)

        assert result.id == 1
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_build(self, mock_invalidate_cache, mock_build, mock_build_update):
        """Test updating a build"""
        db = AsyncMock(spec=AsyncSession)

        result = await build_crud.update(db, db_obj=mock_build, obj_in=mock_build_update)

        assert result.name == "Updated Build"
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        mock_invalidate_cache.assert_called()

    @pytest.mark.asyncio
    async def test_remove_build(self, mock_invalidate_cache, mock_build):
        """Test removing a build"""
        db = AsyncMock(spec=AsyncSession)

        with patch.object(build_crud, "get", new_callable=AsyncMock, return_value=mock_build) as mock_get:
            result = await build_crud.remove(db, id=1)

            assert result.name == "Test Build"
            mock_get.assert_called_once_with(db, id=1)
            db.delete.assert_called_once_with(mock_build)
            db.commit.assert_called_once()
            mock_invalidate_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_builds_by_owner(self, mock_invalidate_cache, mock_build):
        """Test retrieving builds by owner"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_build], is_list=True)

        result = await build_crud.get_multi_by_owner(db, owner_id=1)

        assert len(result) == 1
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_multi_by_profession(self, mock_invalidate_cache, mock_build):
        """Test retrieving builds by profession"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_build], is_list=True)

        result = await build_crud.get_multi_by_profession(db, profession_id=1)

        assert len(result) == 1
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_multi_by_elite_spec(self, mock_invalidate_cache, mock_build):
        """Test retrieving builds by elite specialization"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result([mock_build], is_list=True)

        result = await build_crud.get_multi_by_elite_spec(db, elite_spec_id=1)

        assert len(result) == 1
        db.execute.assert_called_once()


@patch("app.crud.crud_build.settings.CACHE_ENABLED", True)
@patch("app.crud.crud_build.cache", new_callable=AsyncMock)
class TestCRUDBuildCache:
    @pytest.mark.asyncio
    async def test_get_build_by_id_cache_hit(self, mock_cache, mock_build):
        """Test retrieving a build by ID from cache"""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = mock_build

        result = await build_crud.get(db, 1)

        assert result.id == 1
        mock_cache.get.assert_called_once_with("build:1")
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_build_by_id_cache_miss(self, mock_cache, mock_build):
        """Test retrieving a build by ID with a cache miss"""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = None
        db.execute.return_value = create_mock_result(mock_build)

        result = await build_crud.get(db, 1)

        assert result.id == 1
        mock_cache.get.assert_called_once_with("build:1")
        db.execute.assert_called_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_multi_by_owner_cache_hit(self, mock_cache, mock_build):
        """Test retrieving multiple builds by owner from cache"""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = [mock_build]

        result = await build_crud.get_multi_by_owner(db, owner_id=1, limit=10)

        assert len(result) == 1
        mock_cache.get.assert_called_once_with("builds:owner:1:0:10")
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_multi_by_owner_cache_miss(self, mock_cache, mock_build):
        """Test retrieving multiple builds by owner with a cache miss"""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = None
        db.execute.return_value = create_mock_result([mock_build], is_list=True)

        result = await build_crud.get_multi_by_owner(db, owner_id=1, limit=10)

        assert len(result) == 1
        mock_cache.get.assert_called_once_with("builds:owner:1:0:10")
        db.execute.assert_called_once()
        mock_cache.set.assert_called_once()
