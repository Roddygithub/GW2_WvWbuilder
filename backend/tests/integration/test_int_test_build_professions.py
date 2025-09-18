"""Tests for build-profession associations."""
import logging
from typing import List

import pytest
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.build import build as build_crud
from app.db.base import Base
from app.models import Build, Profession

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
    build_data = {
        "name": "Test Build with Professions",
        "description": "A build with multiple professions",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {"test": "config"},
        "constraints": {"test": "constraints"},
        "profession_ids": profession_ids
    }
    
    # Create build using CRUD
    build = build_crud.create_with_owner(
        db=db,
        obj_in=schemas.BuildCreate(**build_data),
        owner_id=1,  # Assuming user with ID 1 exists
        profession_ids=profession_ids
    )
    
    logger.info(f"Created build with ID: {build.id}")
    
    # Verify the build was created correctly
    assert build is not None
    assert build.name == build_data["name"]
    assert build.description == build_data["description"]
    assert build.game_mode == build_data["game_mode"]
    assert build.team_size == build_data["team_size"]
    assert build.is_public == build_data["is_public"]
    assert build.config == build_data["config"]
    assert build.constraints == build_data["constraints"]
    
    # Verify profession associations were created
    db.refresh(build)
    assert len(build.professions) == len(profession_ids)
    
    # Check that all specified professions are associated
    associated_profession_ids = {p.id for p in build.professions}
    assert associated_profession_ids == set(profession_ids)
    
    # Verify we can retrieve the build with its professions
    build_in_db = db.query(Build).options(
        joinedload(Build.professions)
    ).filter(Build.id == build.id).first()
    
    assert build_in_db is not None
    assert len(build_in_db.professions) == len(profession_ids)
    
    logger.info("=== Test completed successfully ===")
