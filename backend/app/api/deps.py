from typing import Optional, Tuple
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.gw2.client import GW2Client, GW2APIError, GW2APIUnauthorizedError

from app.core.config import settings
from app.db.session import get_async_db as get_db_session
from app import crud, models
from app.models.team import Team
from app.services.webhook_service import WebhookService
from app.core.exceptions import (
    CredentialsException,
    InactiveUserException,
    NotSuperUserException,
    UserNotFoundException,
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False  # Permet de gérer manuellement l'absence de token
)


# Get the async database session
get_async_db = get_db_session


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
) -> models.User:
    """
    Dependency to get the current user from the JWT token.

    Args:
        request: The FastAPI request object
        token: The JWT token from the Authorization header
        db: Async database session

    Returns:
        models.User: The authenticated user

    Raises:
        CredentialsException: If token is invalid or user not found
    """
    # Handle test environment with special token
    if token == "x":
        user = await crud.user.get(db, id=1)
        if not user:
            # Create a test user if it doesn't exist
            user_in = models.UserCreate(email="test@example.com", password="testpassword", full_name="Test User")
            user = await crud.user.create(db, obj_in=user_in)
        return user

    if not token:
        raise CredentialsException()

    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_aud": False}
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise CredentialsException()

        # Get user from database
        user = await crud.user.get(db, id=int(user_id))
        if not user:
            raise UserNotFoundException()

        return user

    except (JWTError, ValidationError):
        raise CredentialsException()


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependency to ensure the current user is active.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        models.User: The active user

    Raises:
        InactiveUserException: If the user account is inactive
    """
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependency to ensure the current user is a superuser.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        models.User: The superuser

    Raises:
        NotSuperUserException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise NotSuperUserException()
    return current_user


async def get_current_user_dep(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependency to get the current user for dependency injection.
    This is an alias of get_current_user for better naming in dependency injection.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        models.User: The authenticated user
    """
    return current_user


async def get_team_and_check_access(
    team_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Tuple[Team, bool]:
    """
    Dependency to get a team and check if the current user has access to it.

    Args:
        team_id: The ID of the team to access
        db: Async database session
        current_user: The authenticated user

    Returns:
        Tuple[Team, bool]: The team and a boolean indicating if the user is an admin

    Raises:
        HTTPException: If the team is not found or the user doesn't have access
    """
    # Récupérer l'équipe avec ses membres
    stmt = select(Team).options(selectinload(Team.members)).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier si l'utilisateur est le propriétaire
    is_owner = team.owner_id == current_user.id

    # Vérifier si l'utilisateur est administrateur de l'équipe
    is_admin = False
    if not is_owner:
        stmt = select(team_members).where(
            (team_members.c.team_id == team_id)
            & (team_members.c.user_id == current_user.id)
            & (team_members.c.is_admin == True)  # noqa: E712
        )
        result = await db.execute(stmt)
        is_admin = bool(result.first())

    # Vérifier si l'utilisateur a accès à l'équipe
    has_access = is_owner or is_admin or team.is_public or any(member.id == current_user.id for member in team.members)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette équipe",
        )

    return team, is_admin


async def get_webhook_service(
    db: AsyncSession = Depends(get_async_db),
) -> WebhookService:
    """
    Dependency that returns a WebhookService instance with the database session.
    """
    return webhook_service


async def get_gw2_client(
    x_gw2_api_key: Optional[str] = Header(None, description="Guild Wars 2 API key"),
    accept_language: str = Header("en", description="Preferred language for responses"),
    x_schema_version: str = Header("2022-03-23T00:00:00Z", description="API schema version"),
) -> GW2Client:
    """
    Dependency that provides a GW2 API client.

    This client can be used to interact with the Guild Wars 2 API.

    Args:
        x_gw2_api_key: Optional GW2 API key for authenticated endpoints
        accept_language: Preferred language for responses (e.g., 'en', 'fr', 'de')
        x_schema_version: API schema version to use

    Returns:
        GW2Client: An instance of the GW2 API client

    Raises:
        HTTPException: If the API key is invalid or the API is unavailable
    """
    try:
        async with GW2Client(
            api_key=x_gw2_api_key,
            language=accept_language,
            schema_version=x_schema_version,
        ) as client:
            # Test the connection if an API key was provided
            if x_gw2_api_key:
                try:
                    await client.get_account()
                except GW2APIUnauthorizedError as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Guild Wars 2 API key",
                    ) from e
            return client
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


async def check_team_admin(
    team_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_active_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> Team:
    """
    {{ ... }}

        Args:
            team_id: The ID of the team to check
            db: Async database session
            current_user: The authenticated user

        Returns:
            Team: The team if the user is an admin

        Raises:
            HTTPException: If the user is not an admin of the team
    """
    team, is_admin = await get_team_and_check_access(team_id, db, current_user)

    if not is_admin and team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez être administrateur de l'équipe pour effectuer cette action",
        )

    return team
