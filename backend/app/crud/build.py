import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Type, Generic
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
import traceback

logger = logging.getLogger(__name__)

from app import models, schemas
from app.crud.base import CRUDBase
from app.models import Build, BuildProfession, Profession

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
    ) -> Optional[Build]:
        """Create a new build with the given owner and profession associations.
        
        Args:
            db: Database session
            obj_in: Build data including profession_ids
            owner_id: ID of the user creating the build
            
        Returns:
            The created build with associated professions, or None if creation failed
        """
        logger.info("\n" + "="*80)
        logger.info(f"=== START: create_with_owner for owner_id: {owner_id} ===")
        logger.info(f"Input data: {obj_in.model_dump()}")
        
        try:
            # Log current transaction state
            logger.info(f"\n[1/5] Current transaction state:")
            logger.info(f"- In transaction: {db.in_transaction()}")
            logger.info(f"- Is active: {db.is_active}")
            
            # Prepare build data
            logger.info("\n[2/5] Preparing build data...")
            build_data = obj_in.model_dump()
            profession_ids = build_data.pop('profession_ids', [])
            logger.info(f"Extracted profession_ids: {profession_ids}")
            
            # Add required fields
            build_data['created_by_id'] = owner_id
            now = func.now()
            build_data['created_at'] = now
            build_data['updated_at'] = now
            build_data.setdefault('config', {})
            build_data.setdefault('constraints', {})
            
            logger.info(f"Final build data: {build_data}")
            
            # Log current database state
            logger.info("\n[3/5] Current database state:")
            try:
                prof_count = db.query(Profession).count()
                logger.info(f"Total professions in database: {prof_count}")
                for i, prof in enumerate(db.query(Profession).all()[:5], 1):  # Limit to first 5
                    logger.info(f"  {i}. Profession(id={prof.id}, name='{prof.name}')")
                
                build_count = db.query(Build).count()
                logger.info(f"Total builds in database: {build_count}")
                
                bp_count = db.query(BuildProfession).count()
                logger.info(f"Total build-profession associations: {bp_count}")
                
                # Log the actual profession IDs we're trying to associate with
                if profession_ids:
                    logger.info("\nVerifying requested profession IDs exist in database:")
                    for prof_id in profession_ids:
                        exists = db.query(Profession).filter(Profession.id == prof_id).first() is not None
                        logger.info(f"  - Profession ID {prof_id}: {'FOUND' if exists else 'NOT FOUND'}")
                        
            except Exception as db_err:
                logger.error(f"Error querying database state: {str(db_err)}", exc_info=True)
            
            # Don't start a new transaction if one is already active
            in_transaction = db.in_transaction()
            logger.info(f"\n[3/5] Transaction status: {'Already in a transaction' if in_transaction else 'No active transaction'}")
            
            try:
                # Create build
                logger.info("\n[4/5] Creating build record...")
                logger.info(f"Creating Build with data: {build_data}")
                db_obj = Build(**build_data)
                logger.info(f"Build object created (not yet persisted): {db_obj}")
                
                db.add(db_obj)
                logger.info("Build object added to session")
                
                db.flush()
                logger.info(f"Build record flushed to database. Assigned ID: {db_obj.id}")
                
                # Add profession associations if any
                if profession_ids:
                    logger.info(f"\nAdding {len(profession_ids)} profession associations...")
                    for i, prof_id in enumerate(profession_ids, 1):
                        logger.info(f"  {i}. Creating BuildProfession: build_id={db_obj.id}, profession_id={prof_id}")
                        try:
                            # Verify profession exists
                            prof = db.query(Profession).filter_by(id=prof_id).first()
                            if not prof:
                                raise ValueError(f"Profession with ID {prof_id} not found in database")
                                
                            bp = BuildProfession(build_id=db_obj.id, profession_id=prof_id)
                            logger.info(f"  Created BuildProfession: {bp}")
                            db.add(bp)
                            logger.info("  BuildProfession added to session")
                            
                        except Exception as bp_err:
                            logger.error(f"  Error creating BuildProfession: {str(bp_err)}", exc_info=True)
                            raise
                    
                    # Verify associations were created
                    db.flush()
                    logger.info("\nVerifying profession associations...")
                    assoc_count = db.query(BuildProfession).filter_by(build_id=db_obj.id).count()
                    logger.info(f"Successfully created {assoc_count}/{len(profession_ids)} profession associations")
                    
                    if assoc_count != len(profession_ids):
                        logger.warning(f"Mismatch in created associations. Expected {len(profession_ids)}, got {assoc_count}")
                
                # Only commit if we started the transaction
                if not in_transaction:
                    logger.info("\n[5/5] Committing transaction...")
                    db.commit()
                    logger.info("✅ Transaction committed successfully")
                else:
                    logger.info("\n[5/5] Skipping commit - using existing transaction")
                
                # Refresh and return the build
                db.refresh(db_obj)
                logger.info(f"✅ Successfully created build: {db_obj}")
                
                # Verify the build was saved
                saved_build = db.query(Build).filter_by(id=db_obj.id).first()
                if not saved_build:
                    logger.error("❌ Build not found in database after commit!")
                    return None
                    
                logger.info(f"✅ Verified build exists in database with ID: {saved_build.id}")
                return db_obj
                
            except Exception as inner_e:
                logger.error("\n❌ Error during transaction:", exc_info=True)
                logger.error(f"Error type: {type(inner_e).__name__}")
                logger.error(f"Error details: {str(inner_e)}")
                
                if 'transaction' in locals():
                    try:
                        transaction.rollback()
                        logger.info("Transaction rolled back due to error")
                    except Exception as rollback_err:
                        logger.error(f"Error during rollback: {str(rollback_err)}")
                
                return None
            
        except Exception as e:
            logger.error("\n❌ Unhandled error in create_with_owner:", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            return None
        finally:
            logger.info("="*80 + "\n")

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
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle profession updates if needed
        if 'profession_ids' in update_data:
            # Remove existing associations
            db.query(BuildProfession).filter(
                BuildProfession.build_id == db_obj.id
            ).delete()
            
            # Add new associations
            for prof_id in update_data.pop('profession_ids', []):
                bp = BuildProfession(build_id=db_obj.id, profession_id=prof_id)
                db.add(bp)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_with_professions(
        self, db: Session, *, id: int, user_id: Optional[int] = None
    ) -> Optional[models.Build]:
        query = db.query(self.model).filter(self.model.id == id)
        
        # Check if user has access
        if user_id:
            query = query.filter(
                (self.model.is_public == True) |  # noqa: E712
                (self.model.created_by_id == user_id)
            )
        
        return (
            query
            .options(joinedload(self.model.professions))
            .first()
        )

    def update_with_professions(
        self, 
        db: Session, 
        *, 
        db_obj: Build, 
        obj_in: Union[schemas.BuildUpdate, Dict[str, Any]],
        user_id: int
    ) -> Optional[Build]:
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            # Handle profession updates if needed
            if 'profession_ids' in update_data:
                # Remove existing associations
                db.query(BuildProfession).filter(
                    BuildProfession.build_id == db_obj.id
                ).delete()
                
                # Add new associations
                for prof_id in update_data.pop('profession_ids', []):
                    bp = BuildProfession(build_id=db_obj.id, profession_id=prof_id)
                    db.add(bp)
            
            # Update other fields
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
            
        except Exception as e:
            logger.error(f"Error updating build: {str(e)}", exc_info=True)
            db.rollback()
            return None


# Create a singleton instance
build = CRUDBuild(Build)
