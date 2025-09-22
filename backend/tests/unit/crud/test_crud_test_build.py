"""Tests for build CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import build as crud_build
from app.models import Build, User, Profession
from app.schemas.build import BuildCreate, BuildUpdate


@pytest.mark.asyncio
async def test_create_build(
    db_session: AsyncSession, test_user: User, test_profession: Profession
):
    """Test creating a build."""
    build_in = BuildCreate(
        name="Test Build",
        description="Test Build Description",
        profession_id=test_profession.id,
        is_public=True,
        game_mode="pvp",
    )

    build = await crud_build.create_with_owner(
        db_session, obj_in=build_in, owner_id=test_user.id
    )

    assert build.name == "Test Build"
    assert build.description == "Test Build Description"
    assert build.created_by == test_user.id
    assert build.profession_id == test_profession.id
    assert build.is_public is True
    assert build.game_mode == "pvp"


@pytest.mark.asyncio
async def test_get_build(db_session: AsyncSession, test_build: Build):
    """Test getting a build by ID."""
    build = await crud_build.get(db_session, test_build.id)

    assert build is not None
    assert build.id == test_build.id
    assert build.name == test_build.name


@pytest.mark.asyncio
async def test_get_multi_builds(
    db_session: AsyncSession, test_user: User, test_profession: Profession
):
    """Test getting multiple builds with pagination."""
    # Create test builds
    for i in range(1, 6):
        build_in = BuildCreate(
            name=f"Test Build {i}",
            description=f"Description {i}",
            profession_id=test_profession.id,
            is_public=(i % 2 == 0),  # Alternate public/private
            game_mode="pvp",
        )
        await crud_build.create_with_owner(
            db_session, obj_in=build_in, owner_id=test_user.id
        )

    # Test pagination
    builds_page1 = await crud_build.get_multi(db_session, skip=0, limit=3)
    assert len(builds_page1) == 3

    builds_page2 = await crud_build.get_multi(db_session, skip=3, limit=3)
    assert len(builds_page2) >= 2  # At least 2 more builds


@pytest.mark.asyncio
async def test_get_multi_by_owner(
    db_session: AsyncSession, test_user: User, test_profession: Profession
):
    """Test getting builds by owner."""
    # Create test builds with different owners
    for i in range(1, 4):
        build_in = BuildCreate(
            name=f"Owned Build {i}",
            description=f"Owned Description {i}",
            profession_id=test_profession.id,
            is_public=True,
            game_mode="wvw",
        )
        await crud_build.create_with_owner(
            db_session, obj_in=build_in, owner_id=test_user.id
        )

    # Get builds created by test_user
    builds = await crud_build.get_multi_by_owner(
        db_session, owner_id=test_user.id, skip=0, limit=10
    )

    assert len(builds) == 1  # +1 for the fixture
    assert all(build.created_by == test_user.id for build in builds)


@pytest.mark.asyncio
async def test_update_build(db_session: AsyncSession, test_build: Build):
    """Test updating a build."""
    update_data = BuildUpdate(
        name="Updated Build",
        description="Updated Description",
        is_public=False,
        game_mode="pve",
    )

    updated_build = await crud_build.update(
        db_session, db_obj=test_build, obj_in=update_data
    )

    assert updated_build.name == "Updated Build"
    assert updated_build.description == "Updated Description"
    assert updated_build.is_public is False
    assert updated_build.game_mode == "pve"


@pytest.mark.asyncio
async def test_remove_build(db_session: AsyncSession, test_build: Build):
    """Test removing a build."""
    # First, verify the build exists
    build = await crud_build.get(db_session, test_build.id)
    assert build is not None

    # Remove the build
    await crud_build.remove(db_session, id=test_build.id)

    # Verify the build no longer exists
    removed_build = await crud_build.get(db_session, test_build.id)
    assert removed_build is None


@pytest.mark.asyncio
async def test_add_profession_to_build(
    db_session: AsyncSession, test_build: Build, test_profession: Profession
):
    """Test adding a profession to a build."""
    # Add profession to build
    build = await crud_build.add_profession(
        db_session, build_id=test_build.id, profession_id=test_profession.id
    )

    # Verify the profession was added
    assert len(build.professions) == 1
    assert build.professions[0].id == test_profession.id

    # Test adding the same profession again (should be idempotent)
    build = await crud_build.add_profession(
        db_session, build_id=test_build.id, profession_id=test_profession.id
    )
    assert len(build.professions) == 1  # Still only one profession


@pytest.mark.asyncio
async def test_remove_profession_from_build(
    db_session: AsyncSession, test_build: Build, test_profession: Profession
):
    """Test removing a profession from a build."""
    # First, add a profession
    await crud_build.add_profession(
        db_session, build_id=test_build.id, profession_id=test_profession.id
    )

    # Now remove it
    build = await crud_build.remove_profession(
        db_session, build_id=test_build.id, profession_id=test_profession.id
    )

    # Verify the profession was removed
    assert len(build.professions) == 0

    # Test removing a non-existent profession (should be a no-op)
    build = await crud_build.remove_profession(
        db_session, build_id=test_build.id, profession_id=999  # Non-existent ID
    )
    assert build is not None
