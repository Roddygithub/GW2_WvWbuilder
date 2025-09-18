""Tests for database models and their relationships."""
import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

# Import the models after setting up the test database
from app.models.base_models import (
    Base, User, Role, Profession, EliteSpecialization, Build, 
    Composition, CompositionTag, user_roles, composition_members, build_profession
)
from app.core.security import get_password_hash

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

def setup_test_database():
    """Set up a test database with all tables."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Enable foreign key constraints for SQLite
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('PRAGMA foreign_keys=ON')
    
    from sqlalchemy import event
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    
    # Drop all tables if they exist
    Base.metadata.drop_all(engine)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create a session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, TestingSessionLocal

# Set up the test database once per test session
engine, TestingSessionLocal = setup_test_database()

# Fixture to get a database session for each test
@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Clean up after the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_role(db_session):
    """Create a test role."""
    role = Role(
        name=f"test_role_{uuid.uuid4().hex[:8]}",
        description="Test role",
        permission_level=1,
        is_default=False
    )
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def test_user(db_session, test_role):
    """Create a test user with a role."""
    user = User(
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    user.roles.append(test_role)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_profession(db_session):
    """Create a test profession."""
    profession = Profession(
        name=f"test_prof_{uuid.uuid4().hex[:8]}",
        display_name="Test Profession",
        description="A test profession",
        icon_url="https://example.com/icon.png"
    )
    db_session.add(profession)
    db_session.commit()
    return profession


@pytest.fixture
def test_elite_specialization(db_session, test_profession):
    """Create a test elite specialization."""
    spec = EliteSpecialization(
        name=f"test_espec_{uuid.uuid4().hex[:8]}",
        display_name="Test Elite Spec",
        description="A test elite specialization",
        icon_url="https://example.com/espec.png",
        profession_id=test_profession.id
    )
    db_session.add(spec)
    db_session.commit()
    return spec


@pytest.fixture
def test_build(db_session, test_user, test_profession, test_elite_specialization):
    """Create a test build."""
    build = Build(
        name=f"Test Build {uuid.uuid4().hex[:8]}",
        description="A test build",
        game_mode="wvw",
        is_public=True,
        created_by=test_user.id,
        profession_id=test_profession.id,
        elite_specialization_id=test_elite_specialization.id,
        build_link="http://example.com/build"
    )
    db_session.add(build)
    db_session.commit()
    return build


@pytest.fixture
def test_composition(db_session, test_user, test_build):
    """Create a test composition."""
    composition = Composition(
        name=f"Test Composition {uuid.uuid4().hex[:8]}",
        description="A test composition",
        game_mode="wvw",
        is_public=True,
        created_by=test_user.id
    )
    composition.builds.append(test_build)
    db_session.add(composition)
    db_session.commit()
    return composition

def test_user_model(db_session):
    """Test User model creation and validation."""
    # Create a unique username and email for this test
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "hashed_password": get_password_hash("testpassword"),
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    
    # Verify the user was created successfully
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.full_name == user_data["full_name"]
    assert user.hashed_password == user_data["hashed_password"]
    assert user.is_active == user_data["is_active"]
    assert user.is_superuser == user_data["is_superuser"]
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.last_login is None
    
    # Test string representation
    assert str(user) == f"<User {user_data['email']}>"
    
    # Test email validation
    with pytest.raises(ValueError):
        user.email = "invalid-email"
    
    # Test username validation
    with pytest.raises(ValueError):
        user.username = "user@name"  # No @ allowed in username

def test_role_model(db_session):
    """Test Role model creation and validation."""
    # Create a unique role name for this test
    unique_id = str(uuid.uuid4())[:8]
    role_data = {
        "name": f"test_role_{unique_id}",
        "description": "Test role description",
        "permission_level": 1,
        "is_default": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    role = Role(**role_data)
    db_session.add(role)
    db_session.commit()
    
    # Verify the role was created successfully
    assert role.id is not None
    assert role.name == role_data["name"]
    assert role.description == role_data["description"]
    assert role.permission_level == role_data["permission_level"]
    assert role.is_default == role_data["is_default"]
    assert role.created_at is not None
    assert role.updated_at is not None
    
    # Test string representation
    assert str(role) == f"<Role {role_data['name']}>"
    
    # Test unique constraint on name
    duplicate_role = Role(**role_data)
    db_session.add(duplicate_role)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    
    # Test permission level validation
    with pytest.raises(ValueError):
        role.permission_level = -1
    
    # Test name validation
    with pytest.raises(ValueError):
        role.name = "invalid name with spaces"


def test_profession_model(db_session):
    """Test Profession model creation and validation."""
    # Create test data
    profession_data = {
        "name": "Guardian",
        "display_name": "Guardian",
        "description": "A holy warrior with protective abilities",
        "icon_url": "https://example.com/guardian.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    profession = Profession(**profession_data)
    db_session.add(profession)
    db_session.commit()
    
    # Verify the profession was created successfully
    assert profession.id is not None
    assert profession.name == profession_data["name"]
    assert profession.display_name == profession_data["display_name"]
    assert profession.description == profession_data["description"]
    assert profession.icon_url == profession_data["icon_url"]
    assert profession.created_at is not None
    assert profession.updated_at is not None
    
    # Test string representation
    assert str(profession) == f"<Profession {profession_data['name']}>"
    
    # Test unique constraint on name
    duplicate_profession = Profession(**profession_data)
    db_session.add(duplicate_profession)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    
    # Test name validation
    with pytest.raises(ValueError):
        profession.name = "Invalid Name With Spaces"
    
    # Test display_name validation
    with pytest.raises(ValueError):
        profession.display_name = ""  # Empty display name not allowed


def test_elite_specialization_model(db_session, test_profession):
    """Test EliteSpecialization model creation and validation."""
    # Create test data
    spec_data = {
        "name": "Dragonhunter",
        "display_name": "Dragonhunter",
        "description": "A long-range specialist with traps and virtues",
        "icon_url": "https://example.com/dragonhunter.png",
        "profession_id": test_profession.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    spec = EliteSpecialization(**spec_data)
    db_session.add(spec)
    db_session.commit()
    
    # Verify the elite specialization was created successfully
    assert spec.id is not None
    assert spec.name == spec_data["name"]
    assert spec.display_name == spec_data["display_name"]
    assert spec.description == spec_data["description"]
    assert spec.icon_url == spec_data["icon_url"]
    assert spec.profession_id == test_profession.id
    assert spec.created_at is not None
    assert spec.updated_at is not None
    
    # Test string representation
    assert str(spec) == f"<EliteSpecialization {spec_data['name']}>"
    
    # Test relationship with profession
    assert spec.profession == test_profession
    assert spec in test_profession.elite_specializations
    
    # Test unique constraint on name within profession
    duplicate_spec = EliteSpecialization(**spec_data)
    db_session.add(duplicate_spec)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_build_model(db_session, test_user, test_profession, test_elite_specialization):
    """Test Build model creation and validation."""
    # Create test data
    build_data = {
        "name": "Support Firebrand",
        "description": "A support-focused Firebrand build for WvW",
        "game_mode": "wvw",
        "is_public": True,
        "created_by": test_user.id,
        "profession_id": test_profession.id,
        "elite_specialization_id": test_elite_specialization.id,
        "build_link": "http://example.com/build/123",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    build = Build(**build_data)
    db_session.add(build)
    db_session.commit()
    
    # Verify the build was created successfully
    assert build.id is not None
    assert build.name == build_data["name"]
    assert build.description == build_data["description"]
    assert build.game_mode == build_data["game_mode"]
    assert build.is_public == build_data["is_public"]
    assert build.created_by == test_user.id
    assert build.profession_id == test_profession.id
    assert build.elite_specialization_id == test_elite_specialization.id
    assert build.build_link == build_data["build_link"]
    assert build.created_at is not None
    assert build.updated_at is not None
    
    # Test string representation
    assert str(build) == f"<Build {build_data['name']}>"
    
    # Test relationships
    assert build.creator == test_user
    assert build in test_user.builds
    assert build.profession == test_profession
    assert build.elite_specialization == test_elite_specialization
    
    # Test game mode validation
    with pytest.raises(ValueError):
        build.game_mode = "invalid_game_mode"
    
    # Test build link validation
    with pytest.raises(ValueError):
        build.build_link = "not_a_url"


def test_composition_model(db_session, test_user, test_build):
    """Test Composition model creation and validation."""
    # Create test data
    composition_data = {
        "name": "WvW Zerg Composition",
        "description": "A balanced WvW zerg composition",
        "game_mode": "wvw",
        "is_public": True,
        "created_by": test_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    composition = Composition(**composition_data)
    composition.builds.append(test_build)
    db_session.add(composition)
    db_session.commit()
    
    # Verify the composition was created successfully
    assert composition.id is not None
    assert composition.name == composition_data["name"]
    assert composition.description == composition_data["description"]
    assert composition.game_mode == composition_data["game_mode"]
    assert composition.is_public == composition_data["is_public"]
    assert composition.created_by == test_user.id
    assert composition.created_at is not None
    assert composition.updated_at is not None
    
    # Test string representation
    assert str(composition) == f"<Composition {composition_data['name']}>"
    
    # Test relationships
    assert composition.creator == test_user
    assert composition in test_user.compositions
    assert test_build in composition.builds
    assert composition in test_build.compositions
    
    # Test game mode validation
    with pytest.raises(ValueError):
        composition.game_mode = "invalid_game_mode"


def test_composition_tag_model(db_session, test_composition):
    """Test CompositionTag model creation and validation."""
    # Create test data
    tag_data = {
        "name": "zerg",
        "composition_id": test_composition.id,
        "created_at": datetime.utcnow()
    }
    
    # Test creation with required fields
    tag = CompositionTag(**tag_data)
    db_session.add(tag)
    db_session.commit()
    
    # Verify the tag was created successfully
    assert tag.id is not None
    assert tag.name == tag_data["name"]
    assert tag.composition_id == test_composition.id
    assert tag.created_at is not None
    
    # Test string representation
    assert str(tag) == f"<CompositionTag {tag_data['name']}>"
    
    # Test relationship with composition
    assert tag.composition == test_composition
    assert tag in test_composition.tags
    
    # Test unique constraint on (name, composition_id)
    duplicate_tag = CompositionTag(**tag_data)
    db_session.add(duplicate_tag)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    
    # Test name validation
    with pytest.raises(ValueError):
        tag.name = "invalid tag name with spaces"
    
    # Create a unique profession name for this test
    unique_id = str(uuid.uuid4())[:8]
    profession_name = f"test_profession_{unique_id}"
    
    profession = Profession(
        name=profession_name,
        description="Test profession description",
        icon_url="http://example.com/icon.png",
        game_modes=["WvW", "PvP"]
    )
    
    db_session.add(profession)
    db_session.commit()
    
    # Verify the profession was created successfully
    assert profession.id is not None
    assert profession.name == profession_name
    assert profession.description == "Test profession description"
    assert profession.icon_url == "http://example.com/icon.png"
    assert profession.game_modes == ["WvW", "PvP"]

def test_user_role_relationship(db_session):
    """Test the relationship between user and role."""
    # Create unique test data
    unique_id = str(uuid.uuid4())[:8]
    role_name = f"test_role_{unique_id}"
    username = f"testuser_{unique_id}"
    email = f"{username}@example.com"
    
    # Create a role
    role = Role(
        name=role_name,
        description="Test role for user relationship",
        permission_level=1,
        is_default=False
    )
    db_session.add(role)
    db_session.commit()  # Commit the role first to get an ID
    
    # Create a user
    user = User(
        email=email,
        username=username,
        hashed_password="testpassword",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()  # Commit the user to get an ID
    
    # Manually add the user-role association
    stmt = user_roles.insert().values(user_id=user.id, role_id=role.id)
    db_session.execute(stmt)
    db_session.commit()
    
    # Refresh the objects to get the updated relationships
    db_session.refresh(user)
    db_session.refresh(role)
    
    # Verify the relationship was established
    assert len(user.roles) == 1
    assert user.roles[0].id == role.id
    assert user.roles[0].name == role_name
    
    # Verify the back-populated relationship
    assert len(role.users) == 1
    assert role.users[0].id == user.id
    assert role.users[0].username == username

def test_unique_constraint_violation(db_session):
    """Test the unique constraint on email."""
    from app.models.base_models import User, Role
    
    # Create unique test data
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    
    # Create a role first (required by User model constraints)
    role = Role(
        name=f"test_role_{unique_id}",
        description="Test role",
        permission_level=1,
        is_default=False
    )
    db_session.add(role)
    db_session.commit()
    
    # Create first user
    user1 = User(
        email=email,
        username=f"user1_{unique_id}",
        hashed_password="password123",
        is_active=True,
        is_superuser=False,
    )
    user1.roles.append(role)
    db_session.add(user1)
    db_session.commit()
    
    # Try to create a second user with the same email
    with pytest.raises(IntegrityError):
        user2 = User(
            email=email,  # Same email as user1
            username=f"user2_{unique_id}",
            hashed_password="password456",
            is_active=True,
            is_superuser=False,
        )
        user2.roles.append(role)
        db_session.add(user2)
        db_session.commit()
    
    # Annuler la transaction pour éviter de polluer la base de données
    db_session.rollback()
