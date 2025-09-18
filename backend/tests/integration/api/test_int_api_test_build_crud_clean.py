"""Integration tests for build CRUD operations."""
import json
import logging
import traceback
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, joinedload

from app import crud
from app.core.config import settings
from app.models import models
from app.models.build import Build, BuildProfession
from app.models.profession import Profession
from app.schemas.build import BuildCreate, BuildUpdate, Build as BuildSchema

logger = logging.getLogger(__name__)

def test_create_build(client: TestClient, db: Session, test_user: models.User) -> None:
    """Test creating a new build with associated professions."""
    logger.info("=== Starting test_create_build ===")
    
    try:
        logger.info(f"Using test user with ID: {test_user.id}")
        
        # Create test professions
        logger.info("Creating test professions...")
        professions = []
        for i in range(3):
            prof = Profession(
                name=f"Test Profession {i}",
                description=f"Test Description {i}",
                icon_url=f"http://example.com/icon{i}.png"
            )
            db.add(prof)
            db.flush()  # Flush to get the ID
            professions.append(prof)
        
        # Commit to make sure the professions are visible to the API
        db.commit()
        
        logger.info(f"Created {len(professions)} test professions with IDs: {[p.id for p in professions]}")
        
        # Set the current user in the test client using the user ID as the token
        logger.info("Setting current user in test client...")
        client.headers.update({"Authorization": f"Bearer {test_user.id}"})
        # Also set the token directly in the client for the test
        if hasattr(client, 'set_current_user'):
            client.set_current_user(test_user)
        
        # Create test build data with the profession IDs
        build_data = {
            "name": "Test Build CRUD",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "config": {"test": "config"},
            "constraints": {"test": "constraints"},
            "profession_ids": [p.id for p in professions]
        }
        
        logger.info(f"Sending request with data: {build_data}")
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify build was created with correct data
        assert data["name"] == build_data["name"]
        assert data["description"] == build_data["description"]
        assert data["game_mode"] == build_data["game_mode"]
        assert data["team_size"] == build_data["team_size"]
        assert data["is_public"] == build_data["is_public"]
        assert data["config"] == build_data["config"]
        assert data["constraints"] == build_data["constraints"]
        
        # Verify profession associations were created
        db.refresh(test_user)
        build_in_db = db.query(Build).options(
            joinedload(Build.professions)
        ).filter(Build.id == data["id"]).first()
        
        assert build_in_db is not None, "Build not found in database"
        assert len(build_in_db.professions) == len(professions), \
            f"Expected {len(professions)} professions in DB, got {len(build_in_db.professions)}"
        
        # Verify profession IDs match
        db_profession_ids = {p.id for p in build_in_db.professions}
        expected_profession_ids = {p.id for p in professions}
        assert db_profession_ids == expected_profession_ids, \
            f"Expected profession IDs {expected_profession_ids}, got {db_profession_ids}"
        
        logger.info("=== Test completed successfully ===")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}\n{traceback.format_exc()}")
        raise
