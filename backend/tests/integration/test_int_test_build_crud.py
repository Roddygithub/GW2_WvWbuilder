"""Comprehensive tests for Build CRUD operations."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Build, User, Profession, EliteSpecialization
from app.schemas.build import BuildConfig, GameMode

@pytest.mark.asyncio
async def test_create_build(async_db, user_factory, profession_factory):
    """Test creating a build with valid data."""
    # Create test user and profession
    user = await user_factory()
    profession = await profession_factory()
    
    # Create build data
    build_data = {
        "name": "Test Build",
        "description": "A test build",
        "game_mode": GameMode.WVW.value,
        "is_public": True,
        "created_by_id": user.id,
        "professions": [profession],
        "config": BuildConfig().dict()
    }
    
    # Create and add build
    build = Build(**build_data)
    async_db.add(build)
    await async_db.commit()
    await async_db.refresh(build)
    
    # Verify build was created
    assert build.id is not None
    assert build.name == "Test Build"
    assert len(build.professions) == 1
    assert build.professions[0].id == profession.id

@pytest.mark.asyncio
async def test_read_build(async_db, build_factory):
    """Test reading a build by ID."""
    # Create a test build
    build = await build_factory()
    
    # Retrieve the build
    result = await async_db.execute(select(Build).filter_by(id=build.id))
    fetched_build = result.scalar_one_or_none()
    
    # Verify the build was retrieved
    assert fetched_build is not None
    assert fetched_build.id == build.id
    assert fetched_build.name == build.name

@pytest.mark.asyncio
async def test_update_build(async_db, build_factory):
    """Test updating a build."""
    # Create a test build
    build = await build_factory()
    
    # Update the build
    build.name = "Updated Build Name"
    build.description = "Updated description"
    build.is_public = False
    
    await async_db.commit()
    await async_db.refresh(build)
    
    # Verify the update
    assert build.name == "Updated Build Name"
    assert build.description == "Updated description"
    assert build.is_public is False

@pytest.mark.asyncio
async def test_delete_build(async_db, build_factory):
    """Test deleting a build."""
    # Create a test build
    build = await build_factory()
    build_id = build.id
    
    # Delete the build
    await async_db.delete(build)
    await async_db.commit()
    
    # Verify the build was deleted
    result = await async_db.execute(select(Build).filter_by(id=build_id))
    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_build_validation_missing_name(async_db, user_factory):
    """Test build validation fails with missing name."""
    user = await user_factory()
    build = Build(
        description="A build with no name",
        game_mode=GameMode.WVW.value,
        created_by_id=user.id,
        config=BuildConfig().dict()
    )
    
    with pytest.raises(IntegrityError):
        async_db.add(build)
        await async_db.commit()
    
    await async_db.rollback()

@pytest.mark.asynbox async def test_build_with_multiple_professions(async_db, user_factory, profession_factory):
    """Test creating a build with multiple professions."""
    user = await user_factory()
    profession1 = await profession_factory(name="Guardian")
    profession2 = await profession_factory(name="Warrior")
    
    build = Build(
        name="Multi-Profession Build",
        game_mode=GameMode.WVW.value,
        created_by_id=user.id,
        config=BuildConfig().dict(),
        professions=[profession1, profession2]
    )
    
    async_db.add(build)
    await async_db.commit()
    await async_db.refresh(build)
    
    assert len(build.professions) == 2
    assert {p.name for p in build.professions} == {"Guardian", "Warrior"}

@pytest.mark.asynbox async def test_build_visibility(async_db, user_factory, build_factory):
    """Test build visibility (public/private)."""
    user1 = await user_factory(username="user1")
    user2 = await user_factory(username="user2")
    
    # Create public and private builds for user1
    public_build = await build_factory(created_by=user1, is_public=True)
    private_build = await build_factory(created_by=user1, is_public=False)
    
    # Test public build is visible to all
    result = await async_db.execute(
        select(Build)
        .filter_by(id=public_build.id)
    )
    assert result.scalar_one_or_none() is not None
    
    # Test private build is only visible to owner
    result = await async_db.execute(
        select(Build)
        .filter(
            (Build.id == private_build.id) &
            ((Build.is_public == True) | (Build.created_by_id == user2.id))
        )
    )
    assert result.scalar_one_or_none() is None
