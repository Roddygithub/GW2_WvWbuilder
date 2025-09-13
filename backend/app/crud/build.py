import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Type, Generic
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
import traceback

logger = logging.getLogger(__name__)

from app import models, schemas
from app.crud.base import CRUDBase
from app.models.build import Build, BuildProfession
from app.models.profession import Profession

class CRUDBuild(CRUDBase[Build, schemas.BuildCreate, schemas.BuildUpdate]):
    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Build]:
        return (
            db.query(self.model)
            .filter(models.Build.created_by_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_builds(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[models.Build]:
        return (
            db.query(self.model)
            .filter(models.Build.is_public == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, *, obj_in: schemas.BuildCreate, owner_id: int
    ) -> Build:
        logger.info(f"Creating build for owner_id: {owner_id}")
        logger.info(f"Build data: {obj_in.model_dump()}")
        
        # Extract profession_ids if they exist
        profession_ids = getattr(obj_in, 'profession_ids', [])
        logger.info(f"Profession IDs from input: {profession_ids}")
        
        # Create build data without profession_ids
        obj_data = obj_in.model_dump()
        if 'profession_ids' in obj_data:
            del obj_data['profession_ids']
            
        logger.info(f"Creating build with data: {obj_data}")
        
        try:
            # Start a transaction
            with db.begin_nested():
                # Create the build first
                db_obj = Build(**obj_data, created_by_id=owner_id, created_at=func.now(), updated_at=func.now())
                db.add(db_obj)
                db.flush()  # Flush to get the build ID
                
                logger.info(f"Created build with ID: {db_obj.id}")
                
                if profession_ids:
                    # Get the profession objects
                    professions = db.query(models.Profession).filter(
                        models.Profession.id.in_(profession_ids)
                    ).all()
                    
                    if not professions:
                        logger.warning(f"No professions found for IDs: {profession_ids}")
                    else:
                        logger.info(f"Found {len(professions)} professions to associate")
                        
                        # Clear any existing associations first to avoid unique constraint violations
                        db.query(models.BuildProfession).filter(
                            models.BuildProfession.build_id == db_obj.id
                        ).delete(synchronize_session=False)
                        
                        # Create new associations using the relationship
                        for prof in professions:
                            # Create the association object
                            bp = models.BuildProfession(
                                build_id=db_obj.id,
                                profession_id=prof.id
                            )
                            db.add(bp)
                            logger.info(f"Created BuildProfession association: build_id={db_obj.id}, profession_id={prof.id}")
                        
                        # Explicitly flush to catch any constraint violations
                        db.flush()
                        
                        # Set the relationship on the instance
                        db_obj.professions = professions
                        logger.info(f"Set {len(professions)} professions on build")
            
            # Commit the transaction
            db.commit()
            logger.info("Committed transaction")
            
            # Expire the build object to ensure we get fresh data
            db.expire(db_obj)
            
            # Reload the build with all relationships using a fresh query
            db_obj = db.query(Build).options(
                joinedload(Build.build_professions).joinedload(models.BuildProfession.profession),
                joinedload(Build.professions)
            ).filter(Build.id == db_obj.id).first()
            
            if not db_obj:
                raise ValueError("Failed to reload build after creation")
                
            logger.info(f"Reloaded build with {len(db_obj.professions) if hasattr(db_obj, 'professions') else 0} professions")
            
            return db_obj
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in create_with_owner: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def update(
        self,
        db: Session,
        *,
        db_obj: models.Build,
        obj_in: Union[schemas.BuildUpdate, Dict[str, Any]]
    ) -> models.Build:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Handle profession updates
        if "profession_ids" in update_data:
            professions = db.query(models.Profession).filter(
                models.Profession.id.in_(update_data.pop("profession_ids", []))
            ).all()
            db_obj.professions = professions

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def generate_build(
        self,
        db: Session,
        *,
        generation_request: schemas.BuildGenerationRequest,
        owner_id: int
    ) -> schemas.BuildGenerationResponse:
        """
        Generate a build based on the given constraints and preferences.
        This is a placeholder implementation that should be replaced with actual logic.
        """
        try:
            # Get all available professions
            professions = db.query(models.Profession).all()
            
            # Filter by preferred professions if specified
            if generation_request.preferred_professions:
                professions = [
                    p for p in professions 
                    if p.id in generation_request.preferred_professions
                ]
            
            # Ensure we have at least one profession
            if not professions:
                logger.warning("No professions available for build generation")
                return schemas.BuildGenerationResponse(
                    success=False,
                    message="No valid professions available for build generation",
                    build=None,
                    suggested_composition=[]
                )
            
            # Simple round-robin assignment as a starting point
            # Replace this with actual build generation logic
            selected_professions = []
            for i in range(generation_request.team_size):
                selected_professions.append(professions[i % len(professions)])
            
            # Prepare constraints as a dictionary if they exist
            constraints_dict = generation_request.constraints.dict() if hasattr(generation_request.constraints, 'dict') else {}
            
            # Create a new build with the generated composition
            build_in = schemas.BuildCreate(
                name=f"Generated Build - {generation_request.team_size} players",
                description=f"Automatically generated build for {generation_request.team_size} players",
                game_mode="wvw",  # Default to WvW for generated builds
                team_size=generation_request.team_size,
                is_public=False,
                config={"generated": True, "constraints": constraints_dict},
                constraints=constraints_dict,
                profession_ids=[p.id for p in selected_professions]
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
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description or ""
                    }
                    for p in selected_professions
                ],
                "config": build.config or {},
                "constraints": build.constraints or {}
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
                
                suggested_composition.append({
                    "position": i + 1,
                    "profession": prof.name,
                    "role": role,
                    "build": f"{prof.name} - {role}",
                    "required_boons": ["Might", "Fury"],
                    "required_utilities": ["CC", "Cleanse"]
                })
            
            # Prepare metrics
            metrics = {
                "boon_coverage": {
                    "might": 100.0,
                    "fury": 100.0,
                    "quickness": 50.0,
                    "alacrity": 0.0
                },
                "role_distribution": {
                    "healer": 1,
                    "support": 1,
                    "dps": generation_request.team_size - 2 if generation_request.team_size > 2 else 1
                },
                "profession_distribution": {p.name: 1 for p in selected_professions}
            }
            
            return schemas.BuildGenerationResponse(
                success=True,
                message="Build generated successfully",
                build=build_dict,
                suggested_composition=suggested_composition,
                metrics=metrics
            )
            
        except Exception as e:
            return schemas.BuildGenerationResponse(
                success=False,
                message=f"Error generating build: {str(e)}",
                build=None,
                suggested_composition=[]
            )

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        public_only: bool = False
    ) -> List[Build]:
        query = db.query(self.model)
        
        if public_only:
            query = query.filter(Build.is_public == True)  # noqa: E712
        elif user_id is not None:
            query = query.filter((Build.created_by_id == user_id) | (Build.is_public == True))  # noqa: E712
            
        return query.offset(skip).limit(limit).all()
    
    def get_with_professions(
        self, db: Session, *, id: int, user_id: Optional[int] = None
    ) -> Optional[Build]:
        query = db.query(self.model).options(
            joinedload(Build.professions)
        ).filter(Build.id == id)
        
        if user_id is not None:
            query = query.filter(
                (Build.created_by_id == user_id) | (Build.is_public == True)  # noqa: E712
            )
            
        return query.first()
    
    def update_with_professions(
        self, 
        db: Session, 
        *, 
        db_obj: Build, 
        obj_in: Union[schemas.BuildUpdate, Dict[str, Any]],
        user_id: int
    ) -> Build:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        # Handle profession updates
        if "profession_ids" in update_data:
            # Clear existing profession associations
            db.query(BuildProfession).filter(
                BuildProfession.build_id == db_obj.id
            ).delete()
            
            # Add new profession associations
            for prof_id in update_data["profession_ids"]:
                bp = BuildProfession(build_id=db_obj.id, profession_id=prof_id)
                db.add(bp)
                
            del update_data["profession_ids"]
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)


build = CRUDBuild(Build)
