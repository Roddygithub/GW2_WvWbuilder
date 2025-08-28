from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

# Profession endpoints
@router.get("/", response_model=List[schemas.Profession])
def read_professions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve professions.
    """
    professions = crud.profession.get_multi(db, skip=skip, limit=limit)
    return professions

@router.post("/", response_model=schemas.Profession)
def create_profession(
    *,
    db: Session = Depends(deps.get_db),
    profession_in: schemas.ProfessionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new profession.
    """
    profession = crud.profession.get_by_name(db, name=profession_in.name)
    if profession:
        raise HTTPException(
            status_code=400,
            detail="The profession with this name already exists in the system.",
        )
    profession = crud.profession.create(db, obj_in=profession_in)
    return profession

@router.get("/{profession_id}", response_model=schemas.Profession)
def read_profession(
    profession_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get profession by ID.
    """
    profession = crud.profession.get(db, id=profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="The profession with this ID does not exist in the system",
        )
    return profession

@router.put("/{profession_id}", response_model=schemas.Profession)
def update_profession(
    *,
    db: Session = Depends(deps.get_db),
    profession_id: int,
    profession_in: schemas.ProfessionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a profession.
    """
    profession = crud.profession.get(db, id=profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="The profession with this ID does not exist in the system",
        )
    profession = crud.profession.update(db, db_obj=profession, obj_in=profession_in)
    return profession

@router.delete("/{profession_id}", response_model=schemas.Profession)
def delete_profession(
    *,
    db: Session = Depends(deps.get_db),
    profession_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a profession.
    """
    profession = crud.profession.get(db, id=profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="The profession with this ID does not exist in the system",
        )
    profession = crud.profession.remove(db, id=profession_id)
    return profession

# Elite Specialization endpoints
@router.get("/elite-specializations/", response_model=List[schemas.EliteSpecialization])
def read_elite_specializations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    profession_id: Optional[int] = None,
) -> Any:
    """
    Retrieve elite specializations, optionally filtered by profession.
    """
    filters = {}
    if profession_id is not None:
        filters["profession_id"] = profession_id
    
    elite_specializations = crud.elite_specialization.get_multi(
        db, skip=skip, limit=limit, **filters
    )
    return elite_specializations

@router.post("/elite-specializations/", response_model=schemas.EliteSpecialization)
def create_elite_specialization(
    *,
    db: Session = Depends(deps.get_db),
    elite_specialization_in: schemas.EliteSpecializationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new elite specialization.
    """
    # Check if profession exists
    profession = crud.profession.get(db, id=elite_specialization_in.profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="The profession with this ID does not exist in the system",
        )
    
    # Check if elite specialization with this name already exists for this profession
    elite_specialization = crud.elite_specialization.get_by_name_and_profession(
        db, 
        name=elite_specialization_in.name, 
        profession_id=elite_specialization_in.profession_id
    )
    if elite_specialization:
        raise HTTPException(
            status_code=400,
            detail="The elite specialization with this name already exists for this profession.",
        )
    
    elite_specialization = crud.elite_specialization.create(db, obj_in=elite_specialization_in)
    return elite_specialization

@router.get("/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization)
def read_elite_specialization(
    elite_spec_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get elite specialization by ID.
    """
    elite_specialization = crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_specialization:
        raise HTTPException(
            status_code=404,
            detail="The elite specialization with this ID does not exist in the system",
        )
    return elite_specialization

@router.put("/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization)
def update_elite_specialization(
    *,
    db: Session = Depends(deps.get_db),
    elite_spec_id: int,
    elite_spec_in: schemas.EliteSpecializationUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an elite specialization.
    """
    elite_specialization = crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_specialization:
        raise HTTPException(
            status_code=404,
            detail="The elite specialization with this ID does not exist in the system",
        )
    
    # If profession_id is being updated, check if the new profession exists
    if elite_spec_in.profession_id is not None:
        profession = crud.profession.get(db, id=elite_spec_in.profession_id)
        if not profession:
            raise HTTPException(
                status_code=404,
                detail="The profession with this ID does not exist in the system",
            )
    
    elite_specialization = crud.elite_specialization.update(
        db, db_obj=elite_specialization, obj_in=elite_spec_in
    )
    return elite_specialization

@router.delete("/elite-specializations/{elite_spec_id}", response_model=schemas.EliteSpecialization)
def delete_elite_specialization(
    *,
    db: Session = Depends(deps.get_db),
    elite_spec_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an elite specialization.
    """
    elite_specialization = crud.elite_specialization.get(db, id=elite_spec_id)
    if not elite_specialization:
        raise HTTPException(
            status_code=404,
            detail="The elite specialization with this ID does not exist in the system",
        )
    elite_specialization = crud.elite_specialization.remove(db, id=elite_spec_id)
    return elite_specialization
