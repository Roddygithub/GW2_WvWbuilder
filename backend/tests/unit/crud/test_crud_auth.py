import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional

from app.crud.user import CRUDUser
from app.models import User, Token
from app.core.security import get_password_hash, verify_password

# Create an instance of CRUDUser for testing (auth operations are part of user CRUD)
user_crud = CRUDUser(User)

# For backward compatibility
class CRUDAuth:
    """Compatibility layer for auth operations."""
    
    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user."""
        user = await user_crud.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def create_access_token(
        self, db: AsyncSession, user_id: int, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token for a user."""
        # This is a simplified version - in a real app, you'd use a proper JWT library
        from app.core.security import create_access_token
        return create_access_token(
            data={"sub": str(user_id)},
            expires_delta=expires_delta
        )
    
    async def get_token(self, db: AsyncSession, token: str) -> Optional[Token]:
        """Get a token by its value."""
        return await db.execute(
            Token.select().where(Token.token == token)
        ).scalar_one_or_none()
    
    async def revoke_token(self, db: AsyncSession, token: str) -> None:
        """Revoke a token."""
        db_token = await self.get_token(db, token=token)
        if db_token:
            db_token.revoked = True
            db_token.revoked_at = datetime.utcnow()
            db.add(db_token)
            await db.commit()

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
        role_id=1,
    )


@pytest.fixture
def mock_token():
    return Token(
        id=1,
        token="test_token",
        expires_at=datetime.utcnow() + timedelta(days=1),
        user_id=1,
    )


# Tests
class TestCRUDAuth:
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_user):
        """Test successful user authentication"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value=mock_user))
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
                return_value=MagicMock(first=MagicMock(return_value=mock_user))
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
        assert hasattr(token, "token")
        assert hasattr(token, "expires_at")
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token(self, mock_token):
        """Test retrieving a token"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value=mock_token))
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
                return_value=MagicMock(first=MagicMock(return_value=mock_token))
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
