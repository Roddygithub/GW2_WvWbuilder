from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import crud, models, schemas
from app.api import dependencies as deps
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi_async(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email_async(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create_async(db, obj_in=user_in)
    return user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user = await crud.user.update_async(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    # Simply return the current user from the dependency
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Get a specific user by id.
    """
    # Vérifier si l'utilisateur demandé est l'utilisateur actuel
    if current_user.id == user_id:
        return current_user

    # Vérifier si l'utilisateur actuel est un superutilisateur
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user",
        )

    # Récupérer l'utilisateur demandé
    user = await crud.user.get_async(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get_async(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user does not exist in the system",
        )
    user = await crud.user.update_async(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/{user_id}/roles/{role_id}", response_model=schemas.User)
async def add_role_to_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Add a role to a user.
    """
    # Vérifier si l'utilisateur existe
    user = await crud.user.get_async(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Vérifier si le rôle existe
    role = await crud.role.get_async(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Vérifier si l'utilisateur a déjà ce rôle
    if role in user.roles:
        return user

    # Ajouter le rôle à l'utilisateur
    await crud.user.add_role_async(db, user=user, role_id=role_id)
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=schemas.User)
async def remove_role_from_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Remove a role from a user.
    """
    # Vérifier si l'utilisateur existe
    user = await crud.user.get_async(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Vérifier si le rôle existe
    role = await crud.role.get_async(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Vérifier si l'utilisateur a ce rôle
    if role not in user.roles:
        return user

    # Retirer le rôle de l'utilisateur
    await crud.user.remove_role_async(db, user=user, role_id=role_id)
    return user
