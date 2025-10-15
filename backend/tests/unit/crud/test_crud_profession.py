import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.profession import CRUDProfession
from app.models import Profession
from app.schemas.profession import ProfessionCreate, ProfessionUpdate

# Create an instance of CRUDProfession for testing
profession_crud = CRUDProfession(Profession)


# Fixtures
@pytest.fixture
def mock_profession():
    return Profession(
        id=1,
        name="Test Profession",
        description="Test Description",
        icon_url="https://example.com/warrior.png",
    )


@pytest.fixture
def mock_profession_create():
    return ProfessionCreate(
        name="New Profession",
        description="New Profession Description",
        icon_url="https://example.com/new_icon.png",
    )


@pytest.fixture
def mock_profession_update():
    return ProfessionUpdate(
        name="Updated Profession", description="Updated Description"
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
class TestCRUDProfession:
    @pytest.mark.asyncio
    async def test_create_profession_success(
        self, mock_profession, mock_profession_create
    ):
        """Test creating a profession with valid data"""
        db = AsyncMock(spec=AsyncSession)
        db.scalar.return_value = mock_profession

        result = await profession_crud.create_async(db, obj_in=mock_profession_create)

        assert result.name == mock_profession_create.name
        assert result.description == mock_profession_create.description
        assert result.icon_url == mock_profession_create.icon_url
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profession_by_id(self, mock_profession):
        """Test retrieving a profession by ID"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_profession)

        result = await profession_crud.get_async(db, 1)

        assert result.id == 1
        assert result.name == "Test Profession"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profession_by_name(self, mock_profession):
        """Test retrieving a profession by name"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_profession)

        result = await profession_crud.get_by_name_async(db, name="Test Profession")

        assert result.name == "Test Profession"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profession(self, mock_profession, mock_profession_update):
        """Test updating a profession"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_profession)

        result = await profession_crud.update_async(
            db, db_obj=mock_profession, obj_in=mock_profession_update
        )

        assert result.name == "Updated Profession"
        assert result.description == "Updated Description"
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_profession(self, mock_profession):
        """Test removing a profession"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_profession)

        result = await profession_crud.remove_async(db, id=1)

        assert result.name == "Test Profession"
        db.delete.assert_called_once_with(mock_profession)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_professions(self, mock_profession):
        """Test retrieving all professions"""
        db = AsyncMock(spec=AsyncSession)
        mock_profession2 = Profession(
            id=2, name="Second Profession", description="Desc 2"
        )
        db.execute.return_value = create_mock_result(
            [mock_profession, mock_profession2], is_list=True
        )

        result = await profession_crud.get_multi_async(db)

        assert len(result) == 2
        assert result[0].name == "Test Profession"
        assert result[1].name == "Second Profession"
        db.execute.assert_called_once()
