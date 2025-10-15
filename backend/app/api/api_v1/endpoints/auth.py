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
from app.schemas.user import Token, UserCreate, User, UserRegister

router = APIRouter()


# Initialiser rate_limiter avec une valeur par défaut
rate_limiter = get_rate_limiter()

# Désactiver le rate limiter en environnement de test ou si le cache est désactivé
if settings.ENVIRONMENT == "test" or not settings.CACHE_ENABLED:
    rate_limiter = None

deps = [Depends(rate_limiter)] if rate_limiter else []


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    This endpoint creates its own database session to avoid FastAPI dependency issues.
    It extracts all needed data before closing the session, then verifies the password.
    """
    from sqlalchemy import select
    from app.models.user import User as UserModel
    from app.db.session import AsyncSessionLocal

    # Create our own session to avoid get_async_db blocking issues
    async with AsyncSessionLocal() as db:
        try:
            # Fetch user by email
            stmt = select(UserModel).where(UserModel.email == form_data.username)
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password",
                )

            # Extract ALL needed data immediately before session closes
            user_id = user.id
            hashed_password = user.hashed_password
            is_active = user.is_active

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    # Session is now closed, verify password with extracted data
    if not security.verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=user_id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister) -> Any:
    """
    Register a new user.

    Creates a new user account with hashed password and returns access/refresh tokens.
    """
    from sqlalchemy import select
    from app.models.user import User as UserModel
    from app.db.session import AsyncSessionLocal

    # Create our own session to avoid dependency issues
    async with AsyncSessionLocal() as db:
        try:
            # Check if user with this email already exists
            stmt = select(UserModel).where(UserModel.email == user_in.email)
            result = await db.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists in the system",
                )

            # Create new user with hashed password
            hashed_password = security.get_password_hash(user_in.password)

            # Generate username from email if not provided
            username = (
                user_in.username if user_in.username else user_in.email.split("@")[0]
            )

            # Create user object
            new_user = UserModel(
                email=user_in.email,
                username=username,
                full_name=user_in.full_name,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=False,
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            # Extract user ID before session closes
            user_id = new_user.id

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}",
            )

    # Session is now closed, create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=user_id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token, dependencies=deps)
async def refresh_token(
    refresh_token: str, db: AsyncSession = Depends(get_async_db)
) -> Any:
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = security.create_refresh_token(
        subject=user.id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
    }


@router.post("/test-simple")
async def test_simple():
    """Simple test endpoint without dependencies."""
    return {"status": "ok", "message": "Auth endpoint working"}


@router.post("/test-login-minimal")
async def test_login_minimal(form_data: OAuth2PasswordRequestForm = Depends()):
    """Minimal login test without database."""
    return {
        "status": "received",
        "username": form_data.username,
        "message": "Form data received successfully",
    }


@router.post("/login-working", response_model=Token)
async def login_working(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Working login endpoint that bypasses get_async_db dependency issue.
    Creates its own database session and runs bcrypt in a thread pool.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from sqlalchemy import select
    from app.models.user import User as UserModel
    from app.db.session import AsyncSessionLocal

    # Create our own session instead of using get_async_db
    async with AsyncSessionLocal() as db:
        try:
            # Fetch user by email
            stmt = select(UserModel).where(UserModel.email == form_data.username)
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password",
                )

            # Extract ALL needed data immediately
            user_id = user.id
            hashed_password = user.hashed_password
            is_active = user.is_active

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    # Session is now closed, verify password in thread pool (bcrypt is CPU-intensive)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        is_valid = await loop.run_in_executor(
            pool, security.verify_password, form_data.password, hashed_password
        )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=user_id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/simple-login")
async def simple_login(
    db: AsyncSession = Depends(get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Simplified login endpoint that works without session issues
    """
    from sqlalchemy import select
    from app.models.user import User as UserModel
    from app.core import security as sec

    # Get user by email
    stmt = select(UserModel).where(UserModel.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Extract data before session closes
    user_id = user.id
    user_email = user.email
    user_username = user.username
    hashed_password = user.hashed_password
    is_active = user.is_active

    # Verify password
    if not sec.verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=user_id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Register a new user.

    Args:
        user_in: User registration data (username, email, password)
        db: Database session

    Returns:
        Created user object as dict

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
    # Convert to dict before session closes
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
