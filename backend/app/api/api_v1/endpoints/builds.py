from typing import Any, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app import models, schemas
from app.crud import build_crud, user_crud
from app.api.deps import get_current_user, get_async_db

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
    "constraints": {"min_healers": 1, "min_dps": 2, "min_support": 1},
    "preferences": {
        "favorite_professions": ["Guardian", "Elementalist"],
        "avoid_duplicates": True,
    },
}

BUILD_CREATE_EXAMPLE = {
    "name": "WvW Zerg Build",
    "description": "Optimal build for WvW zerg fights",
    "is_public": True,
    "config": {
        "weapons": ["Greatsword", "Staff"],
        "traits": ["Dragonhunter", "Zeal", "Radiance"],
        "skills": ["Merciful Intervention", "Sword of Justice"],
    },
    "constraints": {"min_healers": 1, "min_dps": 3, "min_support": 1},
    "profession_ids": [1, 2, 3],  # IDs of associated professions
}

BUILD_UPDATE_EXAMPLE = {
    "name": "Updated WvW Zerg Build",
    "description": "Updated optimal build for WvW zerg fights",
    "is_public": False,
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
                            "created_at": "2025-08-29T14:30:00Z",
                        },
                        "suggested_composition": [
                            {
                                "role": "Healer",
                                "profession": "Guardian",
                                "build": "Firebrand - Heal/Support",
                            },
                            {
                                "role": "DPS",
                                "profession": "Elementalist",
                                "build": "Weaver - Power DPS",
                            },
                        ],
                    }
                }
            },
        },
        400: {"description": "Invalid input or generation constraints"},
        401: {"description": "Not authenticated"},
    },
)
async def generate_build(
    *,
    db: AsyncSession = Depends(get_async_db),
    build_in: schemas.BuildGenerationRequest = Body(
        ...,
        examples={"example": {"value": BUILD_GENERATION_EXAMPLE}},
        description="Build generation parameters including team size, constraints, and preferences",
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
    # Convertir la requête en dict pour la compatibilité
    build_data = build_in.dict()
    build_data["created_by_id"] = current_user.id
    
    # Créer un objet BuildCreate à partir des données générées
    build_create = schemas.BuildCreate(**build_data)
    
    # Créer le build avec les données générées
    db_build = await build_crud.create_with_owner_async(
        db=db, 
        obj_in=build_create, 
        owner_id=current_user.id
    )
    
    # Retourner la réponse formatée
    return {
        "success": True,
        "message": "Build generated successfully",
        "build": db_build,
        "suggested_composition": []  # À implémenter avec la logique de génération
    }


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
        409: {"description": "Build already exists"},
    },
)
async def create_build(
    *,
    db: AsyncSession = Depends(get_async_db),
    build_in: schemas.BuildCreate = Body(
        ...,
        examples={"example": {"value": BUILD_CREATE_EXAMPLE}},
        description="Build data including name, description, and configuration",
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
    logger.info(f"=== Starting build creation for user {current_user.id} ===")
    logger.info(f"Build data: {build_in}")

    try:
        # Create the build with the owner and profession associations
        logger.info("Calling create_with_owner...")
        try:
            logger.info("Calling create_with_owner with data:")
            logger.info(f"- owner_id: {current_user.id}")
            logger.info(f"- build_data: {build_in.model_dump()}")

            # Log current database state before the operation
            logger.info("Current database state before create_with_owner:")
            try:
                prof_count = db.query(models.Profession).count()
                logger.info(f"- Total professions: {prof_count}")

                build_count = db.query(models.Build).count()
                logger.info(f"- Total builds: {build_count}")

                bp_count = db.query(models.BuildProfession).count()
                logger.info(f"- Total build-profession associations: {bp_count}")
            except Exception as db_err:
                logger.error(
                    f"Error querying database state: {str(db_err)}", exc_info=True
                )

            # Call the create_with_owner method
            try:
                existing_build = await build_crud.get_by_name_async(
                    db, name=build_in.name, owner_id=current_user.id
                )

                if existing_build:
                    logger.error(f"Build with name '{build_in.name}' already exists")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Build with this name already exists",
                    )

                db_build = await build_crud.create_with_owner(
                    db=db, obj_in=build_in, owner_id=current_user.id
                )

                # Log the result
                if db_build:
                    logger.info(
                        f"Successfully created build with ID: {getattr(db_build, 'id', 'N/A')}"
                    )
                else:
                    logger.error("create_with_owner returned None")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create build: No build was returned",
                    )

                return db_build

            except ValueError as ve:
                # Handle validation errors with a 400 Bad Request
                logger.error(
                    f"Validation error in create_with_owner: {str(ve)}", exc_info=True
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid build data: {str(ve)}",
                )

            except Exception as e:
                # Log detailed error information
                error_type = type(e).__name__
                error_message = str(e)
                logger.error(
                    f"Unexpected error in create_with_owner: {error_type}: {error_message}",
                    exc_info=True,
                )

                # Re-raise as a 500 error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An error occurred while creating the build: {error_message}",
                )

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions as-is
            logger.error(f"HTTPException in create_with_owner: {str(http_exc)}")
            raise

        except Exception as e:
            # Log detailed error information
            error_type = type(e).__name__
            error_message = str(e)
            logger.error(
                f"Unexpected error in build creation: {error_type}: {error_message}",
                exc_info=True,
            )

            # Log the full traceback to help with debugging
            import traceback

            logger.error(f"Full traceback:\n{traceback.format_exc()}")

            # Raise a 500 error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the build. Please try again later.",
            )

            # Log the build data that caused the error
            try:
                logger.error(
                    f"Build data that caused the error: {build_in.model_dump_json()}"
                )
            except Exception as json_err:
                logger.error(f"Could not serialize build data: {str(json_err)}")

            # Log current database state for debugging
            try:
                logger.info("Current builds in database:")
                builds = db.query(models.Build).all()
                logger.info(f"- Total builds: {len(builds)}")
                for b in builds[:5]:  # Limit to first 5 builds to avoid huge logs
                    logger.info(
                        f"  - Build {b.id}: {b.name} (owner: {getattr(b, 'created_by_id', 'N/A')})"
                    )

                logger.info("Current professions in database:")
                profs = db.query(models.Profession).all()
                logger.info(f"- Total professions: {len(profs)}")
                for p in profs[:5]:  # Limit to first 5 professions
                    logger.info(f"  - Profession {p.id}: {p.name}")

            except Exception as db_err:
                logger.error(
                    f"Error querying database state: {str(db_err)}", exc_info=True
                )

            # Re-raise with a generic error message to avoid leaking internal details
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the build. Please try again.",
            )

        logger.info(f"Successfully created build with ID: {db_build.id}")

        # Explicitly load the build with its professions
        logger.info("Loading build with professions...")
        db_build = build_crud.get_with_professions(
            db=db, id=db_build.id, user_id=current_user.id
        )

        if not db_build:
            logger.error(f"Failed to load build with ID {db_build.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load created build",
            )

        logger.info(
            f"Successfully loaded build with {len(db_build.professions) if hasattr(db_build, 'professions') else 0} professions"
        )

        # Log profession information
        if hasattr(db_build, "professions"):
            logger.info(f"Build professions: {[p.id for p in db_build.professions]}")

        return db_build

    except Exception as e:
        logger.error(f"Error creating build: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create build: {str(e)}",
        )
    if hasattr(db_build, "professions") and db_build.professions:
        logger.info(
            f"Build has {len(db_build.professions)} professions: {[p.id for p in db_build.professions]}"
        )
    else:
        logger.warning("Build has no professions attribute or empty professions list")

    # Create a dictionary with only the fields we want to include in the response
    build_data = {
        "id": db_build.id,
        "name": db_build.name,
        "description": db_build.description or "",
        "game_mode": db_build.game_mode,
        "team_size": db_build.team_size,
        "is_public": db_build.is_public,
        "config": db_build.config or {},
        "constraints": db_build.constraints or {},
        "created_by_id": db_build.created_by_id,
        "created_at": db_build.created_at,
        "updated_at": db_build.updated_at,
        "owner_id": db_build.created_by_id,  # Map created_by_id to owner_id for the schema
    }

    # Get the professions from the build_professions relationship
    if hasattr(db_build, "build_professions"):
        professions = []
        for bp in db_build.build_professions:
            if hasattr(bp, "profession") and bp.profession is not None:
                profession_data = {
                    "id": bp.profession.id,
                    "name": bp.profession.name,
                    "description": bp.profession.description or "",
                }
                professions.append(profession_data)

        build_data["professions"] = professions
        build_data["profession_ids"] = [p["id"] for p in professions]
    else:
        build_data["professions"] = []
        build_data["profession_ids"] = []

    logger.info(f"Build data with professions: {build_data}")

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
        404: {"description": "Build not found"},
    },
)
async def read_build(
    *,
    db: AsyncSession = Depends(get_async_db),
    build_id: int = Path(..., description="The ID of the build to retrieve"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get build by ID.
    """
    build = await build_crud.get_async(db, id=build_id)
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
        404: {"description": "Build not found"},
    },
)
async def update_build(
    *,
    db: AsyncSession = Depends(get_async_db),
    build_id: int = Path(..., description="ID of the build to update"),
    build_in: schemas.BuildUpdate = Body(
        ...,
        examples={"example": {"value": BUILD_UPDATE_EXAMPLE}},
        description="Updated build data",
    ),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a build.

    Only the build owner can update the build. Partial updates are supported.
    """
    build = await build_crud.get_async(db, id=build_id)
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

    return await build_crud.update_async(db=db, db_obj=build, obj_in=update_data)


@router.delete(
    "/{build_id}",
    response_model=schemas.Build,
    responses={
        200: {"description": "Successfully deleted build"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Build not found"},
    },
)
async def delete_build(
    *,
    db: AsyncSession = Depends(get_async_db),
    build_id: int = Path(..., description="The ID of the build to delete"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a build.
    """
    build = await build_crud.get_async(db, id=build_id)
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

    return await build_crud.remove_async(db=db, id=build_id)


@router.get(
    "/",
    response_model=List[schemas.Build],
    responses={
        200: {"description": "Successfully retrieved builds"},
        401: {"description": "Not authenticated"},
    },
)
async def read_builds(
    db: AsyncSession = Depends(get_async_db),
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
    user_builds = await build_crud.get_multi_by_owner_async(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    
    # If we have less than the limit, add public builds
    if len(user_builds) < limit:
        remaining = limit - len(user_builds)
        public_builds = await build_crud.get_public_builds_async(db, skip=0, limit=remaining)
        
        # Filter out builds that are already in user_builds
        public_builds = [
            b for b in public_builds 
            if b.id not in {b.id for b in user_builds}
        ]
        user_builds.extend(public_builds[:remaining])

    return user_builds
