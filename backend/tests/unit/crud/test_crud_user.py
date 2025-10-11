import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User as UserModel
from app.schemas.user import UserCreate, UserUpdate

# Use the user instance from the module, which is a CRUDUser instance
from app.crud.user import user as user_crud


# Fixtures
@pytest.fixture
def mock_user() -> UserModel:
    """Fixture for a mock user model instance."""
    return UserModel(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password_string",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def mock_user_create() -> UserCreate:
    """Fixture for a user creation schema."""
    return UserCreate(email="new@example.com", password="new_password")


@pytest.fixture
def mock_user_update() -> UserUpdate:
    """Fixture for a user update schema."""
    return UserUpdate(email="updated@example.com", full_name="Updated Name")


# Helper function to create a mock result for SQLAlchemy queries
def create_mock_sql_result(return_value):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = return_value
    return mock_result


class TestCRUDUser:
    """Test suite for asynchronous user CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_by_email_async(self, mock_user):
        """Test getting a user by email asynchronously."""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_sql_result(mock_user)

        result = await user_crud.get_by_email_async(db, email="test@example.com")

        assert result is not None
        assert result.id == mock_user.id
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.core.security.get_password_hash", return_value="hashed_new_password")
    async def test_create_async(self, mock_get_password_hash, mock_user_create):
        """Test creating a user asynchronously."""
        db = AsyncMock(spec=AsyncSession)

        # Mock the check for existing email to return None (user does not exist)
        with patch.object(user_crud, "get_by_email_async", new_callable=AsyncMock, return_value=None):
            created_user = await user_crud.create_async(db, obj_in=mock_user_create)

            mock_get_password_hash.assert_called_once_with("new_password")
            db.add.assert_called_once()
            db.commit.assert_awaited_once()
            db.refresh.assert_awaited_once()
            assert created_user.email == mock_user_create.email
            assert created_user.hashed_password == "hashed_new_password"

    @pytest.mark.asyncio
    async def test_create_async_existing_email(self, mock_user_create, mock_user):
        """Test that creating a user with an existing email raises ValueError."""
        db = AsyncMock(spec=AsyncSession)

        # Mock the check for existing email to return a user
        with patch.object(user_crud, "get_by_email_async", new_callable=AsyncMock, return_value=mock_user):
            with pytest.raises(ValueError, match="Email already registered"):
                await user_crud.create_async(db, obj_in=mock_user_create)

    @pytest.mark.asyncio
    @patch("app.core.security.verify_password", return_value=True)
    async def test_authenticate_async_success(self, mock_verify_password, mock_user):
        """Test successful user authentication."""
        db = AsyncMock(spec=AsyncSession)
        with patch.object(user_crud, "get_by_email_async", new_callable=AsyncMock, return_value=mock_user):
            authenticated_user = await user_crud.authenticate_async(
                db, email="test@example.com", password="correct_password"
            )

            mock_verify_password.assert_called_once_with("correct_password", mock_user.hashed_password)
            assert authenticated_user == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_async_user_not_found(self):
        """Test authentication failure when user does not exist."""
        db = AsyncMock(spec=AsyncSession)
        with patch.object(user_crud, "get_by_email_async", new_callable=AsyncMock, return_value=None):
            authenticated_user = await user_crud.authenticate_async(
                db, email="nonexistent@example.com", password="any_password"
            )
            assert authenticated_user is None

    @pytest.mark.asyncio
    @patch("app.core.security.verify_password", return_value=False)
    async def test_authenticate_async_wrong_password(self, mock_verify_password, mock_user):
        """Test authentication failure with wrong password."""
        db = AsyncMock(spec=AsyncSession)
        with patch.object(user_crud, "get_by_email_async", new_callable=AsyncMock, return_value=mock_user):
            authenticated_user = await user_crud.authenticate_async(
                db, email="test@example.com", password="wrong_password"
            )
            assert authenticated_user is None

    @pytest.mark.asyncio
    @patch("app.core.security.get_password_hash", return_value="hashed_updated_password")
    async def test_update_async_with_password(self, mock_get_password_hash, mock_user):
        """Test updating a user, including their password."""
        db = AsyncMock(spec=AsyncSession)
        update_data = UserUpdate(password="updated_password")

        updated_user = await user_crud.update_async(db, db_obj=mock_user, obj_in=update_data)

        mock_get_password_hash.assert_called_once_with("updated_password")
        assert updated_user.hashed_password == "hashed_updated_password"
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()

    def test_is_superuser(self, mock_user):
        """Test the is_superuser check."""
        assert user_crud.is_superuser(mock_user) is False
        mock_user.is_superuser = True
        assert user_crud.is_superuser(mock_user) is True
