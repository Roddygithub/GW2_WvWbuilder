from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import dependencies as deps
from app.core.exceptions import NotFoundException

router = APIRouter()


# Profession endpoints
@router.get("/", response_model=List[schemas.Profession])
async def read_professions(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve professions.
    """
    professions = await crud.profession.get_multi(db, skip=skip, limit=limit)
    return professions


@router.post("/", response_model=schemas.Profession)
async def create_profession(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    profession_in: schemas.ProfessionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new profession.
    """
    profession = await crud.profession.get_by_name(db, name=profession_in.name)
    if profession:
        raise HTTPException(
            status_code=400,
            detail="The profession with this name already exists in the system.",
        )
    profession = await crud.profession.create(db, obj_in=profession_in)
    return profession


@router.get("/{profession_id}", response_model=schemas.Profession)
async def read_profession(
    profession_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Get profession by ID.
    """
    profession = await crud.profession.get(db, id=profession_id)
    if not profession:
        raise NotFoundException(
            detail="The profession with this ID does not exist in the system"
        )
    return profession


@router.put("/{profession_id}", response_model=schemas.Profession)
async def update_profession(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    profession_id: int,
    profession_in: schemas.ProfessionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a profession.
    """
    profession = await crud.profession.get(db, id=profession_id)
    if not profession:
        raise NotFoundException(
            detail="The profession with this ID does not exist in the system"
        )
    profession = await crud.profession.update(
        db, db_obj=profession, obj_in=profession_in
    )
    return profession


@router.delete("/{profession_id}", response_model=schemas.Profession)
async def delete_profession(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    profession_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a profession.
    """
    profession = await crud.profession.get(db, id=profession_id)
    if not profession:
        raise NotFoundException(
            detail="The profession with this ID does not exist in the system"
        )
    profession = await crud.profession.remove(db, id=profession_id)
    return profession


# Elite Specialization endpoints
@router.get("/elite-specializations/", response_model=List[schemas.EliteSpecialization])
async def read_elite_specializations(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    profession_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve elite specializations, optionally filtered by profession and active status.

    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (for pagination)
    - profession_id: Filter by profession ID
    - is_active: Filter by active status (true/false)
    """
    filters = {}
    if profession_id is not None:
        filters["profession_id"] = profession_id
    if is_active is not None:
        filters["is_active"] = is_active

    elite_specializations = await crud.elite_specialization.get_multi(
        db, skip=skip, limit=limit, **filters
    )
    return elite_specializations


@router.post(
    "/elite-specializations/",
    response_model=schemas.EliteSpecialization,
    status_code=201,
)
async def create_elite_specialization(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    elite_specialization_in: schemas.EliteSpecializationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new elite specialization.

    Required fields:
    - name: Name of the elite specialization (2-50 characters)
    - profession_id: ID of the parent profession
    - weapon_type: Type of weapon added by this specialization

    Optional fields:
    - description: Detailed description
    - icon_url: URL of the specialization icon
    - background_url: URL of the background image
    - is_active: Whether the specialization is currently available (default: true)
    """
    # Check if profession exists
    profession = await crud.profession.get(db, id=elite_specialization_in.profession_id)
    if not profession:
        raise NotFoundException(
            detail="The profession with this ID does not exist in the system"
        )

    # Check if elite specialization with this name already exists for this profession
    elite_spec = await crud.elite_specialization.get_by_name_and_profession_async(
        db,
        name=elite_specialization_in.name,
        profession_id=elite_specialization_in.profession_id,
    )

    if elite_spec:
        raise HTTPException(
            status_code=400,
            detail="An elite specialization with this name already exists for this profession.",
        )

    # Create the new elite specialization
    elite_spec = await crud.elite_specialization.create(
        db, obj_in=elite_specialization_in
    )
    await db.refresh(elite_spec)
    return elite_spec


@router.get(
    "/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization
)
async def read_elite_specialization(
    elite_spec_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Get elite specialization by ID.
    """
    elite_spec = await crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_spec:
        raise NotFoundException(detail="Elite specialization not found")
    return elite_spec


@router.put(
    "/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization
)
async def update_elite_specialization(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    elite_spec_id: int,
    elite_spec_in: schemas.EliteSpecializationUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an elite specialization.

    All fields are optional. Only provided fields will be updated.
    """
    # Get the existing elite specialization
    elite_spec = await crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_spec:
        raise NotFoundException(detail="Elite specialization not found")

    # Check if profession exists if being updated
    if elite_spec_in.profession_id is not None:
        profession = await crud.profession.get(db, id=elite_spec_in.profession_id)
        if not profession:
            raise NotFoundException(
                detail="The profession with this ID does not exist in the system"
            )

    # Check if name is being updated and if it already exists for this profession
    if elite_spec_in.name is not None and elite_spec_in.name != elite_spec.name:
        existing_spec = (
            await crud.elite_specialization.get_by_name_and_profession_async(
                db,
                name=elite_spec_in.name,
                profession_id=elite_spec_in.profession_id or elite_spec.profession_id,
            )
        )
        if existing_spec and existing_spec.id != elite_spec_id:
            raise HTTPException(
                status_code=400,
                detail="An elite specialization with this name already exists for this profession.",
            )

    # Update the elite specialization
    elite_spec = await crud.elite_specialization.update(
        db, db_obj=elite_spec, obj_in=elite_spec_in
    )
    await db.refresh(elite_spec)
    return elite_spec


@router.delete(
    "/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization
)
async def delete_elite_specialization(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    elite_spec_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an elite specialization.

    This is a soft delete that sets is_active to False.
    The record remains in the database for historical purposes.
    """
    elite_spec = await crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_spec:
        raise NotFoundException(detail="Elite specialization not found")

    # Soft delete by setting is_active to False
    if elite_spec.is_active:
        elite_spec = await crud.elite_specialization.update(
            db,
            db_obj=elite_spec,
            obj_in=schemas.EliteSpecializationUpdate(is_active=False),
        )
        await db.refresh(elite_spec)

    return elite_spec
