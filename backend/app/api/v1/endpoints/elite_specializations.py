"""Elite Specialization API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app import crud, models, schemas
from app.api import deps
from app.schemas.elite_specialization import (
    GameMode,
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[schemas.EliteSpecialization])
async def get_elite_specs(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[schemas.EliteSpecialization]:
    """Get all elite specializations."""
    return await crud.elite_spec_crud.get_multi_async(db, skip=skip, limit=limit)


@router.post(
    "/", response_model=schemas.EliteSpecialization, status_code=status.HTTP_201_CREATED
)
async def create_elite_spec(
    elite_spec_in: EliteSpecializationCreate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> schemas.EliteSpecialization:
    """Create a new elite specialization."""
    return await crud.elite_spec_crud.create_async(db, obj_in=elite_spec_in)


@router.get("/{elite_spec_id}", response_model=schemas.EliteSpecialization)
async def get_elite_spec(
    elite_spec_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> schemas.EliteSpecialization:
    """Get an elite spec by ID."""
    elite_spec = await crud.elite_spec_crud.get_async(db, id=elite_spec_id)
    if not elite_spec:
        raise HTTPException(status_code=404, detail="Elite specialization not found")
    return elite_spec


@router.put("/{elite_spec_id}", response_model=schemas.EliteSpecialization)
async def update_elite_spec(
    elite_spec_id: int,
    elite_spec_in: EliteSpecializationUpdate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> schemas.EliteSpecialization:
    """Update an elite specialization."""
    elite_spec = await crud.elite_spec_crud.get_async(db, id=elite_spec_id)
    if not elite_spec:
        raise HTTPException(status_code=404, detail="Elite specialization not found")
    return await crud.elite_spec_crud.update_async(
        db, db_obj=elite_spec, obj_in=elite_spec_in
    )


@router.delete("/{elite_spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_elite_spec(
    elite_spec_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> None:
    """Delete an elite specialization."""
    elite_spec = await crud.elite_spec_crud.get_async(db, id=elite_spec_id)
    if not elite_spec:
        raise HTTPException(status_code=404, detail="Elite specialization not found")
    await crud.elite_spec_crud.remove_async(db, id=elite_spec_id)
    return None


@router.get(
    "/by-profession/{profession_id}", response_model=list[schemas.EliteSpecialization]
)
async def get_elite_specs_by_profession(
    profession_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[schemas.EliteSpecialization]:
    """Get elite specs by profession ID."""
    return await crud.elite_spec_crud.get_by_profession_async(db, profession_id=profession_id)


@router.get(
    "/by-game-mode/{game_mode}", response_model=list[schemas.EliteSpecialization]
)
async def get_elite_specs_by_game_mode(
    game_mode: GameMode,
    profession_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[schemas.EliteSpecialization]:
    """Get elite specializations by game mode and optional profession."""
    return await crud.elite_spec_crud.get_viable_for_game_mode(
        db, game_mode=game_mode, profession_id=profession_id
    )
