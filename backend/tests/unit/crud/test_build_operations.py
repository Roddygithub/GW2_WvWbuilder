import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app import models, schemas
from app.crud.build import CRUDBuild
from app.schemas.build import BuildCreate, BuildUpdate
from tests.integration.fixtures.factories import UserFactory, BuildFactory, ProfessionFactory

# Test utilities
def create_test_user(db: Session, username: str = "testuser") -> models.User:
    """Create a test user."""
    # Set the session for the factory
    UserFactory._meta.sqlalchemy_session = db
    return UserFactory.create(
        username=username,
        email=f"{username}@example.com",
        is_active=True,
        is_superuser=False
    )

def create_test_build(db: Session, user_id: int, is_public: bool = True) -> models.Build:
    """Create a test build."""
    # Create a user if not provided
    if not db.query(models.User).filter(models.User.id == user_id).first():
        create_test_user(db, f"user{user_id}")
    
    # Create build directly using the model
    build = models.Build(
        name="Test Build",
        description="A test build",
        game_mode="wvw",
        team_size=5,
        is_public=is_public,
        created_by_id=user_id,
        config={},
        constraints={}
    )
    db.add(build)
    db.commit()
    db.refresh(build)
    return build

def test_create_build(db: Session):
    """Test creating a new build."""
    # Create a test user
    user = create_test_user(db, "testuser")
    
    # Create a test profession
    profession = models.Profession(name="Test Profession", description="Test Description")
    db.add(profession)
    db.commit()
    db.refresh(profession)
    
    # Create test data using Pydantic model
    build_data = BuildCreate(
        name="Test Build",
        description="A test build",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        config={},
        constraints={},
        profession_ids=[profession.id]  # Include at least one profession ID
    )
    
    # Create build
    crud_build = CRUDBuild(models.Build)
    build = crud_build.create_with_owner(db=db, obj_in=build_data, owner_id=user.id)
    
    # Verify the build was created correctly
    assert build.id is not None
    assert build.name == "Test Build"
    assert build.created_by_id == user.id
    assert build.is_public is True

    assert build.is_public is True

def test_get_build(db: Session):
    """Test retrieving a build by ID."""
    # Create a test user and build
    user = create_test_user(db, "testuser")
    build = create_test_build(db, user.id)
    
    # Retrieve the build
    crud_build = CRUDBuild(models.Build)
    retrieved = crud_build.get(db, id=build.id)
    
    # Verify the build was retrieved correctly
    assert retrieved is not None
    assert retrieved.id == build.id
    assert retrieved.name == build.name
    assert retrieved.created_by_id == user.id

def test_update_build(db: Session):
    """Test updating a build."""
    # Create a test user and build
    user = create_test_user(db, "testuser")
    build = create_test_build(db, user.id)
    
    # Create a test profession
    profession = models.Profession(name="Test Profession", description="Test Description")
    db.add(profession)
    db.commit()
    db.refresh(profession)
    
    # Update data using Pydantic model
    update_data = BuildUpdate(
        name="Updated Build Name",
        profession_ids=[profession.id]  # Include required profession_ids
    )
    
    # Update the build
    crud_build = CRUDBuild(models.Build)
    updated_build = crud_build.update(db, db_obj=build, obj_in=update_data)
    
    # Commit the changes and refresh
    db.commit()
    db.refresh(updated_build)
    
    # Verify the build was updated
    assert updated_build.name == "Updated Build Name"
    assert updated_build.updated_at is not None

def test_delete_build(db: Session):
    """Test deleting a build."""
    # Create a test user and build
    user = create_test_user(db, "testuser")
    build = create_test_build(db, user.id)
    
    # Verify build exists
    crud_build = CRUDBuild(models.Build)
    assert crud_build.get(db, id=build.id) is not None
    
    # Delete the build
    deleted_build = crud_build.remove(db, id=build.id)
    
    # Verify the build was deleted
    assert deleted_build is not None
    assert crud_build.get(db, id=build.id) is None

def test_get_public_builds(db: Session):
    """Test retrieving public builds."""
    # Create test users
    user1 = create_test_user(db, "user1")
    user2 = create_test_user(db, "user2")
    
    # Create public and private builds
    public_build1 = create_test_build(db, user1.id, is_public=True)
    public_build2 = create_test_build(db, user2.id, is_public=True)
    private_build = create_test_build(db, user1.id, is_public=False)
    
    # Get public builds
    crud_build = CRUDBuild(models.Build)
    public_builds = crud_build.get_public_builds(db)
    
    # Verify only public builds are returned
    assert len(public_builds) == 2
    assert all(build.is_public for build in public_builds)
    assert all(build.id in {public_build1.id, public_build2.id} for build in public_builds)

def test_get_multi_by_owner_with_pagination(db: Session):
    """Test retrieving builds by owner with pagination."""
    # Create test users
    user1 = create_test_user(db, "user1")
    user2 = create_test_user(db, "user2")
    
    # Create builds for both users (3 for user1, 2 for user2)
    for i in range(3):
        create_test_build(db, user1.id, is_public=True)
    
    for i in range(2):
        create_test_build(db, user2.id, is_public=True)
    
    # Test pagination for user1
    crud_build = CRUDBuild(models.Build)
    
    # Get first page (2 items)
    page1 = crud_build.get_multi_by_owner(db, owner_id=user1.id, skip=0, limit=2)
    assert len(page1) == 2
    
    # Get second page (remaining 1 item)
    page2 = crud_build.get_multi_by_owner(db, owner_id=user1.id, skip=2, limit=2)
    assert len(page2) == 1
    
    # Verify all builds belong to user1
    assert all(build.created_by_id == user1.id for build in page1 + page2)

def test_update_build_with_professions(db: Session):
    """Test updating a build with profession associations."""
    # Create test user and build
    user = create_test_user(db, "testuser")
    build = create_test_build(db, user.id)
    
    # Create test professions directly
    profession1 = models.Profession(name="Warrior", description="Warrior profession")
    profession2 = models.Profession(name="Guardian", description="Guardian profession")
    db.add_all([profession1, profession2])
    db.commit()
    
    # Update build with professions using Pydantic model
    update_data = BuildUpdate(
        profession_ids=[profession1.id, profession2.id],
        name="Updated Build with Professions"
    )
    
    crud_build = CRUDBuild(models.Build)
    updated_build = crud_build.update_with_professions(
        db=db, 
        db_obj=build, 
        obj_in=update_data,
        user_id=user.id  # Add the required user_id parameter
    )
    
    # Ensure the session is committed and refresh to load relationships
    db.commit()
    db.refresh(updated_build)
    
    # Verify the build was updated with professions
    assert updated_build.name == "Updated Build with Professions"
    assert len(updated_build.professions) == 2
    assert {p.id for p in updated_build.professions} == {profession1.id, profession2.id}
