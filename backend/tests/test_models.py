"""Tests pour les modèles de base de données."""
import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import sessionmaker, Session

# Import the models after setting up the test database
from app.models.base_models import Base, User, Role, Profession, EliteSpecialization, Build, Composition, CompositionTag
from app.models.base_models import user_roles, composition_members, build_profession

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

def test_user_model(db_session):
    """Test de création d'un utilisateur."""
    # Create a unique username and email for this test
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "hashed_password": "testpassword",
        "is_active": True,
        "is_superuser": False
    }
    
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=user_data["hashed_password"],
        is_active=user_data["is_active"],
        is_superuser=user_data["is_superuser"],
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Verify the user was created successfully
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.is_active == user_data["is_active"]
    assert user.is_superuser == user_data["is_superuser"]

def test_role_model(db_session):
    """Test de création d'un rôle."""
    
    # Create a unique role name for this test
    unique_id = str(uuid.uuid4())[:8]
    role_name = f"test_role_{unique_id}"
    
    role = Role(
        name=role_name,
        description="Test role description",
        permission_level=1,
        is_default=False
    )
    
    db_session.add(role)
    db_session.commit()
    
    # Verify the role was created successfully
    assert role.id is not None
    assert role.name == role_name
    assert role.description == "Test role description"
    assert role.permission_level == 1
    assert role.is_default is False

def test_profession_model(db_session):
    """Test de création d'une profession."""
    
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
    """Test de la relation entre utilisateur et rôle."""
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
    """Test de la contrainte d'unicité sur l'email."""
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
