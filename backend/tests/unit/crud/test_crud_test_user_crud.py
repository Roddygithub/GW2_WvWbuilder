"""Tests for user CRUD operations."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.crud.user import CRUDUser
from app.models import User as UserModel, Role as RoleModel
from app.schemas.user import UserCreate, UserUpdate
from app.core import security


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    return UserModel(
        id=1,
        email="test@example.com",
        hashed_password=security.get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        roles=[],
    )


@pytest.fixture
def mock_role():
    """Create a mock role object."""
    return RoleModel(id=1, name="user")


@pytest.fixture
def crud_user():
    """Create a CRUDUser instance for testing."""
    return CRUDUser(UserModel)


class TestCRUDUserSync:
    """Test synchronous user CRUD operations."""

    def test_get_by_email(self, crud_user, mock_user):
        """Test getting a user by email (synchronous)."""
        # Setup
        db = MagicMock(spec=Session)
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_user
        db.scalars.return_value = mock_scalars

        # Test
        result = crud_user.get_by_email(db, email="test@example.com")

        # Assert
        assert result == mock_user
        db.scalars.assert_called_once()
        mock_scalars.first.assert_called_once()

    def test_get_with_roles(self, crud_user, mock_user, mock_role):
        """Test getting a user with roles (synchronous)."""
        # Setup
        db = MagicMock(spec=Session)
        mock_scalars = MagicMock()
        mock_user.roles = [mock_role]
        mock_scalars.first.return_value = mock_user
        db.scalars.return_value = mock_scalars

        # Test
        result = crud_user.get_with_roles(db, id=1)

        # Assert
        assert result == mock_user
        assert result.roles == [mock_role]
        db.scalars.assert_called_once()
        mock_scalars.first.assert_called_once()

    def test_is_superuser(self, crud_user, mock_user):
        """Test checking if a user is a superuser."""
        # Test non-superuser
        assert not crud_user.is_superuser(mock_user)

        # Test superuser
        mock_user.is_superuser = True
        assert crud_user.is_superuser(mock_user)

    def test_create_user(self, crud_user, mock_user):
        """Test creating a new user (synchronous)."""
        # Setup
        db = MagicMock(spec=Session)
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()

        user_data = UserCreate(
            email="new@example.com", password="testpass123", full_name="Test User"
        )

        # Test
        result = crud_user.create(db, obj_in=user_data)

        # Assert
        assert result.email == user_data.email
        assert result.hashed_password is not None
        assert result.hashed_password != user_data.password
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()


class TestCRUDUserAsync:
    """Test asynchronous user CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_by_email_async(self, crud_user, mock_user):
        """Test getting a user by email (asynchronous)."""
        # Setup
        mock_result = MagicMock()
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_user
        mock_result.scalars.return_value = mock_scalar_result

        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = mock_result

        # Test
        result = await crud_user.get_by_email_async(db, email="test@example.com")

        # Assert
        assert result == mock_user
        db.execute.assert_awaited_once()
        mock_scalar_result.first.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_roles_async(self, crud_user, mock_user, mock_role):
        """Test getting a user with roles (asynchronous)."""
        # Setup
        mock_user.roles = [mock_role]
        mock_result = MagicMock()
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_user
        mock_result.scalars.return_value = mock_scalar_result

        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = mock_result

        # Test
        result = await crud_user.get_with_roles_async(db, id=1)

        # Assert
        assert result == mock_user
        assert result.roles == [mock_role]
        db.execute.assert_awaited_once()
        mock_scalar_result.first.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_async(self, crud_user, mock_user):
        """Test user authentication (asynchronous)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Mock get_by_email_async to return our test user
        with patch.object(crud_user, "get_by_email_async", return_value=mock_user):
            # Test successful authentication
            user = await crud_user.authenticate_async(
                db, email="test@example.com", password="testpassword"
            )
            assert user == mock_user

            # Test wrong password
            user = await crud_user.authenticate_async(
                db, email="test@example.com", password="wrongpassword"
            )
            assert user is None

            # Test non-existent user
            with patch.object(crud_user, "get_by_email_async", return_value=None):
                user = await crud_user.authenticate_async(
                    db, email="nonexistent@example.com", password="testpassword"
                )
                assert user is None

    @pytest.mark.asyncio
    async def test_update_user_async(self, crud_user, mock_user):
        """Test updating a user (asynchronous)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        db.refresh = AsyncMock()

        update_data = UserUpdate(
            email="updated@example.com",
            full_name="Updated Name",
            password="newpassword123",
        )

        # Test
        result = await crud_user.update_async(db, db_obj=mock_user, obj_in=update_data)

        # Assert
        assert result.email == update_data.email
        assert result.full_name == update_data.full_name
        assert (
            result.hashed_password != mock_user.hashed_password
        )  # Password was updated
        db.refresh.assert_awaited_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_remove_user_async(self, crud_user, mock_user):
        """Test removing a user (asynchronous)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        db.delete = AsyncMock()
        db.commit = AsyncMock()

        # Test
        result = await crud_user.remove_async(db, id=1)

        # Assert
        assert result == 1  # Number of rows affected
        db.delete.assert_awaited_once()
        db.commit.assert_awaited_once()


class TestUserRoleManagement:
    """Test user role management functionality."""

    @pytest.mark.asyncio
    async def test_add_role_to_user_async(self, crud_user, mock_user, mock_role):
        """Test adding a role to a user."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_user.roles = []
        
        # Mock get_async to return the mock user
        crud_user.get_async = AsyncMock(return_value=mock_user)
        
        # Mock the role query
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_role
        db.execute.return_value = mock_result
        
        # Mock the user query with roles
        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = mock_user
        db.execute.return_value = mock_user_result

        # Test adding role
        result = await crud_user.add_role_to_user_async(db, user_id=1, role_id=1)

        # Assert
        assert result is True
        assert len(mock_user.roles) == 1
        assert mock_user.roles[0].id == 1
        db.add.assert_called_once_with(mock_user)
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_remove_role_from_user_async(self, crud_user, mock_user, mock_role):
        """Test removing a role from a user."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_user.roles = [mock_role]
        
        # Mock get_async to return the mock user
        crud_user.get_async = AsyncMock(return_value=mock_user)
        
        # Mock the role query
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_role
        db.execute.return_value = mock_result
        
        # Mock the user query with roles
        mock_user_result = MagicMock()
        mock_user_result.scalars.return_value.first.return_value = mock_user
        db.execute.return_value = mock_user_result

        # Test removing role
        result = await crud_user.remove_role_from_user_async(db, user_id=1, role_id=1)

        # Assert
        assert result is True
        assert len(mock_user.roles) == 0
        db.add.assert_called_once_with(mock_user)
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(mock_user)


class TestUserActivation:
    """Test user activation/deactivation functionality."""

    @pytest.mark.asyncio
    async def test_activate_user_async(self, crud_user, mock_user):
        """Test activating a user."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_user.is_active = False

        # Test activation
        with patch.object(crud_user, "get_async", return_value=mock_user):
            result = await crud_user.activate_user_async(db, user_id=1)

            # Assert
            assert result.is_active is True
            db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_async(self, crud_user, mock_user):
        """Test deactivating a user."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_user.is_active = True

        # Test deactivation
        with patch.object(crud_user, "get_async", return_value=mock_user):
            result = await crud_user.deactivate_user_async(db, user_id=1)

            # Assert
            assert result.is_active is False
            db.commit.assert_awaited_once()
