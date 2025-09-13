import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.crud.auth import CRUDAuth, get_password_hash, verify_password
from app.models import User, Token
from app.schemas.user import UserCreate, UserUpdate

# Create an instance of CRUDAuth for testing
auth_crud = CRUDAuth()

# Fixtures
@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        role_id=1
    )

@pytest.fixture
def mock_token():
    return Token(
        id=1,
        token="test_token",
        expires_at=datetime.utcnow() + timedelta(days=1),
        user_id=1
    )

# Tests
class TestCRUDAuth:
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_user):
        """Test successful user authentication"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(
                    first=MagicMock(return_value=mock_user)
                )
            )
        )
        
        result = await auth_crud.authenticate(
            db, username="testuser", password="password123"
        )
        
        assert result is not None
        assert result.username == "testuser"
        assert verify_password("password123", result.hashed_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_user):
        """Test authentication with wrong password"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(
                    first=MagicMock(return_value=mock_user)
                )
            )
        )
        
        result = await auth_crud.authenticate(
            db, username="testuser", password="wrongpassword"
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_token(self, mock_user):
        """Test creating an access token"""
        db = AsyncMock(spec=AsyncSession)
        
        token = await auth_crud.create_access_token(
            db, user_id=1, expires_delta=timedelta(days=1)
        )
        
        assert token is not None
        assert hasattr(token, 'token')
        assert hasattr(token, 'expires_at')
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token(self, mock_token):
        """Test retrieving a token"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(
                    first=MagicMock(return_value=mock_token)
                )
            )
        )
        
        result = await auth_crud.get_token(db, token="test_token")
        
        assert result is not None
        assert result.token == "test_token"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_token(self, mock_token):
        """Test revoking a token"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(
                    first=MagicMock(return_value=mock_token)
                )
            )
        )
        
        await auth_crud.revoke_token(db, token="test_token")
        
        db.delete.assert_called_once_with(mock_token)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_password(self):
        """Test password verification"""
        plain_password = "testpassword"
        hashed_password = get_password_hash(plain_password)
        
        assert verify_password(plain_password, hashed_password) is True
        assert verify_password("wrongpassword", hashed_password) is False
