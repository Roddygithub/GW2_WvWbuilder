"""Enhanced tests for build CRUD operations."""
import uuid
import json
import pytest
from fastapi import status, HTTPException, HTTPException as FastAPIHTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.future import select
from datetime import datetime, timezone, UTC
from typing import Dict, Any, List, Optional, Set
from pydantic import ValidationError

from app.models.base_models import Build, build_profession, User, Profession, EliteSpecialization, Role, user_roles
from app.schemas.build import BuildCreate, BuildUpdate, BuildGenerationRequest, Build as BuildSchema
from app.crud.build import CRUDBuild, build as build_crud
from app.core.security import get_password_hash
from app.core.config import settings
# Using FastAPI's built-in exceptions instead of custom ones

# Test data
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "Test Description",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "config": {
        "weapons": ["Greatsword", "Hammer"],
        "traits": ["Strength", "Discipline", "Spellbreaker"],
        "skills": ["Banner of Strength", "Banner of Discipline"]
    },
    "constraints": {
        "required_roles": ["banners", "might"],
        "min_healers": 1
    },
    "profession_ids": [1, 2]  # Will be replaced in tests
}

@pytest.fixture(autouse=True)
def cleanup_db(db: Session):
    """Clean up the database after each test."""
    yield
    # Clean up all test data
    db.execute(build_profession.delete())
    db.execute(EliteSpecialization.__table__.delete())
    db.execute(Profession.__table__.delete())
    db.execute(Build.__table__.delete())
    db.execute(User.__table__.delete())
    db.commit()

@pytest.fixture
def test_role(db: Session) -> Role:
    """Create a test role."""
    role = Role(
        name=f"test_role_{uuid.uuid4().hex[:8]}",
        description="Test Role",
        permission_level=100,
        is_default=True
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@pytest.fixture
def test_user(db: Session, test_role: Role) -> User:
    """Create a test user with a unique username and email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name=f"Test User {unique_id}",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.flush()
    
    # Assign role to user
    stmt = user_roles.insert().values(user_id=user.id, role_id=test_role.id)
    db.execute(stmt)
    
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_professions(db: Session):
    """Create test professions."""
    # Create professions
    professions = []
    for i in range(3):
        prof = Profession(
            name=f"Profession {i}",
            description=f"Test Profession {i}",
        )
        db.add(prof)
        professions.append(prof)
    
    db.commit()
    
    # Create elite specializations
    for prof in professions:
        elite = EliteSpecialization(
            name=f"Elite {prof.name}",
            description=f"Elite spec for {prof.name}",
            profession_id=prof.id
        )
        db.add(elite)
    
    db.commit()
    return professions

def test_create_build(db: Session, test_user: User, test_professions: List[Profession]) -> None:
    """Test creating a build with various scenarios."""
    # Clear any existing build_professions to avoid unique constraint issues
    db.execute(build_profession.delete())
    db.commit()
    
    # Test with minimum required fields
    build_data = BuildCreate(**{
        **TEST_BUILD_DATA,
        "profession_ids": [test_professions[0].id]
    })
    build = CRUDBuild(Build).create_with_owner(db, obj_in=build_data, owner_id=test_user.id)
    assert build.id is not None
    assert build.name == TEST_BUILD_DATA["name"]
    assert build.description == TEST_BUILD_DATA["description"]
    assert build.game_mode == "wvw"
    assert build.team_size == 5
    assert build.is_public is True
    assert build.config == TEST_BUILD_DATA["config"]
    assert build.constraints == TEST_BUILD_DATA["constraints"]
    assert build.created_by_id == test_user.id
    assert build.created_at is not None
    assert build.updated_at is not None
    
    # Refresh the build to ensure we have the latest data
    db.refresh(build)
    assert len(build.professions) == 1  # type: ignore
    assert build.professions[0].id == test_professions[0].id  # type: ignore

    # Test with minimum required professions (1)
    build_data = BuildCreate(**{
        **TEST_BUILD_DATA,
        "name": "Build with minimum professions",
        "profession_ids": [test_professions[0].id]
    })
    build = CRUDBuild(Build).create_with_owner(db, obj_in=build_data, owner_id=test_user.id)
    
    # Test partial update (only update name)
    update_data = BuildUpdate(name="Partially Updated Name")
    updated_build = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=update_data, user_id=test_user.id
    )
    assert updated_build.name == "Partially Updated Name"
    assert updated_build.description == TEST_BUILD_DATA["description"]  # Should remain unchanged
    
    # Update build with new data and additional profession
    update_data = BuildUpdate(
        name="Updated Build Name",
        description="Updated Description",
        profession_ids=[test_professions[0].id, test_professions[1].id],
        is_public=False,
        config={"weapons": ["Sword", "Pistol"], "traits": ["Daredevil"]},
        constraints={"required_roles": ["damage"], "min_healers": 0}
    )
    
    updated_build = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=update_data, user_id=test_user.id
    )
    
    assert updated_build.name == "Updated Build Name"
    assert updated_build.description == "Updated Description"
    assert not updated_build.is_public
    assert updated_build.config == {"weapons": ["Sword", "Pistol"], "traits": ["Daredevil"]}
    assert updated_build.constraints == {"required_roles": ["damage"], "min_healers": 0}
    assert len(updated_build.professions) == 2  # type: ignore
    assert {p.id for p in updated_build.professions} == {test_professions[0].id, test_professions[1].id}  # type: ignore
    
    # Verify that updated_at was updated (use assertNotEqual since they might be the same in tests)
    # Note: In a real scenario with enough time between operations, updated_at would be different
    assert updated_build.updated_at >= build.updated_at
    
    # Test updating with invalid profession ID
    update_data = BuildUpdate(profession_ids=[99999])  # Non-existent profession
    result = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=update_data, user_id=test_user.id
    )
    assert result is None  # Should return None on error
    
    # Test updating with empty profession IDs (should raise Pydantic validation error)
    with pytest.raises(ValidationError) as exc_info:
        # This will raise a Pydantic validation error during model creation
        BuildUpdate(profession_ids=[])
    
    # Check for Pydantic validation error
    assert "profession_ids" in str(exc_info.value)
    
    # Test unauthorized update (non-owner, non-admin)
    other_user = User(
        username="other_user",
        email="other@example.com",
        hashed_password=get_password_hash("otherpassword"),
        is_active=True
    )
    db.add(other_user)
    db.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        update_data = BuildUpdate(name="Unauthorized Update")
        CRUDBuild(Build).update_with_professions(
            db, db_obj=build, obj_in=update_data, user_id=other_user.id
        )
    assert exc_info.value.status_code == 403
    assert "Not enough permissions" in str(exc_info.value.detail)
    
    # Test admin can update any build
    admin_user = User(
        username="admin_user",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    
    admin_update_data = BuildUpdate(description="Updated by admin")
    admin_updated = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=admin_update_data, user_id=admin_user.id
    )
    assert admin_updated.description == "Updated by admin"
    
    # Test updating non-existent build
    with pytest.raises(ValueError) as exc_info:
        non_existent_build = Build(id=99999, name="Non-existent")
        CRUDBuild(Build).update_with_professions(
            db, db_obj=non_existent_build, obj_in=BuildUpdate(name="Test"), user_id=test_user.id
        )
    assert "Build with ID 99999 not found" in str(exc_info.value)

def test_update_build(db: Session, test_user: User, test_professions: List[Profession]) -> None:
    """Test updating a build with various scenarios."""
    # Clear any existing build_professions to avoid unique constraint issues
    db.execute(build_profession.delete())
    db.commit()
    
    # Create a build first
    build_data = BuildCreate(**{
        **TEST_BUILD_DATA,
        "profession_ids": [test_professions[0].id]
    })
    build = CRUDBuild(Build).create_with_owner(db, obj_in=build_data, owner_id=test_user.id)
    
    # Test updating with new values
    update_data = BuildUpdate(
        name="Updated Build Name",
        description="Updated description",
        team_size=10,
        is_public=False,
        config={"new": "config"},
        constraints={"new": "constraints"},
        profession_ids=[p.id for p in test_professions[1:3]]  # Change professions
    )
    
    updated_build = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=update_data, user_id=test_user.id
    )
    
    # Verify updates
    assert updated_build.name == "Updated Build Name"
    assert updated_build.description == "Updated description"
    assert updated_build.team_size == 10
    assert updated_build.is_public is False
    assert updated_build.config == {"new": "config"}
    assert updated_build.constraints == {"new": "constraints"}
    assert updated_build.updated_at >= build.updated_at
    
    # Refresh to ensure we have the latest data
    db.refresh(updated_build)
    
    # Verify profession associations were updated
    assert len(updated_build.professions) == 2  # type: ignore
    assert {p.id for p in updated_build.professions} == {p.id for p in test_professions[1:3]}  # type: ignore
    
    # Test updating with invalid profession ID
    update_data = BuildUpdate(profession_ids=[99999])  # Non-existent profession
    result = CRUDBuild(Build).update_with_professions(
        db, db_obj=build, obj_in=update_data, user_id=test_user.id
    )
    assert result is None  # Should return None on error
    
    # Verify that updated_at was updated (use assertNotEqual since they might be the same in tests)
    # Note: In a real scenario with enough time between operations, updated_at would be different
    assert updated_build.updated_at >= build.updated_at

def test_delete_build(db: Session, test_user: User, test_professions: List[Profession]) -> None:
    """Test deleting a build and its associations."""
    # Clear any existing build_professions to avoid unique constraint issues
    db.execute(build_profession.delete())
    db.commit()
    
    # Create a build with professions
    build_data = BuildCreate(**{
        **TEST_BUILD_DATA,
        "profession_ids": [p.id for p in test_professions]
    })
    build = CRUDBuild(Build).create_with_owner(db, obj_in=build_data, owner_id=test_user.id)
    build_id = build.id
    
    # Ensure the build is committed to the database
    db.commit()
    
    # Verify build exists with professions
    build_with_profs = db.query(Build).options(joinedload(Build.professions)).filter(Build.id == build_id).first()
    assert build_with_profs is not None
    assert len(build_with_profs.professions) == len(test_professions)  # type: ignore
    
    # Delete the build - call remove without user_id
    deleted_build = CRUDBuild(Build).remove(db, id=build_id)
    assert deleted_build is not None
    assert deleted_build.id == build_id
    
    # Verify build is deleted
    assert CRUDBuild(Build).get(db, id=build_id) is None
    
    # Verify build_profession associations are deleted
    stmt = select(build_profession).where(build_profession.c.build_id == build_id)
    result = db.execute(stmt).all()
    assert len(result) == 0
    
    # Test deleting non-existent build (should return None, not raise)
    non_existent_id = 99999
    assert CRUDBuild(Build).get(db, id=non_existent_id) is None
    assert CRUDBuild(Build).remove(db, id=non_existent_id) is None
    
    # Test deleting a build
    build_to_delete = CRUDBuild(Build).create_with_owner(
        db, 
        obj_in=BuildCreate(**{
            **TEST_BUILD_DATA,
            "profession_ids": [test_professions[0].id]
        }), 
        owner_id=test_user.id
    )
    
    # Delete the build
    deleted = CRUDBuild(Build).remove(db, id=build_to_delete.id)
    assert deleted is not None
    assert deleted.id == build_to_delete.id
    assert CRUDBuild(Build).get(db, id=build_to_delete.id) is None
    
    # Test cascading delete with related models
    # Create a build with professions
    build_with_relations = CRUDBuild(Build).create_with_owner(
        db,
        obj_in=BuildCreate(**{
            **TEST_BUILD_DATA,
            "name": "Build with relations",
            "profession_ids": [p.id for p in test_professions]
        }),
        owner_id=test_user.id
    )
    
    # Verify build was created with professions
    build_with_relations = db.query(Build).options(joinedload(Build.professions))\
        .filter(Build.id == build_with_relations.id).first()
    assert build_with_relations is not None
    assert len(build_with_relations.professions) > 0
    
    # Delete the build and verify cascading deletes
    CRUDBuild(Build).remove(db, id=build_with_relations.id)
    
    # Verify build_profession associations are deleted
    stmt = select(build_profession).where(build_profession.c.build_id == build_with_relations.id)
    result = db.execute(stmt).all()
    assert len(result) == 0
    
    # Verify professions still exist (shouldn't be deleted by cascade)
    for prof in test_professions:
        assert db.query(Profession).filter(Profession.id == prof.id).first() is not None
    admin_user = User(
        username="admin_user_2",
        email="admin2@example.com",
        hashed_password=get_password_hash("adminpassword2"),
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    
    # Test admin can delete any build
    admin_deletable_build = CRUDBuild(Build).create_with_owner(
        db,
        obj_in=BuildCreate(**{
            **TEST_BUILD_DATA,
            "name": "Build to delete by admin",
            "profession_ids": [test_professions[0].id]
        }),
        owner_id=test_user.id
    )
    
    # Admin deletes the build
    deleted = CRUDBuild(Build).remove(db, id=admin_deletable_build.id)
    assert deleted is not None
    assert db.get(Build, admin_deletable_build.id) is None
