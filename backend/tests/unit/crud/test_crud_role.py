import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.role import CRUDRole
from app.models import Role
from app.schemas.role import RoleCreate, RoleUpdate

# Create an instance of CRUDRole for testing
role_crud = CRUDRole(Role)


# Fixtures
@pytest.fixture
def mock_role():
    return Role(
        id=1,
        name="Test Role",
        description="Test Description",
        permission_level=1,
        is_default=False,
    )


@pytest.fixture
def mock_role_create():
    return RoleCreate(
        name="New Role",
        description="New Role Description",
        permission_level=1,
        is_default=False,
    )


@pytest.fixture
def mock_role_update():
    return RoleUpdate(
        name="Updated Role",
        description="Updated Description",
        permission_level=2,
        is_default=True,
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
class TestCRUDRole:
    @pytest.mark.asyncio
    async def test_create_role_success(self, mock_role, mock_role_create):
        """Test creating a role with valid data"""
        db = AsyncMock(spec=AsyncSession)
        db.scalar.return_value = mock_role

        result = await role_crud.create_async(db, obj_in=mock_role_create)

        assert result.name == mock_role_create.name
        assert result.description == mock_role_create.description
        assert result.permission_level == mock_role_create.permission_level
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_id(self, mock_role):
        """Test retrieving a role by ID"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_role)

        result = await role_crud.get_async(db, 1)

        assert result.id == 1
        assert result.name == "Test Role"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_name(self, mock_role):
        """Test retrieving a role by name"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_role)

        result = await role_crud.get_by_name_async(db, name="Test Role")

        assert result.name == "Test Role"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_role(self, mock_role, mock_role_update):
        """Test updating a role"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_role)

        result = await role_crud.update_async(db, db_obj=mock_role, obj_in=mock_role_update)

        assert result.name == "Updated Role"
        assert result.description == "Updated Description"
        assert result.permission_level == 2
        assert result.is_default is True
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_role(self, mock_role):
        """Test removing a role"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_role)

        result = await role_crud.remove_async(db, id=1)

        assert result.name == "Test Role"
        db.delete.assert_called_once_with(mock_role)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_roles_by_permission_level(self, mock_role):
        """Test retrieving roles by permission level"""
        db = AsyncMock(spec=AsyncSession)
        mock_role2 = Role(id=2, name="Admin", permission_level=10, is_default=False)
        db.execute.return_value = create_mock_result([mock_role, mock_role2], is_list=True)

        result = await role_crud.get_by_permission_level_async(db, permission_level=1)

        assert len(result) == 2
        assert result[0].name == "Test Role"
        assert result[1].name == "Admin"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_default_role(self, mock_role):
        """Test retrieving the default role"""
        db = AsyncMock(spec=AsyncSession)
        mock_role.is_default = True
        db.execute.return_value = create_mock_result(mock_role)

        result = await role_crud.get_default_role_async(db)

        assert result.is_default is True
        db.execute.assert_called_once()
