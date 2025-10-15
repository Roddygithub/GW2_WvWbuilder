from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.db.dependencies import get_db
from app.schemas.token import TokenPayload


def create_access_token(
    subject: Union[str, int], expires_delta: timedelta = None, **kwargs
) -> str:
    """
    Crée un token JWT d'accès.

    Args:
        subject: Le sujet du token (ID de l'utilisateur)
        expires_delta: Durée de validité du token
        **kwargs: Données supplémentaires à inclure dans le token

    Returns:
        str: Le token JWT encodé

    Raises:
        ValueError: Si le subject est None ou vide
    """
    if subject is None:
        raise ValueError("Subject cannot be None")
    if not str(subject).strip():
        raise ValueError("Subject cannot be empty")

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Utiliser l'ID de l'utilisateur comme sujet et inclure les données supplémentaires
    # Convertir l'expiration en timestamp pour la compatibilité avec TokenPayload
    to_encode = {"exp": int(expire.timestamp()), "sub": str(subject), **kwargs}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int], expires_delta: timedelta = None, **kwargs
) -> str:
    """
    Crée un token de rafraîchissement JWT.

    Args:
        subject: Le sujet du token (ID de l'utilisateur)
        expires_delta: Durée de validité du token (par défaut: settings.REFRESH_TOKEN_EXPIRE_DAYS)
        **kwargs: Données supplémentaires à inclure dans le token

    Returns:
        str: Le token JWT encodé

    Raises:
        ValueError: Si le subject est None ou vide
    """
    if subject is None:
        raise ValueError("Subject cannot be None")
    if not str(subject).strip():
        raise ValueError("Subject cannot be empty")

    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(subject, expires_delta, **kwargs)


def verify_token(token: str) -> Dict[str, Any]:
    """
    Vérifie et décode un token JWT.

    Args:
        token: Le token JWT à vérifier

    Returns:
        Dict[str, Any]: Les données décodées du token

    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        token_data = TokenPayload(**payload)
        return token_data.dict()
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de valider les informations d'identification",
        ) from e


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Vérifie et décode un token de rafraîchissement JWT.

    Args:
        token: Le token JWT à vérifier

    Returns:
        Dict[str, Any]: Les données décodées du token

    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        # Convertir le timestamp en datetime pour la validation
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Vérifier si le token est expiré
        if exp_datetime < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Créer le TokenPayload avec les données décodées
        token_data = TokenPayload(
            sub=payload["sub"],
            exp=exp_datetime,
            iat=payload.get("iat"),
            jti=payload.get("jti"),
        )

        return token_data.dict()
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de valider les informations d'identification",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract the JWT token from the request.

    The token can be provided in:
    - The Authorization header (Bearer token) - case insensitive
    - A cookie named 'access_token'
    - The query parameter 'token'

    Args:
        request: The incoming request

    Returns:
        Optional[str]: The extracted token or None if not found
    """
    # Check Authorization header (case insensitive)
    auth_header = next(
        (v for k, v in request.headers.items() if k.lower() == "authorization"), None
    )
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return token

    # Check cookie
    token = request.cookies.get("access_token")
    if token:
        return token

    # Check query parameter
    token = request.query_params.get("token")
    return token


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Get the current authenticated user from the JWT token.
    The token subject should be the user's ID.

    Creates its own database session to avoid FastAPI dependency blocking issues.

    Args:
        token: Token JWT

    Returns:
        models.User: L'utilisateur authentifié

    Raises:
        HTTPException: Si les informations d'identification sont invalides
    """
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        token_data = TokenPayload(**payload)
        user_id = token_data.sub

        if user_id is None:
            raise credentials_exception

    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from e

    # Create our own session to avoid blocking
    async with AsyncSessionLocal() as db:
        # Get user from database
        stmt = select(models.User).where(models.User.id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise credentials_exception

        # Extract all needed data immediately before session closes
        # This prevents DetachedInstanceError
        _ = user.id
        _ = user.email
        _ = user.username
        _ = user.is_active
        _ = user.is_superuser
        _ = user.full_name
        _ = user.created_at
        _ = user.updated_at

    # Session is now closed, but user object attributes are loaded
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
