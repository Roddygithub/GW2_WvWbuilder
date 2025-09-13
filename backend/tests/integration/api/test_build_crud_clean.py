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
            "description": "A test build for CRUD operations",
            "game_mode": "wvw",
            "team_size": 5,
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
            "profession_ids": [p.id for p in professions]
        }
        
        # Send the build creation request
        logger.info("Sending build creation request...")
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Verify response
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
        content = response.json()
        
        # Verify basic response structure
        assert content["name"] == build_data["name"]
        # Verify the build was created with the correct owner (test_user.id)
        assert content["created_by_id"] == test_user.id
        assert content["is_public"] is True
        
        # Verify professions in response
        response_professions = content.get("professions", [])
        assert len(response_professions) == len(professions), \
            f"Expected {len(professions)} professions, got {len(response_professions)}"
        
        # Verify database state
        db_build = (
            db.query(Build)
            .options(
                joinedload(Build.build_professions)
                .joinedload(BuildProfession.profession),
                joinedload(Build.professions)
            )
            .filter(Build.id == content["id"])
            .first()
        )
        
        assert db_build is not None, "Build not found in database"
        assert len(db_build.professions) == len(professions), \
            f"Expected {len(professions)} professions in DB, got {len(db_build.professions)}"
        
        # Verify profession IDs match
        db_profession_ids = {p.id for p in db_build.professions}
        expected_profession_ids = {p.id for p in professions}
        assert db_profession_ids == expected_profession_ids, \
            f"Expected profession IDs {expected_profession_ids}, got {db_profession_ids}"
        
        logger.info("=== Test completed successfully ===")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}\n{traceback.format_exc()}")
        raise
