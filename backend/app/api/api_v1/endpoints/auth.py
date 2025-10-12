from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user as user_crud
from app.api.deps import get_async_db
from app.core import security
from app.core.config import settings
from app.core.limiter import get_rate_limiter
from app.schemas.user import Token, UserCreate, User

router = APIRouter()


# Initialiser rate_limiter avec une valeur par défaut
rate_limiter = get_rate_limiter()

# Désactiver le rate limiter en environnement de test ou si le cache est désactivé
if settings.ENVIRONMENT == "test" or not settings.CACHE_ENABLED:
    rate_limiter = None

deps = [Depends(rate_limiter)] if rate_limiter else []


@router.post("/login", response_model=Token, dependencies=deps)
async def login(db: AsyncSession = Depends(get_async_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_crud.authenticate_async(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

    # Créer le token de rafraîchissement
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(subject=user.id, expires_delta=refresh_token_expires)

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh", response_model=Token, dependencies=deps)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Refresh access token using a valid refresh token.

    Args:
        refresh_token: The refresh token to validate
        db: Database session

    Returns:
        New access token and refresh token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    # Verify the refresh token
    payload = security.verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = await user_crud.get_async(db, id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = security.create_refresh_token(subject=user.id, expires_delta=refresh_token_expires)

    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, dependencies=deps)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User registration data (username, email, password)
        db: Database session
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if user with this email already exists
    user = await user_crud.get_by_email_async(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Check if user with this username already exists
    user = await user_crud.get_by_username_async(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )
    
    # Create new user
    user = await user_crud.create_async(db, obj_in=user_in)
    return user
