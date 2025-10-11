"""Test client helpers for API testing."""

from typing import Any, AsyncGenerator, Dict, Optional, Union

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models import User


class TestClientFactory:
    """Factory for creating test clients with authentication."""

    def __init__(self, app: FastAPI):
        """Initialize the test client factory.

        Args:
            app: FastAPI application instance
        """
        self.app = app

    def get_test_client(self, **kwargs: Any) -> TestClient:
        """Get a synchronous test client.

        Args:
            **kwargs: Additional arguments to pass to TestClient

        Returns:
            A TestClient instance
        """
        return TestClient(app=self.app, **kwargs)

    def get_authenticated_client(self, user: User, scopes: Optional[list[str]] = None, **kwargs: Any) -> TestClient:
        """Get an authenticated test client.

        Args:
            user: User to authenticate as
            scopes: List of OAuth2 scopes
            **kwargs: Additional arguments to pass to TestClient

        Returns:
            An authenticated TestClient instance
        """
        access_token = create_access_token(subject=user.id, scopes=scopes or [])

        client = self.get_test_client(**kwargs)
        client.headers.update({"Authorization": f"Bearer {access_token}"})

        return client

    async def get_async_client(self, base_url: str = "http://test", **kwargs: Any) -> AsyncGenerator[AsyncClient, None]:
        """Get an asynchronous test client.

        Args:
            base_url: Base URL for the test client
            **kwargs: Additional arguments to pass to AsyncClient

        Yields:
            An AsyncClient instance
        """
        async with AsyncClient(transport=ASGITransport(app=self.app), base_url=base_url, **kwargs) as client:
            yield client

    async def get_authenticated_async_client(
        self, user: User, scopes: Optional[list[str]] = None, **kwargs: Any
    ) -> AsyncGenerator[AsyncClient, None]:
        """Get an authenticated asynchronous test client.

        Args:
            user: User to authenticate as
            scopes: List of OAuth2 scopes
            **kwargs: Additional arguments to pass to AsyncClient

        Yields:
            An authenticated AsyncClient instance
        """
        access_token = create_access_token(subject=user.id, scopes=scopes or [])

        async with AsyncClient(transport=ASGITransport(app=self.app), base_url="http://test", **kwargs) as client:
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            yield client


class AuthTestClient:
    """Test client with authentication helpers."""

    def __init__(self, client: TestClient, user: User):
        """Initialize the authenticated test client.

        Args:
            client: TestClient instance
            user: Authenticated user
        """
        self.client = client
        self.user = user

    def get(self, *args, **kwargs):
        """Send a GET request."""
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Send a POST request."""
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """Send a PUT request."""
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Send a DELETE request."""
        return self.client.delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """Send a PATCH request."""
        return self.client.patch(*args, **kwargs)

    def head(self, *args, **kwargs):
        """Send a HEAD request."""
        return self.client.head(*args, **kwargs)

    def options(self, *args, **kwargs):
        """Send an OPTIONS request."""
        return self.client.options(*args, **kwargs)


async def create_test_user(
    session: AsyncSession,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword",
    is_active: bool = True,
    is_superuser: bool = False,
    **kwargs: Any,
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
    **kwargs: Any,
) -> Any:
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


def get_auth_headers(user_id: Union[str, int], scopes: Optional[list[str]] = None) -> Dict[str, str]:
    """Get authentication headers for a user.

    Args:
        user_id: User ID
        scopes: List of OAuth2 scopes

    Returns:
        Dictionary with Authorization header
    """
    access_token = create_access_token(subject=str(user_id), scopes=scopes or [])

    return {"Authorization": f"Bearer {access_token}"}


def get_superuser_auth_headers(user_id: Union[str, int] = 1) -> Dict[str, str]:
    """Get authentication headers for a superuser.

    Args:
        user_id: User ID

    Returns:
        Dictionary with Authorization header for a superuser
    """
    return get_auth_headers(user_id=user_id, scopes=["superuser"])
