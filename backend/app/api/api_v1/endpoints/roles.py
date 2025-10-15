from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[schemas.Role])
async def read_roles(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve roles.
    """
    roles = await crud.role.get_multi(db, skip=skip, limit=limit)
    return roles


@router.post("/", response_model=schemas.Role)
async def create_role(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new role.
    """
    role = await crud.role.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="The role with this name already exists in the system.",
        )
    role = await crud.role.create(db, obj_in=role_in)
    return role


@router.put("/{role_id}", response_model=schemas.Role)
async def update_role(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    role_id: int,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a role.
    """
    role = await crud.role.get(db, id=role_id)
    if not role:
        raise NotFoundException(
            detail="The role with this id does not exist in the system"
        )
    role = await crud.role.update(db, db_obj=role, obj_in=role_in)
    return role


@router.get("/{role_id}", response_model=schemas.Role)
async def read_role(
    role_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Get role by ID.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this ID does not exist in the system",
        )
    return role


@router.delete("/{role_id}", response_model=schemas.Role)
async def delete_role(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a role.
    """
    role = await crud.role.get(db, id=role_id)
    if not role:
        raise NotFoundException(
            detail="The role with this id does not exist in the system"
        )
    role = await crud.role.remove(db, id=role_id)
    return role
