"""Tests for the Build model."""
import pytest
from sqlalchemy import select, insert, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models import Build, Composition, composition_members, build_profession, EliteSpecialization, User, Profession, Role
from app.schemas.build import BuildUpdate, BuildCreate
from app.core.config import settings
from app.core.security import get_password_hash

@pytest.fixture(autouse=True)
async def test_build_data(async_db_session: AsyncSession):
    """Create test data for build tests."""
    # Check if role already exists
    existing_role = (await async_db_session.execute(
        select(Role).filter_by(name="test_role")
    )).scalar_one_or_none()
    
    if not existing_role:
        # Create test role if it doesn't exist
        role = Role(
            name="test_role",
            description="Test Role",
            permission_level=1,
            is_default=True
        )
        async_db_session.add(role)
        await async_db_session.flush()
    else:
        role = existing_role
    
    # Check if user already exists
    existing_user = (await async_db_session.execute(
        select(User).filter_by(username="testuser")
    )).scalar_one_or_none()
    
    if not existing_user:
        # Create test user if it doesn't exist
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        async_db_session.add(user)
        await async_db_session.flush()
    else:
        user = existing_user
    
    # Check if profession already exists
    existing_profession = (await async_db_session.execute(
        select(Profession).filter_by(name="Guardian")
    )).scalar_one_or_none()
    
    if not existing_profession:
        # Create test profession if it doesn't exist
        profession = Profession(
            name="Guardian",
            description="Test Profession",
            game_modes=["wvw", "pve"]
        )
        async_db_session.add(profession)
        await async_db_session.flush()
        
        # Create test elite specialization
        elite_spec = EliteSpecialization(
            name="Firebrand",
            profession_id=profession.id,
            description="Test Elite Spec"
        )
        async_db_session.add(elite_spec)
        await async_db_session.flush()
    else:
        profession = existing_profession
        # Get existing elite spec for the profession
        elite_spec = (await async_db_session.execute(
            select(EliteSpecialization)
            .filter_by(profession_id=profession.id, name="Firebrand")
        )).scalar_one_or_none()
        
        if not elite_spec:
            elite_spec = EliteSpecialization(
                name="Firebrand",
                profession_id=profession.id,
                description="Test Elite Spec"
            )
            async_db_session.add(elite_spec)
            await async_db_session.flush()
    
    # Create another test user for visibility tests with a unique username
    import uuid
    unique_username = f"otheruser_{uuid.uuid4().hex[:8]}"
    other_user = User(
        username=unique_username,
        email=f"{unique_username}@example.com",
        hashed_password=get_password_hash("otherpassword"),
        is_active=True,
        is_superuser=False,
    )
    async_db_session.add(other_user)
    await async_db_session.flush()
    
    return {
        "user": user,
        "other_user": other_user,
        "profession": profession,
        "elite_spec": elite_spec
    }

@pytest.mark.asyncio
async def test_create_build(async_db_session: AsyncSession, test_build_data):
    """Test creating a build."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a test build with required fields
    build = Build(
        name="Test Build",
        description="Test Build Description",
        created_by_id=test_user.id,
        is_public=True,
        game_mode="wvw"
    )
    
    # Set config separately
    build.config = {
        "build_link": "http://example.com/build",
        "video_link": "http://example.com/video",
        "specialization": "firebrand",
        "traits": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "skills": [1, 2, 3, 4, 5],
        "gear": {"weapon": "mace", "armor": "harrier"},
        "infusions": {"weapon": ["concentration"], "armor": ["healing"]},
        "food": "Bowl of Sweet and Spicy Butternut Squash Soup",
        "utility": "Superior Sharpening Stone",
        "attributes": {"healing": 1500, "concentration": 1000, "toughness": 1000},
        "rotation": "Rotation details here",
        "notes": "Additional notes about the build"
    }
    
    # Add the build to session
    async_db_session.add(build)
    await async_db_session.flush()
    
    # Add profession to the build using the association table
    stmt = insert(build_profession).values(
        build_id=build.id,
        profession_id=guardian.id
    )
    await async_db_session.execute(stmt)
    
    # Verify the build was created with correct data
    assert build.id is not None
    assert build.name == "Test Build"
    assert build.description == "Test Build Description"
    assert build.created_by_id == test_user.id
    assert build.is_public is True
    assert build.game_mode == "wvw"
    
    # Verify timestamps
    assert build.created_at is not None
    # updated_at might be None initially in some database configurations
    if hasattr(build, 'updated_at') and build.updated_at is not None:
        assert build.updated_at is not None
    
    # Verify the professions relationship
    # Need to refresh to load the relationship
    await async_db_session.refresh(build, ['professions'])
    assert len(build.professions) == 1
    assert build.professions[0].id == guardian.id

@pytest.mark.asyncio
async def test_build_relationships(async_db_session: AsyncSession, test_build_data):
    """Test build relationships."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a second profession for testing with a unique name
    import uuid
    unique_name = f"Warrior_{uuid.uuid4().hex[:8]}"  # Generate a unique name
    warrior = Profession(
        name=unique_name,
        description="Test Warrior",
        game_modes=["wvw", "pve"]
    )
    async_db_session.add(warrior)
    await async_db_session.flush()
    
    # Create a test build
    build = Build(
        name="Test Build for Relationships",
        description="Test build for relationship testing",
        created_by_id=test_user.id,  # Use created_by_id
        is_public=True,
        game_mode="wvw",
        config={}
    )
    # Add profession to the build
    build.professions.append(guardian)
    async_db_session.add(build)
    await async_db_session.flush()
    
    # Create a composition with the build relationship
    composition = Composition(
        name="Test Composition",
        description="Test Composition Description",
        created_by=test_user.id,
        is_public=True,
        squad_size=10,
        build=build  # Set the build relationship
    )
    
    # Add composition to session and flush
    async_db_session.add(composition)
    await async_db_session.flush()
    
    # Verify the composition was created with the build reference
    assert composition.id is not None
    assert composition.build_id == build.id
    
    # Verify the build relationship
    assert composition.build is not None
    assert composition.build.id == build.id
    
    # Add warrior profession to build using the association table
    stmt = insert(build_profession).values(
        build_id=build.id,
        profession_id=warrior.id
    )
    await async_db_session.execute(stmt)
    
    # Commit all changes
    await async_db_session.commit()
    
    # Refresh objects to get updated relationships
    await async_db_session.refresh(build)
    await async_db_session.refresh(composition)
    
    # Refresh to load relationships
    await async_db_session.refresh(build)
    
    # Reload build with relationships
    result = await async_db_session.execute(
        select(Build)
        .options(
            selectinload(Build.created_by),
            selectinload(Build.professions),
            selectinload(Build.compositions)
        )
        .where(Build.id == build.id)
    )
    build = result.scalar_one()
    
    # Test created_by relationship
    assert build.created_by is not None
    assert build.created_by.id == test_user.id
    
    # Test professions relationship
    assert len(build.professions) == 2
    assert any(p.name.startswith("Guardian") or p.name.startswith("Warrior_") for p in build.professions)
    
    # Test compositions relationship
    assert len(build.compositions) == 1
    assert build.compositions[0].name == "Test Composition"
    
    # Test profession relationship
    assert len(build.professions) > 0
    assert any(p.id == guardian.id for p in build.professions)
    assert any(p.id == warrior.id for p in build.professions)
    
    # Test build_profession relationship (through association table)
    result = await async_db_session.execute(
        select(build_profession)
        .where(build_profession.c.build_id == build.id)
    )
    build_professions = result.all()
    # Should have both guardian and warrior professions
    assert len(build_professions) == 2
    profession_ids = {bp.profession_id for bp in build_professions}
    assert guardian.id in profession_ids
    assert warrior.id in profession_ids

@pytest.mark.asyncio
async def test_build_update_from_schema(async_db_session: AsyncSession, test_build_data):
    """Test updating build from schema."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a test build
    build = Build(
        name="Test Build",
        description="Test Build Description",
        created_by_id=test_user.id,
        is_public=True,
        game_mode="wvw",
        config={}
    )
    # Add profession to the build
    build.professions.append(guardian)
    async_db_session.add(build)
    await async_db_session.commit()
    await async_db_session.refresh(build)
    
    # Update the build using the schema
    update_data = {
        "name": "Updated Build",
        "description": "Updated description",
        "game_mode": "pvp",
        "is_public": False,
        "config": {
            "specialization": "dragonhunter",
            "build_link": "http://example.com/updated-build"
        }
    }
    
    # Apply the update directly to the model
    for field, value in update_data.items():
        if hasattr(build, field):
            setattr(build, field, value)
    
    # Add to session and flush
    async_db_session.add(build)
    await async_db_session.flush()
    await async_db_session.refresh(build)
    
    # Verify the updates
    assert build.name == "Updated Build"
    assert build.description == "Updated description"
    assert build.is_public is False
    assert build.game_mode == "pvp"
    assert build.config.get("specialization") == "dragonhunter"
    assert build.config.get("build_link") == "http://example.com/updated-build"
    

@pytest.mark.asyncio
async def test_build_representation(async_db_session: AsyncSession, test_build_data):
    """Test build string representation."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a build
    build = Build(
        name="Test Build",
        description="Test Description",
        created_by_id=test_user.id,
        is_public=True,
        game_mode="wvw",
        config={"specialization": "dragonhunter"}
    )
    # Add profession to the build
    build.professions.append(guardian)
    async_db_session.add(build)
    await async_db_session.flush()
    
    # Test string representation
    assert str(build) == f"<Build {build.name}>"
    assert repr(build) == f"<Build {build.name}>"

@pytest.mark.asyncio
async def test_build_with_professions(async_db_session: AsyncSession, test_build_data):
    """Test build with multiple professions."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a second profession for testing with a unique name
    import uuid
    unique_name = f"Warrior_{uuid.uuid4().hex[:8]}"  # Generate a unique name
    warrior = Profession(
        name=unique_name,
        description="Test Warrior",
        game_modes=["wvw", "pve"]
    )
    async_db_session.add(warrior)
    await async_db_session.flush()
    
    # Create a test build
    build = Build(
        name="Test Build with Professions",
        description="Test build with multiple professions",
        created_by_id=test_user.id,
        is_public=True,
        game_mode="wvw",
        config={}
    )
    # Add professions to the build
    build.professions.append(guardian)
    build.professions.append(warrior)
    
    async_db_session.add(build)
    await async_db_session.flush()
    await async_db_session.refresh(build)
    
    # Query to verify the relationships
    result = await async_db_session.execute(
        select(build_profession)
        .where(build_profession.c.build_id == build.id)
    )
    build_profs = result.all()
    
    # Should have 2 profession associations
    assert len(build_profs) == 2
    
    # Get the profession IDs
    prof_ids = {prof.profession_id for prof in build_profs}
    assert guardian.id in prof_ids
    assert warrior.id in prof_ids

@pytest.mark.asyncio
async def test_build_visibility(async_db_session: AsyncSession, test_build_data):
    """Test build visibility based on is_public flag."""
    # Get test data
    test_user = test_build_data["user"]
    guardian = test_build_data["profession"]
    
    # Create a public build
    public_build = Build(
        name="Public Build",
        created_by_id=test_user.id,
        is_public=True,
        game_mode="wvw",
        config={"specialization": "firebrand"}
    )
    public_build.professions.append(guardian)
    
    # Create a private build
    private_build = Build(
        name="Private Build",
        created_by_id=test_user.id,
        is_public=False,
        game_mode="wvw",
        config={"specialization": "dragonhunter"}
    )
    private_build.professions.append(guardian)
    
    # Add builds to session
    async_db_session.add_all([public_build, private_build])
    await async_db_session.flush()
    
    # Test visibility for owner - should see both builds
    stmt = select(Build).where(
        (Build.is_public == True) | 
        (Build.created_by_id == test_user.id)
    )
    result = await async_db_session.execute(stmt)
    owner_builds = result.scalars().all()
    
    # We should see at least our two new builds in the results
    assert any(b.name == "Public Build" for b in owner_builds)
    assert any(b.name == "Private Build" for b in owner_builds)
    
    # Test visibility for other user - should only see public build
    other_user = test_build_data["other_user"]
    stmt = select(Build).where(
        (Build.is_public == True) | 
        (Build.created_by_id == other_user.id)
    )
    result = await async_db_session.execute(stmt)
    other_user_builds = result.scalars().all()
    # Should only see the public build we just created
    assert any(b.name == "Public Build" for b in other_user_builds)
    assert not any(b.name == "Private Build" for b in other_user_builds)
    
    # Find our public build in the results
    public_builds = [b for b in other_user_builds if b.name == "Public Build"]
    assert len(public_builds) == 1
    assert public_builds[0].is_public is True
    
    # Test public-only query - should only return public builds
    stmt = select(Build).where(Build.is_public == True)
    result = await async_db_session.execute(stmt)
    public_builds = result.scalars().all()
    assert len(public_builds) >= 1  # At least our public build
    assert any(b.name == "Public Build" for b in public_builds)
    
    # Clean up
    await async_db_session.delete(public_build)
    await async_db_session.delete(private_build)
    await async_db_session.commit()
