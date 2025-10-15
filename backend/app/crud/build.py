import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.crud.base import CRUDBase
from app.models import Build, Profession, build_profession
import random

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class CRUDBuild(CRUDBase[Build, schemas.BuildCreate, schemas.BuildUpdate]):
    """CRUD operations for Build model with both sync and async support."""

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Build]:
        """Get multiple builds by owner ID (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.created_by_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    async def get_multi_by_owner_async(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.Build]:
        """Get multiple builds by owner ID (asynchronous)."""
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.professions),
                selectinload(self.model.created_by),
            )
            .where(self.model.created_by_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_public_builds(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[models.Build]:
        """Get public builds (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.is_public == True)
            .offset(skip)
            .limit(limit)
        )  # noqa: E712
        return list(db.scalars(stmt).all())

    async def get_public_builds_async(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[models.Build]:
        """Get public builds (asynchronous)."""
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.professions),
                selectinload(self.model.created_by),
            )
            .where(self.model.is_public == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def create_with_owner(
        self, db: Session, *, obj_in: schemas.BuildCreate, owner_id: int
    ) -> Optional[Build]:
        """
        Create a new build with the given owner and profession associations (synchronous).

        Args:
            db: Database session
            obj_in: Build data including profession_ids
            owner_id: ID of the user creating the build

        Returns:
            The created build with associated professions, or None if creation failed
        """
        try:
            logger.info(f"Starting build creation for user {owner_id}")
            logger.info(f"Build data: {obj_in}")

            # Prepare build data
            build_data = obj_in.model_dump()
            profession_ids = build_data.pop("profession_ids", [])

            # Log the profession IDs we're trying to associate
            logger.info(f"Associating profession IDs: {profession_ids}")

            # Verify all professions exist before starting the transaction
            if profession_ids:
                existing_professions = (
                    db.query(Profession).filter(Profession.id.in_(profession_ids)).all()
                )
                existing_ids = {p.id for p in existing_professions}
                missing_ids = set(profession_ids) - existing_ids

                if missing_ids:
                    error_msg = (
                        f"The following profession IDs do not exist: {missing_ids}"
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            # Add required fields
            build_data["created_by_id"] = owner_id
            now = datetime.now(timezone.utc)
            build_data["created_at"] = now
            build_data["updated_at"] = now
            build_data.setdefault("config", {})
            build_data.setdefault("constraints", {})

            # Log the final build data
            logger.info(f"Creating build with data: {build_data}")

            # Create build
            db_obj = Build(**build_data)
            db.add(db_obj)
            db.flush()  # This will generate the build ID

            logger.info(f"Created build with ID: {db_obj.id}")

            # Add profession associations if any
            if profession_ids:
                for prof_id in profession_ids:
                    logger.info(f"Adding profession {prof_id} to build {db_obj.id}")
                    stmt = build_profession.insert().values(
                        build_id=db_obj.id, profession_id=prof_id
                    )
                    db.execute(stmt)

            db.commit()
            db.refresh(db_obj)
            logger.info(f"Successfully created build {db_obj.id}")
            return db_obj

        except Exception as e:
            error_msg = f"Error in create_with_owner: {str(e)}"
            logger.error(error_msg, exc_info=True)
            db.rollback()
            # Re-raise with more context
            raise ValueError(f"Failed to create build: {str(e)}") from e

    async def create_with_owner_async(
        self, db: AsyncSession, *, obj_in: schemas.BuildCreate, owner_id: int
    ) -> Optional[Build]:
        """
        Create a new build with the given owner and profession associations (asynchronous).

        Args:
            db: Async database session
            obj_in: Build data including profession_ids
            owner_id: ID of the user creating the build

        Returns:
            The created build with associated professions, or None if creation failed
        """
        try:
            # Prepare build data
            build_data = obj_in.model_dump()
            profession_ids = build_data.pop("profession_ids", [])

            # Verify all professions exist before starting the transaction
            if profession_ids:
                stmt = select(func.count(Profession.id)).where(
                    Profession.id.in_(profession_ids)
                )
                result = await db.execute(stmt)
                count = result.scalar_one()
                if count != len(set(profession_ids)):
                    # Find which ones are missing for a better error message
                    existing_stmt = select(Profession.id).where(
                        Profession.id.in_(profession_ids)
                    )
                    existing_result = await db.execute(existing_stmt)
                    existing_ids = {r[0] for r in existing_result}
                    missing_ids = set(profession_ids) - existing_ids
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Professions not found: {missing_ids}",
                    )

            # Add required fields
            build_data["created_by_id"] = owner_id
            now = datetime.now(timezone.utc)
            build_data["created_at"] = now
            build_data["updated_at"] = now
            build_data.setdefault("config", {})
            build_data.setdefault("constraints", {})

            # Ensure we have at least one profession
            if not profession_ids:
                logger.warning("No professions available for build generation")
                return schemas.BuildGenerationResponse(
                    success=False,
                    message="No valid professions available for build generation",
                    build=None,
                    suggested_composition=[],
                )

            # Simple round-robin assignment as a starting point
            # Replace this with actual build generation logic
            selected_professions = []
            for i in range(generation_request.team_size):
                selected_professions.append(professions[i % len(professions)])

            # Prepare constraints as a dictionary if they exist
            constraints_dict = (
                generation_request.constraints.dict()
                if hasattr(generation_request.constraints, "dict")
                else {}
            )

            # Create a new build with the generated composition
            build_in = schemas.BuildCreate(
                name=f"Generated Build - {generation_request.team_size} players",
                description=f"Automatically generated build for {generation_request.team_size} players",
                game_mode="wvw",  # Default to WvW for generated builds
                team_size=generation_request.team_size,
                is_public=False,
                config={"generated": True, "constraints": constraints_dict},
                constraints=constraints_dict,
                profession_ids=[p.id for p in selected_professions],
            )

            build = self.create_with_owner(db, obj_in=build_in, owner_id=owner_id)

            # Convert build to dict and update with profession details
            build_dict = {
                "id": build.id,
                "name": build.name,
                "description": build.description,
                "game_mode": build.game_mode,
                "team_size": build.team_size,
                "is_public": build.is_public,
                "owner_id": owner_id,  # Add owner_id to match the schema
                "created_by_id": build.created_by_id,
                "created_at": build.created_at.isoformat(),
                "updated_at": build.updated_at.isoformat(),
                "profession_ids": [p.id for p in selected_professions],
                "professions": [
                    {"id": p.id, "name": p.name, "description": p.description or ""}
                    for p in selected_professions
                ],
                "config": build.config or {},
                "constraints": build.constraints or {},
            }

            # Prepare suggested composition - ensure this is always a list, even if empty
            suggested_composition = []
            for i, prof in enumerate(selected_professions):
                # Determine role based on position or other logic
                role = "DPS"  # Default role
                if i == 0 and generation_request.team_size > 1:
                    role = "Healer"
                elif i == 1 and generation_request.team_size > 2:
                    role = "Support"

                suggested_composition.append(
                    {
                        "position": i + 1,
                        "profession": prof.name,
                        "role": role,
                        "build": f"{prof.name} - {role}",
                        "required_boons": ["Might", "Fury"],
                        "required_utilities": ["CC", "Cleanse"],
                    }
                )

            # Prepare metrics
            metrics = {
                "boon_coverage": {
                    "might": 100.0,
                    "fury": 100.0,
                    "quickness": 50.0,
                    "alacrity": 0.0,
                },
                "role_distribution": {
                    "healer": 1,
                    "support": 1,
                    "dps": (
                        generation_request.team_size - 2
                        if generation_request.team_size > 2
                        else 1
                    ),
                },
                "profession_distribution": {p.name: 1 for p in selected_professions},
            }

            return schemas.BuildGenerationResponse(
                success=True,
                message="Build generated successfully",
                build=build_dict,
                suggested_composition=suggested_composition,
                metrics=metrics,
            )
        except Exception as e:
            return schemas.BuildGenerationResponse(
                success=False,
                message=f"Error generating build: {str(e)}",
                build=None,
                suggested_composition=[],
            )

    def get_with_professions(
        self, db: Session, *, id: int, user_id: Optional[int] = None
    ) -> Optional[models.Build]:
        """Get a build with its professions (synchronous)."""
        stmt = select(self.model).where(self.model.id == id)

        # Check if user has access
        if user_id is not None:
            stmt = stmt.where(
                (self.model.is_public == True) | (self.model.created_by_id == user_id)
            )  # noqa: E712

        stmt = stmt.options(joinedload(self.model.professions))
        return db.scalars(stmt).first()

    async def get_with_professions_async(
        self, db: AsyncSession, *, id: int, user_id: Optional[int] = None
    ) -> Optional[models.Build]:
        """Get a build with its professions (asynchronous)."""
        stmt = select(self.model).where(self.model.id == id)

        # Check if user has access
        if user_id is not None:
            stmt = stmt.where(
                (self.model.is_public == True) | (self.model.created_by_id == user_id)
            )  # noqa: E712

        stmt = stmt.options(joinedload(self.model.professions))
        result = await db.execute(stmt)
        return result.unique().scalars().first()

    def update_with_professions(
        self,
        db: Session,
        *,
        db_obj: Build,
        obj_in: Union[schemas.BuildUpdate, Dict[str, Any]],
        user_id: int,
    ) -> Optional[Build]:
        """
        Update a build with its professions (synchronous).

        Args:
            db: Database session
            db_obj: The build to update
            obj_in: Update data including profession_ids
            user_id: ID of the user performing the update (for authorization)

        Returns:
            The updated build, or None if update failed
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in.copy()
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            # Handle profession updates if needed
            if "profession_ids" in update_data:
                # Remove existing associations
                db.execute(
                    build_profession.delete().where(
                        build_profession.c.build_id == db_obj.id
                    )
                )

                # Add new associations
                for prof_id in update_data.pop("profession_ids", []):
                    # Verify profession exists
                    prof = db.get(Profession, prof_id)
                    if not prof:
                        raise ValueError(f"Profession with ID {prof_id} not found")

                    stmt = build_profession.insert().values(
                        build_id=db_obj.id, profession_id=prof_id
                    )
                    db.execute(stmt)

            # Update other fields
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db_obj.updated_at = datetime.now(timezone.utc)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except Exception as e:
            logger.error(f"Error updating build: {str(e)}", exc_info=True)
            db.rollback()
            return None

    async def update_with_professions_async(
        self,
        db: AsyncSession,
        *,
        db_obj: Build,
        obj_in: Union[schemas.BuildUpdate, Dict[str, Any]],
        user_id: int,
    ) -> Optional[Build]:
        """
        Update a build with its professions (asynchronous).

        Args:
            db: Async database session
            db_obj: The build to update
            obj_in: Update data including profession_ids
            user_id: ID of the user performing the update (for authorization)

        Returns:
            The updated build, or None if update failed
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in.copy()
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            # Handle profession updates if needed
            if "profession_ids" in update_data:
                # Remove existing associations
                await db.execute(
                    build_profession.delete().where(
                        build_profession.c.build_id == db_obj.id
                    )
                )

                # Add new associations
                profession_ids = update_data.pop("profession_ids", [])
                if profession_ids:
                    # Verify all professions exist in a single query
                    stmt = select(Profession.id).where(
                        Profession.id.in_(profession_ids)
                    )
                    result = await db.execute(stmt)
                    existing_ids = {row[0] for row in result.all()}

                    for prof_id in profession_ids:
                        if prof_id not in existing_ids:
                            raise ValueError(f"Profession with ID {prof_id} not found")

                        stmt = build_profession.insert().values(
                            build_id=db_obj.id, profession_id=prof_id
                        )
                        await db.execute(stmt)

            # Update other fields
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db_obj.updated_at = datetime.now(timezone.utc)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

        except Exception as e:
            logger.error(f"Error updating build: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    def generate_build(
        self,
        db: Session,
        *,
        generation_request: schemas.BuildGenerationRequest,
        owner_id: int,
    ) -> Dict[str, Any]:
        """
        Generate a new build based on the provided constraints and preferences.

        Args:
            db: Database session
            generation_request: Build generation request data
            owner_id: ID of the user who owns this build

        Returns:
            Dictionary containing the generated build and composition

        Raises:
            ValueError: If no professions are available for build generation
        """
        try:
            # Get the list of preferred professions
            profession_ids = generation_request.preferred_professions or []
            if not profession_ids:
                # If no preferred professions, get all available ones
                profession_ids = [p.id for p in db.query(Profession).all()]

            if not profession_ids:
                raise ValueError("No professions available for build generation")
            # Create a new build record with default values
            now = datetime.now(timezone.utc)
            build_data = {
                "name": f"Generated Build {now.strftime('%Y%m%d%H%M%S')}",
                "description": "Automatically generated build",
                "game_mode": "wvw",  # Default to WvW for now
                "team_size": generation_request.team_size,
                "is_public": True,
                "created_by_id": owner_id,
                "constraints": generation_request.constraints or {},
                "created_at": now,
                "updated_at": now,  # Explicitly set updated_at to match created_at
            }

            # Create the build in the database
            db_build = self.create(db, obj_in=build_data)

            # Get the list of preferred professions
            profession_ids = generation_request.preferred_professions or []
            if not profession_ids:
                # If no preferred professions, get all available ones
                profession_ids = [p.id for p in db.query(Profession).all()]

            # Ensure we have enough unique professions for the team size
            if len(profession_ids) < generation_request.team_size:
                # If not enough unique professions, allow duplicates
                profession_ids = (
                    profession_ids
                    * (generation_request.team_size // len(profession_ids) + 1)
                )[: generation_request.team_size]

            # Shuffle to randomize the selection
            random.shuffle(profession_ids)

            # Create team composition
            team_size = generation_request.team_size
            composition = []

            # Simple role assignment based on required roles
            required_roles = generation_request.required_roles or []
            role_assignments = {}

            # Assign required roles first
            for i, role in enumerate(required_roles):
                if i < team_size:
                    role_assignments[i] = role

            # Fill remaining slots with generic roles
            for i in range(team_size):
                if i not in role_assignments:
                    role_assignments[i] = "dps"  # Default to DPS

            # Create team members
            for i in range(team_size):
                profession_id = profession_ids[i % len(profession_ids)]
                profession = db.get(Profession, profession_id)

                if not profession:
                    continue

                role = role_assignments.get(i, "dps")

                team_member = {
                    "position": i + 1,
                    "profession": profession.name,
                    "role": role,
                    "build": f"{profession.name} - {role.capitalize()}",
                    "required_boons": ["Might", "Fury"],
                    "required_utilities": ["Stun Break", "Condition Cleanse"],
                }
                composition.append(team_member)

                # Add profession to build if not already added
                if profession not in db_build.professions:
                    db_build.professions.append(profession)

            # Update the build with the selected professions
            db.add(db_build)
            db.commit()
            db.refresh(db_build)

            # Prepare metrics
            metrics = {
                "boon_coverage": {
                    "quickness": 100.0 if "quickness" in required_roles else 0.0,
                    "alacrity": 100.0 if "alacrity" in required_roles else 0.0,
                    "might": 100.0,
                    "fury": 100.0,
                    "protection": 50.0,
                    "regeneration": 50.0,
                },
                "role_distribution": {
                    "healer": sum(
                        1
                        for m in composition
                        if "heal" in m["role"].lower() or "support" in m["role"].lower()
                    ),
                    "dps": sum(1 for m in composition if "dps" in m["role"].lower()),
                    "support": sum(
                        1 for m in composition if "support" in m["role"].lower()
                    ),
                    "utility": 0,  # This would be calculated based on actual utilities
                },
                "profession_distribution": {
                    m["profession"]: sum(
                        1 for x in composition if x["profession"] == m["profession"]
                    )
                    for m in composition
                },
            }

            # Prepare response
            response = {
                "success": True,
                "message": "Build generated successfully",
                "build": db_build,
                "suggested_composition": composition,
                "metrics": metrics,
            }

            return response

        except Exception as e:
            logger.error(f"Error generating build: {str(e)}", exc_info=True)
            db.rollback()
            raise


# Create a singleton instance
build = CRUDBuild(Build)
