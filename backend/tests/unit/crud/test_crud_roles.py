import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.crud.role import CRUDRole
from app.models import Role as RoleModel
from app.schemas.role import RoleCreate, RoleUpdate

# Create an instance of CRUDRole for testing
role_crud = CRUDRole(RoleModel)

# Fixtures
@pytest.fixture
def mock_role():
    return RoleModel(
        id=1,
        name="Test Role",
        description="Test Description",
        permission_level=1,
        is_default=False
    )

@pytest.fixture
def mock_role_create():
    return RoleCreate(
        name="New Role",
        description="New Role Description",
        permission_level=1
    )

@pytest.fixture
def mock_role_update():
    return RoleUpdate(
        name="Updated Role",
        description="Updated Description",
        permission_level=2
    )

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
        db.get.return_value = mock_role
        
        result = await role_crud.get_async(db, 1)
        
        assert result.id == 1
        assert result.name == "Test Role"
        db.get.assert_called_once_with(RoleModel, 1)

    @pytest.mark.asyncio
    async def test_get_role_by_name(self, mock_role):
        """Test retrieving a role by name"""
        db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_role
        db.execute.return_value = mock_result
        
        result = await role_crud.get_by_name_async(db, name="Test Role")
        
        assert result.name == "Test Role"
        db.execute.assert_called_once()
        args, _ = db.execute.call_args
        assert isinstance(args[0].whereclause.compare(select(RoleModel).where(RoleModel.name == "Test Role").whereclause), bool)

    @pytest.mark.asyncio
    async def test_get_roles_by_permission_level(self, mock_role):
        """Test retrieving roles by permission level"""
        db = AsyncMock(spec=AsyncSession)
        mock_role2 = RoleModel(id=2, name="Admin", permission_level=10, is_default=False)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_role, mock_role2]
        db.execute.return_value = mock_result
        
        result = await role_crud.get_by_permission_level_async(db, permission_level=1)
        
        assert len(result) == 2
        assert result[0].name == "Test Role"
        assert result[1].name == "Admin"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_roles_in_permission_range(self, mock_role):
        """Test retrieving roles within a permission level range"""
        db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_role]
        db.execute.return_value = mock_result
        
        result = await role_crud.get_multi_by_permission_range_async(
            db, min_level=0, max_level=5, skip=0, limit=10
        )
        
        assert len(result) == 1
        assert result[0].name == "Test Role"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_with_users(self, mock_role):
        """Test retrieving a role with its associated users"""
        db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.first.return_value = mock_role
        db.execute.return_value = mock_result
        
        result = await role_crud.get_with_users_async(db, id=1)
        
        assert result.name == "Test Role"
        db.execute.assert_called_once()
        args, _ = db.execute.call_args
        assert isinstance(args[0].whereclause.compare(select(RoleModel).where(RoleModel.id == 1).whereclause), bool)
        assert selectinload(RoleModel.users) in [opt for opt in args[0]._with_options]

    @pytest.mark.asyncio
    async def test_get_all_role_names(self, mock_role):
        """Test retrieving all role names"""
        db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.all.return_value = [("Role1",), ("Role2",)]
        db.execute.return_value = mock_result
        
        result = await role_crud.get_all_names_async(db)
        
        assert result == ["Role1", "Role2"]
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_id_by_name(self, mock_role):
        """Test retrieving a role ID by name"""
        db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        db.execute.return_value = mock_result
        
        result = await role_crud.get_id_by_name_async(db, name="Test Role")
        
        assert result == 1
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_default_role(self, mock_role):
        """Test retrieving the default role"""
        db = AsyncMock(spec=AsyncSession)
        mock_role.is_default = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_role
        db.execute.return_value = mock_result
        
        result = await role_crud.get_default_role_async(db)
        
        assert result.is_default is True
        db.execute.assert_called_once()
        args, _ = db.execute.call_args
        assert "is_default" in str(args[0])

    @pytest.mark.asyncio
    async def test_update_role(self, mock_role, mock_role_update):
        """Test updating a role"""
        db = AsyncMock(spec=AsyncSession)
        db.get.return_value = mock_role
        
        result = await role_crud.update_async(db, db_obj=mock_role, obj_in=mock_role_update)
        
        assert result.name == "Updated Role"
        assert result.description == "Updated Description"
        assert result.permission_level == 2
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_role(self, mock_role):
        """Test removing a role"""
        db = AsyncMock(spec=AsyncSession)
        db.get.return_value = mock_role
        
        result = await role_crud.remove_async(db, id=1)
        
        assert result.name == "Test Role"
        db.delete.assert_called_once_with(mock_role)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_role(self):
        """Test removing a non-existent role"""
        db = AsyncMock(spec=AsyncSession)
        db.get.return_value = None
        
        result = await role_crud.remove_async(db, id=999)
        
        assert result is None
        db.delete.assert_not_called()
        db.commit.assert_not_called()
