"""
Comprehensive tests for Build CRUD operations.
Tests for app/crud/build.py to achieve 80%+ coverage.

Note: Using synchronous methods (create, get, update, delete) as per CRUDBase implementation.
"""

import pytest
from sqlalchemy.orm import Session
from app.crud.build import CRUDBuild
from app.models.build import Build
from app.models.user import User
from app.models.profession import Profession
from app.schemas.build import BuildCreate, BuildUpdate


@pytest.fixture
def db(db_session: Session) -> Session:
    """Alias fixture to use `db` consistently in tests.

    The CRUD test suite in this folder provides `db_session` in `conftest.py`.
    This alias keeps test signatures simple and consistent across files.
    """
    return db_session


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_profession(db: Session):
    """Create a test profession."""
    profession = Profession(
        name="Guardian", description="A heavy armor profession", armor_type="Heavy"
    )
    db.add(profession)
    db.commit()
    db.refresh(profession)
    return profession


@pytest.fixture
def crud_build():
    """Create CRUDBuild instance."""
    return CRUDBuild(Build)


class TestCRUDBuildCreate:
    """Test Build creation operations."""

    def test_create_build_basic(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test creating a basic build."""
        build_data = BuildCreate(
            name="Test Build",
            description="A test build description",
            profession_id=test_profession.id,
            is_public=True,
        )

        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()
        db.refresh(build)

        assert build.id is not None
        assert build.name == "Test Build"
        assert build.description == "A test build description"
        assert build.profession_id == test_profession.id
        assert build.is_public is True
        assert build.created_by_id == test_user.id

    def test_create_build_with_all_fields(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test creating a build with all optional fields."""
        build_data = BuildCreate(
            name="Complete Build",
            description="A complete build with all fields",
            profession_id=test_profession.id,
            specialization_ids=[],
            skills={
                "heal": "Shelter",
                "utility1": "Stand Your Ground",
                "utility2": "Hold the Line",
                "utility3": "Save Yourselves",
                "elite": "Renewed Focus",
            },
            traits={},
            equipment={},
            is_public=True,
            tags=["wvw", "support"],
        )

        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()
        db.refresh(build)

        assert build.id is not None
        assert build.name == "Complete Build"
        assert build.skills["heal"] == "Shelter"
        assert build.is_public is True

    def test_create_build_private(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test creating a private build."""
        build_data = BuildCreate(
            name="Private Build",
            description="A private build",
            profession_id=test_profession.id,
            is_public=False,
        )

        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()
        db.refresh(build)

        assert build.is_public is False


class TestCRUDBuildRead:
    """Test Build read operations."""

    def test_get_build_by_id(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test getting a build by ID."""
        build_data = BuildCreate(name="Test Build", profession_id=test_profession.id)
        created_build = crud_build.create(db, obj_in=build_data)
        created_build.created_by_id = test_user.id
        db.commit()

        retrieved_build = crud_build.get(db, id=created_build.id)

        assert retrieved_build is not None
        assert retrieved_build.id == created_build.id
        assert retrieved_build.name == "Test Build"

    def test_get_build_nonexistent(self, db: Session, crud_build: CRUDBuild):
        """Test getting a non-existent build."""
        build = crud_build.get(db, id=99999)
        assert build is None

    def test_get_multi_builds(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test getting multiple builds."""
        for i in range(3):
            build_data = BuildCreate(
                name=f"Build {i}", profession_id=test_profession.id
            )
            build = crud_build.create(db, obj_in=build_data)
            build.created_by_id = test_user.id
        db.commit()

        builds = crud_build.get_multi(db, skip=0, limit=10)

        assert len(builds) >= 3

    def test_get_multi_by_owner(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test getting builds by owner."""
        for i in range(2):
            build_data = BuildCreate(
                name=f"Owner Build {i}", profession_id=test_profession.id
            )
            build = crud_build.create(db, obj_in=build_data)
            build.created_by_id = test_user.id
        db.commit()

        builds = crud_build.get_multi_by_owner(db, owner_id=test_user.id)

        assert len(builds) >= 2
        for build in builds:
            assert build.created_by_id == test_user.id


class TestCRUDBuildUpdate:
    """Test Build update operations."""

    def test_update_build_name(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test updating a build's name."""
        build_data = BuildCreate(name="Original Name", profession_id=test_profession.id)
        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()

        update_data = BuildUpdate(name="Updated Name")
        updated_build = crud_build.update(db, db_obj=build, obj_in=update_data)

        assert updated_build.name == "Updated Name"

    def test_update_build_multiple_fields(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test updating multiple fields."""
        build_data = BuildCreate(
            name="Original",
            description="Original description",
            profession_id=test_profession.id,
            is_public=False,
        )
        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()

        update_data = BuildUpdate(
            name="Updated", description="Updated description", is_public=True
        )
        updated_build = crud_build.update(db, db_obj=build, obj_in=update_data)

        assert updated_build.name == "Updated"
        assert updated_build.description == "Updated description"
        assert updated_build.is_public is True

    def test_update_build_skills(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test updating build skills."""
        build_data = BuildCreate(
            name="Skills Build",
            profession_id=test_profession.id,
            skills={"heal": "Shelter"},
        )
        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()

        new_skills = {"heal": "Litany of Wrath", "utility1": "Smite Condition"}
        update_data = BuildUpdate(skills=new_skills)
        updated_build = crud_build.update(db, db_obj=build, obj_in=update_data)

        assert updated_build.skills["heal"] == "Litany of Wrath"
        assert updated_build.skills["utility1"] == "Smite Condition"


class TestCRUDBuildDelete:
    """Test Build delete operations."""

    def test_delete_build(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test deleting a build."""
        build_data = BuildCreate(name="To Delete", profession_id=test_profession.id)
        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()
        build_id = build.id

        deleted_build = crud_build.remove(db, id=build_id)

        assert deleted_build.id == build_id
        assert crud_build.get(db, id=build_id) is None

    def test_delete_nonexistent_build(self, db: Session, crud_build: CRUDBuild):
        """Test deleting a non-existent build."""
        result = crud_build.remove(db, id=99999)
        assert result is None


class TestCRUDBuildFiltering:
    """Test Build filtering operations."""

    def test_filter_public_builds(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test filtering public builds."""
        for i, is_public in enumerate([True, False, True]):
            build_data = BuildCreate(
                name=f"Build {i}", profession_id=test_profession.id, is_public=is_public
            )
            build = crud_build.create(db, obj_in=build_data)
            build.created_by_id = test_user.id
        db.commit()

        public_builds = crud_build.get_multi(db, is_public=True)

        assert len(public_builds) >= 2
        for build in public_builds:
            assert build.is_public is True

    def test_filter_by_profession(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test filtering builds by profession."""
        for i in range(2):
            build_data = BuildCreate(
                name=f"Guardian Build {i}", profession_id=test_profession.id
            )
            build = crud_build.create(db, obj_in=build_data)
            build.created_by_id = test_user.id
        db.commit()

        builds = crud_build.get_multi(db, profession_id=test_profession.id)

        assert len(builds) >= 2
        for build in builds:
            assert build.profession_id == test_profession.id


class TestCRUDBuildPagination:
    """Test Build pagination."""

    def test_pagination(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test pagination with skip and limit."""
        for i in range(5):
            build_data = BuildCreate(
                name=f"Paginated Build {i}", profession_id=test_profession.id
            )
            build = crud_build.create(db, obj_in=build_data)
            build.created_by_id = test_user.id
        db.commit()

        page1 = crud_build.get_multi(db, skip=0, limit=2)
        page2 = crud_build.get_multi(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id


class TestCRUDBuildEdgeCases:
    """Test Build edge cases."""

    def test_create_build_without_description(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test creating a build without description."""
        build_data = BuildCreate(
            name="No Description", profession_id=test_profession.id
        )

        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()

        assert build.description is None or build.description == ""

    def test_update_with_empty_data(
        self,
        db: Session,
        crud_build: CRUDBuild,
        test_user: User,
        test_profession: Profession,
    ):
        """Test updating with empty data."""
        build_data = BuildCreate(name="Original", profession_id=test_profession.id)
        build = crud_build.create(db, obj_in=build_data)
        build.created_by_id = test_user.id
        db.commit()
        original_name = build.name

        update_data = BuildUpdate()
        updated_build = crud_build.update(db, db_obj=build, obj_in=update_data)

        assert updated_build.name == original_name
