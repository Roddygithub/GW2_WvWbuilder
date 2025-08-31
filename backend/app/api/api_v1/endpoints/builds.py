from typing import Any, List, Dict
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from sqlalchemy.orm import Session, joinedload

from app import crud, models, schemas
from app.api.deps import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["builds"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"},
    },
)

# Example request and response data
BUILD_GENERATION_EXAMPLE = {
    "team_size": 5,
    "game_mode": "WvW",
    "constraints": {
        "min_healers": 1,
        "min_dps": 2,
        "min_support": 1
    },
    "preferences": {
        "favorite_professions": ["Guardian", "Elementalist"],
        "avoid_duplicates": True
    }
}

BUILD_CREATE_EXAMPLE = {
    "name": "WvW Zerg Build",
    "description": "Optimal build for WvW zerg fights",
    "is_public": True,
    "config": {
        "weapons": ["Greatsword", "Staff"],
        "traits": ["Dragonhunter", "Zeal", "Radiance"],
        "skills": ["Merciful Intervention", "Sword of Justice"]
    },
    "constraints": {
        "min_healers": 1,
        "min_dps": 3,
        "min_support": 1
    },
    "profession_ids": [1, 2, 3]  # IDs of associated professions
}

BUILD_UPDATE_EXAMPLE = {
    "name": "Updated WvW Zerg Build",
    "description": "Updated optimal build for WvW zerg fights",
    "is_public": False
}

@router.post(
    "/generate/",
    response_model=schemas.BuildGenerationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successfully generated build",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Build generated successfully",
                        "build": {
                            "id": 1,
                            "name": "Generated WvW Zerg Build",
                            "description": "Auto-generated build for WvW zerg",
                            "is_public": False,
                            "created_by_id": 1,
                            "created_at": "2025-08-29T14:30:00Z"
                        },
                        "suggested_composition": [
                            {
                                "role": "Healer",
                                "profession": "Guardian",
                                "build": "Firebrand - Heal/Support"
                            },
                            {
                                "role": "DPS",
                                "profession": "Elementalist",
                                "build": "Weaver - Power DPS"
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid input or generation constraints"},
        401: {"description": "Not authenticated"}
    }
)
def generate_build(
    *,
    db: Session = Depends(get_db),
    build_in: schemas.BuildGenerationRequest = Body(
        ..., 
        examples={"example": {"value": BUILD_GENERATION_EXAMPLE}},
        description="Build generation parameters including team size, constraints, and preferences"
    ),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Generate a new build based on the given constraints and preferences.
    
    - **team_size**: Number of players in the team (1-50)
    - **game_mode**: Game mode (e.g., 'WvW', 'PvP', 'PvE')
    - **constraints**: Team composition constraints
    - **preferences**: Optional preferences for build generation
    
    Returns a generated build with suggested team composition.
    """
    return crud.build.generate_build(
        db=db,
        generation_request=build_in,
        owner_id=current_user.id,
    )

@router.post(
    "/",
    response_model=schemas.Build,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Successfully created build"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Profession not found"},
        409: {"description": "Build already exists"}
    }
)
def create_build(
    *,
    db: Session = Depends(get_db),
    build_in: schemas.BuildCreate = Body(
        ...,
        examples={"example": {"value": BUILD_CREATE_EXAMPLE}},
        description="Build data including name, description, and configuration"
    ),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create a new build.
    
    - **name**: Name of the build (required)
    - **description**: Detailed description (optional)
    - **is_public**: Whether the build is visible to others
    - **config**: Build configuration (weapons, traits, skills)
    - **constraints**: Team composition constraints
    - **profession_ids**: List of associated profession IDs
    """
    # Log the build creation request
    logger.info(f"Creating build with data: {build_in}")
    
    # Create the build with the owner and profession associations
    db_build = crud.build.create_with_owner(
        db=db, obj_in=build_in, owner_id=current_user.id
    )
    
    # Ensure the build was created
    if not db_build:
        logger.error("Failed to create build")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create build"
        )
    
    # Log the created build
    logger.info(f"Created build with ID: {db_build.id}")
    
    # Query the build with all relationships loaded
    db_build = (
        db.query(models.Build)
        .options(
            joinedload(models.Build.build_professions)
            .joinedload(models.BuildProfession.profession),
            joinedload(models.Build.professions)
        )
        .filter(models.Build.id == db_build.id)
        .first()
    )
    
    # Log the loaded build
    logger.info(f"Loaded build from DB: {db_build}")
    
    # Log the build's professions
    if hasattr(db_build, 'professions'):
        logger.info(f"Build has {len(db_build.professions)} professions: {[p.id for p in db_build.professions]}")
    else:
        logger.warning("Build has no professions attribute")
    
    # Create a dictionary with only the fields we want to include in the response
    build_data = {
        'id': db_build.id,
        'name': db_build.name,
        'description': db_build.description or "",
        'game_mode': db_build.game_mode,
        'team_size': db_build.team_size,
        'is_public': db_build.is_public,
        'config': db_build.config or {},
        'constraints': db_build.constraints or {},
        'created_by_id': db_build.created_by_id,
        'created_at': db_build.created_at,
        'updated_at': db_build.updated_at,
        'owner_id': db_build.created_by_id,  # Map created_by_id to owner_id for the schema
        'professions': [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description or ""
            }
            for p in db_build.professions
        ] if hasattr(db_build, 'professions') and db_build.professions else [],
        'profession_ids': [p.id for p in db_build.professions] if hasattr(db_build, 'professions') and db_build.professions else []
    }
    
    # Log the built data for debugging
    logger.info(f"Build data to be serialized: {build_data}")
    
    # Convert to Pydantic model for validation and serialization
    build_schema = schemas.Build.model_validate(build_data)
    
    # Log the final response data
    logger.info(f"Returning build with {len(build_schema.professions)} professions")
    
    return build_schema

@router.get(
    "/{build_id}",
    response_model=schemas.Build,
    responses={
        200: {"description": "Successfully retrieved build"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Build not found"}
    }
)
def read_build(
    *,
    db: Session = Depends(get_db),
    build_id: int = Path(..., description="The ID of the build to retrieve"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get build by ID.
    """
    build = crud.build.get(db, id=build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Build not found",
        )
    
    # Only allow access to owner or public builds
    if build.created_by_id != current_user.id and not build.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return build

@router.put(
    "/{build_id}",
    response_model=schemas.Build,
    responses={
        200: {"description": "Successfully updated build"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Build not found"}
    }
)
def update_build(
    *,
    db: Session = Depends(get_db),
    build_id: int = Path(..., description="ID of the build to update"),
    build_in: schemas.BuildUpdate = Body(
        ...,
        examples={"example": {"value": BUILD_UPDATE_EXAMPLE}},
        description="Updated build data"
    ),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a build.
    
    Only the build owner can update the build. Partial updates are supported.
    """
    build = crud.build.get(db, id=build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Build not found",
        )
    
    # Only allow owner to update
    if build.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return crud.build.update(db, db_obj=build, obj_in=build_in)

@router.delete(
    "/{build_id}",
    response_model=schemas.Build,
    responses={
        200: {"description": "Successfully deleted build"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Build not found"}
    }
)
def delete_build(
    *,
    db: Session = Depends(get_db),
    build_id: int = Path(..., description="The ID of the build to delete"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a build.
    """
    build = crud.build.get(db, id=build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Build not found",
        )
    
    # Only allow owner to delete
    if build.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return crud.build.remove(db, id=build_id)

@router.get(
    "/",
    response_model=List[schemas.Build],
    response_model_exclude_none=True,
    responses={
        200: {"description": "Successfully retrieved builds"},
        401: {"description": "Not authenticated"}
    }
)
def read_builds(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=100, description="Maximum number of records to return"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve builds.
    
    Returns a list of builds including:
    - All builds owned by the current user
    - Public builds from other users
    
    Results are paginated using skip and limit parameters.
    """
    # Get user's builds
    user_builds = crud.build.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    
    # If we have less than the limit, add public builds
    if len(user_builds) < limit:
        remaining = limit - len(user_builds)
        public_builds = crud.build.get_public_builds(
            db, skip=0, limit=remaining
        )
        # Filter out builds that are already in user_builds
        public_builds = [b for b in public_builds if b.id not in {b.id for b in user_builds}]
        user_builds.extend(public_builds)
    
    return user_builds
