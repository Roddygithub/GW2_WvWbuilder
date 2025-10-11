"""Authentication test helpers."""

from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models import User


def get_auth_headers(client: TestClient, user_id: int, scopes: Optional[list] = None) -> Dict[str, str]:
    """Get authentication headers for a test user.

    Args:
        client: Test client instance
        user_id: ID of the user to authenticate as
        scopes: Optional list of scopes for the access token

    Returns:
        Dictionary with Authorization header
    """
    access_token = create_access_token(subject=str(user_id), scopes=scopes or [])
    return {"Authorization": f"Bearer {access_token}"}


async def create_test_user(
    session: AsyncSession,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword",
    is_active: bool = True,
    is_superuser: bool = False,
    **kwargs,
) -> User:
    """Create a test user in the database.

    Args:
        session: Database session
        username: Username for the test user
        email: Email for the test user
        password: Password for the test user
        is_active: Whether the user is active
        is_superuser: Whether the user is a superuser
        **kwargs: Additional user attributes

    Returns:
        The created User instance
    """
    from app.core.security import get_password_hash
    from app.models import User

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_active=is_active,
        is_superuser=is_superuser,
        **kwargs,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def create_test_role(
    session: AsyncSession,
    name: str = "test_role",
    description: str = "Test Role",
    permission_level: int = 1,
    is_default: bool = False,
    **kwargs,
) -> "Role":
    """Create a test role in the database.

    Args:
        session: Database session
        name: Name of the role
        description: Description of the role
        permission_level: Permission level (1-10)
        is_default: Whether this is a default role
        **kwargs: Additional role attributes

    Returns:
        The created Role instance
    """
    from app.models import Role

    role = Role(
        name=name,
        description=description,
        permission_level=permission_level,
        is_default=is_default,
        **kwargs,
    )

    session.add(role)
    await session.commit()
    await session.refresh(role)

    return role


def get_superuser_auth_headers(client: TestClient, user_id: int = 1) -> Dict[str, str]:
    """Get authentication headers for a superuser.

    Args:
        client: Test client instance
        user_id: ID of the superuser

    Returns:
        Dictionary with Authorization header for a superuser
    """
    return get_auth_headers(client=client, user_id=user_id, scopes=["superuser"])
