"""Authentication and authorization test helpers."""

from typing import Any, Dict, List, Optional, Union

from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.tests.helpers.assertions import assert_status_code


def get_auth_headers(user_id: Union[str, int], scopes: Optional[List[str]] = None) -> Dict[str, str]:
    """Get authentication headers for a user.

    Args:
        user_id: User ID
        scopes: Optional list of OAuth2 scopes

    Returns:
        Dictionary with Authorization header
    """
    access_token = create_access_token(subject=str(user_id), scopes=scopes or [])
    return {"Authorization": f"Bearer {access_token}"}


def get_superuser_auth_headers(user_id: Union[str, int] = 1) -> Dict[str, str]:
    """Get authentication headers for a superuser.

    Args:
        user_id: User ID (defaults to 1)

    Returns:
        Dictionary with Authorization header for a superuser
    """
    return get_auth_headers(user_id=user_id, scopes=["superuser"])


async def create_test_user(
    session: AsyncSession,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False,
    roles: Optional[List[Role]] = None,
    **kwargs,
) -> User:
    """Create a test user in the database.

    Args:
        session: Database session
        username: Username (defaults to random username)
        email: Email (defaults to random email)
        password: Password (defaults to random password)
        is_active: Whether the user is active
        is_superuser: Whether the user is a superuser
        roles: List of roles to assign to the user
        **kwargs: Additional user attributes

    Returns:
        The created User instance
    """
    from app.tests.helpers.test_data import (
        random_username,
        random_email,
        random_password,
    )

    user = User(
        username=username or random_username(),
        email=email or random_email(),
        hashed_password=get_password_hash(password or random_password()),
        is_active=is_active,
        is_superuser=is_superuser,
        **kwargs,
    )

    if roles:
        user.roles = roles

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
) -> Role:
    """Create a test role in the database.

    Args:
        session: Database session
        name: Role name
        description: Role description
        permission_level: Permission level (1-10)
        is_default: Whether this is a default role
        **kwargs: Additional role attributes

    Returns:
        The created Role instance
    """
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


async def create_user_and_get_auth_headers(
    client: TestClient,
    session: AsyncSession,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False,
    roles: Optional[List[Role]] = None,
    **kwargs,
) -> Dict[str, str]:
    """Create a test user and get authentication headers.

    Args:
        client: Test client
        session: Database session
        username: Username (defaults to random username)
        email: Email (defaults to random email)
        password: Password (defaults to random password)
        is_active: Whether the user is active
        is_superuser: Whether the user is a superuser
        roles: List of roles to assign to the user
        **kwargs: Additional user attributes

    Returns:
        Dictionary with Authorization header
    """
    user = await create_test_user(
        session=session,
        username=username,
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        roles=roles,
        **kwargs,
    )

    # Get auth token
    login_data = {
        "username": user.email,
        "password": password or "testpassword",
    }

    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert_status_code(response, status.HTTP_200_OK)

    token_data = response.json()
    access_token = token_data["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def get_token_payload(token: str) -> Dict[str, Any]:
    """Get the payload from a JWT token.

    Args:
        token: JWT token

    Returns:
        Token payload as a dictionary
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_aud": False},
    )


def assert_token_payload(
    token: str,
    expected_sub: Optional[Union[str, int]] = None,
    expected_scopes: Optional[List[str]] = None,
    expected_iss: Optional[str] = None,
    expected_aud: Optional[str] = None,
) -> Dict[str, Any]:
    """Assert that a JWT token has the expected payload.

    Args:
        token: JWT token to verify
        expected_sub: Expected subject (user ID)
        expected_scopes: Expected OAuth2 scopes
        expected_iss: Expected issuer
        expected_aud: Expected audience

    Returns:
        The decoded token payload

    Raises:
        AssertionError: If any assertion fails
    """
    payload = get_token_payload(token)

    if expected_sub is not None:
        assert str(payload["sub"]) == str(expected_sub), f"Expected subject '{expected_sub}', got '{payload['sub']}'"

    if expected_scopes is not None:
        scopes = payload.get("scopes", [])
        if not isinstance(scopes, list):
            scopes = [scopes]

        assert set(scopes) == set(expected_scopes), f"Expected scopes {expected_scopes}, got {scopes}"

    if expected_iss is not None:
        assert payload["iss"] == expected_iss, f"Expected issuer '{expected_iss}', got '{payload['iss']}'"

    if expected_aud is not None:
        assert payload["aud"] == expected_aud, f"Expected audience '{expected_aud}', got '{payload['aud']}'"

    return payload


def create_user_create_dto(
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False,
    **kwargs,
) -> UserCreate:
    """Create a UserCreate DTO for testing.

    Args:
        username: Username (defaults to random username)
        email: Email (defaults to random email)
        password: Password (defaults to random password)
        is_active: Whether the user is active
        is_superuser: Whether the user is a superuser
        **kwargs: Additional user attributes

    Returns:
        A UserCreate instance
    """
    from app.tests.helpers.test_data import (
        random_username,
        random_email,
        random_password,
    )

    return UserCreate(
        username=username or random_username(),
        email=email or random_email(),
        password=password or random_password(),
        is_active=is_active,
        is_superuser=is_superuser,
        **kwargs,
    )


def create_user_update_dto(
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None,
    **kwargs,
) -> UserUpdate:
    """Create a UserUpdate DTO for testing.

    Args:
        email: New email (optional)
        password: New password (optional)
        is_active: New active status (optional)
        **kwargs: Additional user attributes

    Returns:
        A UserUpdate instance
    """
    data = {}

    if email is not None:
        data["email"] = email
    if password is not None:
        data["password"] = password
    if is_active is not None:
        data["is_active"] = is_active

    data.update(kwargs)
    return UserUpdate(**data)


def assert_user_data(
    user_data: Dict[str, Any],
    expected_data: Dict[str, Any],
    exclude: Optional[List[str]] = None,
) -> None:
    """Assert that user data matches the expected values.

    Args:
        user_data: User data to check
        expected_data: Expected user data
        exclude: List of fields to exclude from comparison

    Raises:
        AssertionError: If any field doesn't match
    """
    if exclude is None:
        exclude = []

    for key, expected_value in expected_data.items():
        if key in exclude:
            continue

        assert key in user_data, f"Missing field: {key}"
        assert user_data[key] == expected_value, f"Expected {key}={expected_value}, got {user_data[key]}"
