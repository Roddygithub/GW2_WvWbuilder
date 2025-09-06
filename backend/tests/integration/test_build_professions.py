"""Tests for build-profession associations."""
import logging
from typing import List

import pytest
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.build import build as build_crud
from app.db.base import Base
from app.models import Build, BuildProfession, Profession

logger = logging.getLogger(__name__)

def test_create_build_with_professions(db: Session) -> None:
    """Test creating a build with associated professions."""
    logger.info("=== Starting test_create_build_with_professions ===")
    
    # Create test professions
    professions = [
        Profession(name=f"TestProf{i}", description=f"Test Profession {i}")
        for i in range(1, 4)
    ]
    db.add_all(professions)
    db.flush()
    profession_ids = [p.id for p in professions]
    
    logger.info(f"Created professions with IDs: {profession_ids}")
    
    # Create build data
    build_data = schemas.BuildCreate(
        name="Test Build with Professions",
        description="A test build with multiple professions",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        profession_ids=profession_ids,
        config={"key": "value"},
        constraints={"min_healers": 1}
    )
    
    # Create the build
    db_build = build_crud.create_with_owner(
        db=db,
        obj_in=build_data,
        owner_id=1  # Assuming user with ID 1 exists
    )
    
    # Verify the build was created
    assert db_build is not None
    assert db_build.id is not None
    logger.info(f"Created build with ID: {db_build.id}")
    
    # Verify the build was saved to the database
    db_build = db.query(Build).filter(Build.id == db_build.id).first()
    assert db_build is not None
    
    # Verify the build-profession associations
    build_profs = db.query(BuildProfession).filter(
        BuildProfession.build_id == db_build.id
    ).all()
    
    logger.info(f"Found {len(build_profs)} build-profession associations")
    assert len(build_profs) == len(profession_ids), \
        f"Expected {len(profession_ids)} associations, got {len(build_profs)}"
    
    # Verify the profession IDs match
    associated_prof_ids = {bp.profession_id for bp in build_profs}
    expected_prof_ids = set(profession_ids)
    
    logger.info(f"Associated profession IDs: {associated_prof_ids}")
    logger.info(f"Expected profession IDs: {expected_prof_ids}")
    
    assert associated_prof_ids == expected_prof_ids, \
        f"Expected profession IDs {expected_prof_ids}, got {associated_prof_ids}"
    
    # Verify the relationship on the build object
    if hasattr(db_build, 'professions'):
        logger.info(f"Build has {len(db_build.professions)} professions via relationship")
        assert len(db_build.professions) == len(profession_ids), \
            f"Expected {len(profession_ids)} professions via relationship, got {len(db_build.professions)}"
    else:
        logger.warning("Build object does not have 'professions' relationship")
    
    logger.info("=== Test completed successfully ===")
