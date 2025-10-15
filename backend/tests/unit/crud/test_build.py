from sqlalchemy.orm import Session

from app.crud.build import CRUDBuild
from app.models.build import Build
from app.schemas.build import BuildCreate, BuildUpdate
from tests.integration.fixtures.factories import UserFactory, ProfessionFactory


def test_create_build(db: Session) -> None:
    """Test creating a build with valid data."""
    # Create test data
    user = UserFactory()
    profession1 = ProfessionFactory()
    profession2 = ProfessionFactory()
    db.add_all([user, profession1, profession2])
    db.commit()

    # Prepare build data
    build_data = BuildCreate(
        name="Test Build",
        description="Test description",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        profession_ids=[profession1.id, profession2.id],
        config={"test": "config"},
        constraints={"test": "constraint"},
    )

    # Create build
    crud = CRUDBuild(Build)
    result = crud.create_with_owner(db=db, obj_in=build_data, owner_id=user.id)

    # Verify the result
    assert result.name == "Test Build"
    assert result.description == "Test description"
    assert result.game_mode == "wvw"
    assert result.team_size == 5
    assert result.is_public is True
    assert result.created_by_id == user.id
    assert len(result.professions) == 2
    assert {p.id for p in result.professions} == {profession1.id, profession2.id}


def test_update_build(db: Session) -> None:
    """Test updating a build with new data."""
    # Create test data
    user = UserFactory()
    profession1 = ProfessionFactory()
    profession2 = ProfessionFactory()
    build = Build(
        name="Original Build",
        description="Original description",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        created_by_id=user.id,
        config={"original": "config"},
        constraints={"original": "constraint"},
    )
    build.professions = [profession1]
    db.add_all([user, profession1, profession2, build])
    db.commit()
    db.refresh(build)

    # Prepare update data
    update_data = BuildUpdate(
        name="Updated Build",
        description="Updated description",
        is_public=False,
        profession_ids=[profession2.id],
        config={"updated": "config"},
        constraints={"updated": "constraint"},
    )

    # Update build
    crud = CRUDBuild(Build)
    result = crud.update(db=db, db_obj=build, obj_in=update_data)

    # Verify the update
    assert result.name == "Updated Build"
    assert result.description == "Updated description"
    assert result.is_public is False
    assert len(result.professions) == 1
    assert result.professions[0].id == profession2.id
    assert result.config == {"updated": "config"}
    assert result.constraints == {"updated": "constraint"}


def test_generate_build_success(db: Session) -> None:
    """Test generating a build with valid parameters."""
    # Create test data
    user = UserFactory()
    professions = [ProfessionFactory() for _ in range(3)]
    db.add_all([user] + professions)
    db.commit()

    # Prepare generation request
    from app.schemas.build import BuildGenerationRequest

    request_data = BuildGenerationRequest(
        team_size=3,
        required_roles=["healer", "dps", "support"],
        preferred_professions=[p.id for p in professions],
        max_duplicates=2,
        min_healers=1,
        min_dps=1,
        min_support=1,
        constraints={"require_cc": True, "require_cleanses": True},
    )

    # Generate build
    crud = CRUDBuild(Build)
    result = crud.generate_build(
        db=db, generation_request=request_data, owner_id=user.id
    )

    # Verify the result
    assert result.success is True
    assert result.build is not None
    assert len(result.suggested_composition) == 3
    assert result.metrics is not None


def test_generate_build_no_professions(db: Session) -> None:
    """Test generating a build with no professions available."""
    # Create test data (no professions)
    user = UserFactory()
    db.add(user)
    db.commit()

    # Prepare generation request
    from app.schemas.build import BuildGenerationRequest

    request_data = BuildGenerationRequest(
        team_size=3,
        required_roles=["healer", "dps", "support"],
        preferred_professions=[],
        max_duplicates=2,
        min_healers=1,
        min_dps=1,
        min_support=1,
        constraints={},
    )

    # Generate build
    crud = CRUDBuild(Build)
    result = crud.generate_build(
        db=db, generation_request=request_data, owner_id=user.id
    )

    # Verify the result indicates failure
    assert result.success is False
    assert "No valid professions" in result.message
    assert result.build is None
    assert result.suggested_composition == []


def test_get_multi_by_owner(db: Session) -> None:
    """Test retrieving builds by owner."""
    # Create test data
    user1 = UserFactory()
    user2 = UserFactory()

    # Create builds for both users
    builds = [
        Build(
            name=f"Build {i}",
            description=f"Description {i}",
            game_mode="wvw",
            team_size=5,
            is_public=(i % 2 == 0),  # Alternate between public and private
            created_by_id=user1.id if i < 3 else user2.id,
        )
        for i in range(5)
    ]
    db.add_all([user1, user2] + builds)
    db.commit()

    # Test getting builds for user1
    crud = CRUDBuild(Build)
    user1_builds = crud.get_multi_by_owner(db, owner_id=user1.id)
    assert (
        len(user1_builds) == 3
    )  # Should get all builds for user1 regardless of visibility

    # Test getting builds with limit and skip
    limited_builds = crud.get_multi_by_owner(db, owner_id=user1.id, skip=1, limit=2)
    assert len(limited_builds) == 2  # Should get 2 builds, skipping the first one

    # Test getting public builds using the dedicated method
    public_builds = crud.get_public_builds(db)
    assert len(public_builds) >= 2  # At least 2 public builds (from both users)
