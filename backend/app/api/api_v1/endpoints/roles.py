from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve roles.
    """
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return roles

@router.post("/", response_model=schemas.Role)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new role.
    """
    role = crud.role.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="The role with this name already exists in the system.",
        )
    role = crud.role.create(db, obj_in=role_in)
    return role

@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a role.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this ID does not exist in the system",
        )
    role = crud.role.update(db, db_obj=role, obj_in=role_in)
    return role

@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
    role_id: int,
    db: Session = Depends(deps.get_db),
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
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a role.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this ID does not exist in the system",
        )
    role = crud.role.remove(db, id=role_id)
    return role
