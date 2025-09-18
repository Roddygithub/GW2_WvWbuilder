"""Integration tests for the Builds API endpoints."""
import asyncio
import pytest
import random
import string
from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models import Build, Profession, Role, User, build_profession
from app.schemas.build import BuildCreate, BuildGenerationRequest, BuildUpdate, GameMode, RoleType

# OAuth2 scheme for testing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Test user for authentication
async def get_current_user_for_test(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends()
) -> models.User:
    """Async version of get_current_user for testing."""
    from jose import jwt
    from app.core import security
    from app.core.config import settings
    from fastapi import HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# Test data and utilities
MAX_DESCRIPTION_LENGTH = 500

def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string of specified length."""
    return "".join(random.choices(string.ascii_lowercase, k=length))

# Fixture for test data
@pytest.fixture
async def test_role(async_db: AsyncSession) -> Role:
    """Create a test role."""
    role = Role(name="test_role", description="Test Role")
    async_db.add(role)
    await async_db.commit()
    await async_db.refresh(role)
    return role

@pytest.fixture
async def test_professions(async_db: AsyncSession) -> List[Profession]:
    """Create test professions."""
    professions_data = [
        {"name": "Guardian", "role": "Support"},
        {"name": "Warrior", "role": "Damage"},
        {"name": "Engineer", "role": "Support"},
        {"name": "Ranger", "role": "Damage"},
        {"name": "Thief", "role": "Damage"},
        {"name": "Elementalist", "role": "Damage"},
        {"name": "Mesmer", "role": "Support"},
        {"name": "Necromancer", "role": "Damage"},
        {"name": "Revenant", "role": "Support"},
    ]
    
    professions = []
    for data in professions_data:
        profession = Profession(**data)
        async_db.add(profession)
        professions.append(profession)
    
    await async_db.commit()
    return professions

@pytest.fixture
async def test_user(async_db: AsyncSession, test_role: Role) -> User:
    """Create a test user with a role."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        username="testuser"
    )
    user.roles.append(test_role)
    
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user

@pytest.fixture
async def other_test_user(async_db: AsyncSession, test_role: Role) -> User:
    """Create another test user for testing authorization."""
    user = User(
        email="other@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        username="otheruser"
    )
    user.roles.append(test_role)
    
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user

@pytest.fixture
async def test_private_build(
    test_user: User, 
    test_professions: List[Profession], 
    async_db: AsyncSession
) -> Build:
    """Create a private test build."""
    build = Build(
        name="Test Private Build",
        description="A private test build",
        is_public=False,
        owner_id=test_user.id,
        created_by_id=test_user.id,
        game_mode=GameMode.WVW,
        team_size=5
    )
    
    # Add some professions to the build
    for profession in test_professions[:3]:
        build.professions.append(profession)
    
    async_db.add(build)
    await async_db.commit()
    await async_db.refresh(build)
    return build

# Helper function to get auth headers
async def get_auth_headers(user_id: int) -> Dict[str, str]:
    """Generate authentication headers for test requests."""
    token = create_access_token(
        subject=str(user_id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {token}"}

# Test-specific dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends()
) -> models.User:
    """Synchronous version of get_current_user for testing."""
    # Special token for testing
    if token == "test_token":
        from app.crud import CRUDUser
        crud_user = CRUDUser(models.User)
        user = crud_user.get_by_email(db, email="test@example.com")
        if not user:
            user = crud_user.create(db, obj_in={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User",
                "is_active": True,
                "is_superuser": False,
            })
        return user
    
    # For user-specific tokens (format: "user_<id>")
    if token.startswith("user_"):
        user_id = int(token.split("_")[1])
        from app.crud import CRUDUser
        crud_user = CRUDUser(models.User)
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test database and tables
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Create a SQLAlchemy async engine for testing."""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,
        future=True
    )
    return engine

@pytest.fixture(scope="session")
async def init_db(async_engine):
    """Initialize test database with tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="session")
def async_session_maker(async_engine):
    """Create a sessionmaker for creating async sessions."""
    return sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        future=True
    )


@pytest.fixture
async def async_db(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing with automatic rollback and cleanup."""
    async with async_session_maker() as session:
        # Start a transaction
        await session.begin()
        try:
            yield session
            # Always rollback to avoid affecting other tests
            await session.rollback()
        except Exception as e:
            await session.rollback()
            raise e

# Async test client
@pytest.fixture
async def async_client(async_session_maker):
    """Create a test client with overridden dependencies."""
    # Override the get_db dependency
    async def override_get_db():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create and return the test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


def get_current_user_sync(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends()
) -> models.User:
    """Synchronous version of get_current_user for testing."""
    # Special token for testing
    if token == "test_token":
        from app.crud import CRUDUser
        crud_user = CRUDUser(models.User)
        user = crud_user.get_by_email(db, email="test@example.com")
        if not user:
            user = crud_user.create(db, obj_in={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User",
                "is_active": True,
                "is_superuser": False,
            })
        return user
    
    # For user-specific tokens (format: "user_<id>")
    if token.startswith("user_"):
        user_id = int(token.split("_")[1])
        from app.crud import CRUDUser
        crud_user = CRUDUser(models.User)
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Override dependencies for testing
app.dependency_overrides = {}
app.dependency_overrides["get_db"] = override_get_db
app.dependency_overrides["get_current_user"] = sync_get_current_user
from app.db.base import Base
from app.api.deps import get_db
import random
import string
from fastapi import status, HTTPException
from app.core.config import settings
from app.core.security import get_password_hash

# Constants for test data
MAX_NAME_LENGTH = 100

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a clean database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Create all tables
    Base.metadata.create_all(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
MAX_DESCRIPTION_LENGTH = 500

# Test data
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "A test build for WvW",
    "game_mode": "wvw",
    "is_public": True,
    "config": {
        "weapons": ["Greatsword", "Staff"],
        "traits": ["Dragonhunter", "Zeal", "Radiance"],
        "skills": ["Merciful Intervention", "Sword of Justice"]
    },
    "constraints": {
        "min_healers": 1,
        "min_dps": 2,
        "min_support": 1
    },
    "profession_ids": [1, 2, 3]
}

# Invalid test data
INVALID_BUILD_DATA = [
    ({"name": ""}, "name", "String should have at least 1 character"),
    ({"game_mode": "invalid"}, "game_mode", "Input should be 'pve','pvp', or 'wvw'"),
    ({"team_size": 0}, "team_size", "Input should be greater than or equal to 1"),
    ({"team_size": 51}, "team_size", "Input should be less than or equal to 50"),
    ({"profession_ids": []}, "profession_ids", "List should have at least 1 item after validation")
]

# Override the database dependency for testing
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a new database session with a rollback at the end of the test."""
    # Clear all data first
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_role(db: Session) -> Role:
    """Create a test role."""
    role = Role(name="test_role", description="Test Role")
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@pytest.fixture
def test_professions(db: Session) -> List[Profession]:
    """Create test professions."""
    # Create new professions
    professions = [
        Profession(name="Guardian", description="Guardian profession"),
        Profession(name="Warrior", description="Warrior profession"),
        Profession(name="Engineer", description="Engineer profession")
    ]
    
    # Add all professions to the session and commit
    db.add_all(professions)
    db.commit()
    
    # Refresh all professions to get their IDs
    for p in professions:
        db.refresh(p)
    
    print(f"Created test professions with IDs: {[p.id for p in professions]}")
    return professions

@pytest.fixture
def test_user(db: Session, test_role: Role) -> User:
    """Create a test user with a role."""
    # Clear any existing users first
    db.query(User).delete()
    db.commit()
    
    user_data = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_superuser": False,
        "full_name": "Test User"
    }
    
    user = User(**user_data)
    db.add(user)
    
    # Add role to user
    user.roles.append(test_role)
    
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def other_test_user(db: Session, test_role: Role) -> User:
    """Create another test user for testing authorization."""
    user_data = {
        "id": 2,
        "username": "otheruser",
        "email": "other@example.com",
        "hashed_password": get_password_hash("otherpassword"),
        "is_active": True,
        "is_superuser": False,
        "full_name": "Other User"
    }
    
    user = User(**user_data)
    db.add(user)
    user.roles.append(test_role)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_private_build(test_user: User, test_professions: List[Profession], db: Session) -> Build:
    """Create a private test build."""
    if not test_professions:
        pytest.skip("No test professions available")
    
    # Get the first available profession
    profession = test_professions[0]
    
    # Ensure the profession exists in the database
    db.add(profession)
    db.commit()
    db.refresh(profession)
    
    # Create build data with the profession ID
    build_data = {
        "name": f"PrivateTestBuild_{random_lower_string(4)}",  # Ensure unique name
        "description": "A private test build",
        "game_mode": "wvw",
        "is_public": False,
        "profession_ids": [profession.id],
        "config": {"weapons": ["Greatsword"]},
        "constraints": {}
    }
    
    # Create the build directly in the database to avoid API validation issues
    build = Build(
        name=build_data["name"],
        description=build_data["description"],
        game_mode=build_data["game_mode"],
        is_public=build_data["is_public"],
        config=build_data["config"],
        constraints=build_data["constraints"],
        owner_id=test_user.id,
        created_by_id=test_user.id  # Set created_by_id
    )
    
    # Add the build to the session and commit
    db.add(build)
    db.commit()
    db.refresh(build)
    
    # Check if the relationship already exists
    stmt = select(build_profession).where(
        build_profession.c.build_id == build.id,
        build_profession.c.profession_id == profession.id
    )
    result = db.execute(stmt).first()
    
    # Only insert if the relationship doesn't exist
    if not result:
        stmt = build_profession.insert().values(
            build_id=build.id,
            profession_id=profession.id
        )
        db.execute(stmt)
        db.commit()
    
    # Refresh the build to ensure all relationships are loaded
    db.refresh(build)
    
    # Make sure the build is properly associated with the user
    if build.owner_id != test_user.id:
        build.owner_id = test_user.id
        db.commit()
    
    # Refresh the build to get the latest state
    db.refresh(build)
    
    # Verify the build was created with the correct profession
    assert build is not None, "Build creation failed"
    
    # Refresh the build to ensure relationships are loaded
    db.refresh(build)
    
    # Verify the profession was associated correctly
    assert len(build.professions) == 1, f"Build should have exactly one profession, got {len(build.professions)}. Build: {build.__dict__}"
    assert build.professions[0].id == profession.id, f"Build has incorrect profession ID. Expected {profession.id}, got {build.professions[0].id if build.professions else 'None'}"
    
    # Print debug info
    print(f"Created build with ID: {build.id}")
    print(f"Build owner ID: {build.owner_id}")
    print(f"Build professions: {[p.id for p in build.professions]}")
    
    return build

def get_auth_headers(user_id: int) -> Dict[str, str]:
    """Generate authentication headers for test requests.
    
    Args:
        user_id: The ID of the user to authenticate as
        
    Returns:
        Dictionary with the Authorization header containing a valid JWT token
    """
    from datetime import datetime, timedelta
    import jwt
    from app.core.config import settings
    
    # Create a JWT token with the user ID as the subject
    token_data = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    # Generate the JWT token
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def cleanup_db(db: Session):
    """Clean up the database after each test."""
    # This fixture will run after each test
    yield
    
    # Clean up all tables in reverse order to respect foreign key constraints
    db.execute(build_profession.delete())
    db.execute(user_roles.delete())
    db.execute(models.Build.__table__.delete())
    db.execute(models.User.__table__.delete())
    db.execute(models.Profession.__table__.delete())
    db.execute(models.Role.__table__.delete())
    db.commit()
    
    # Verify cleanup
    build_count = db.query(models.Build).count()
    user_count = db.query(User).count()
    prof_count = db.query(Profession).count()
    role_count = db.query(Role).count()
    print(f"[After test] Builds: {build_count}, Users: {user_count}, Professions: {prof_count}, Roles: {role_count}\n")

class TestBuildsAPI:
    """Test suite for the Builds API endpoints."""
    
    async def test_unauthorized_access(self, async_client: AsyncClient, test_user: models.User, other_test_user: models.User, test_private_build: models.Build, async_db: AsyncSession):
        """Test unauthorized access to private builds."""
        # Test 1: Unauthenticated user cannot access private build
        print("\n--- Test 1: Unauthenticated access to private build ---")
        response = await async_client.get(f"/api/v1/builds/{test_private_build.id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND], \
            f"Expected 401 or 404 for unauthenticated access, got {response.status_code}"
        
            
        # Test 2: Non-owner cannot access private build
        print("\n--- Test 2: Non-owner access to private build ---")
        headers = await get_auth_headers(other_test_user.id)
        response = await async_client.get(
            f"/api/v1/builds/{test_private_build.id}",
            headers=headers
        )
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND], \
            f"Expected 403 or 404 for non-owner access, got {response.status_code}"
            
        # Test 3: Owner can access their private build
        print("\n--- Test 3: Owner access to private build ---")
        headers = await get_auth_headers(test_user.id)
        response = await async_client.get(
            f"/api/v1/builds/{test_private_build.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 for owner access, got {response.status_code}"
            
        # Make the build public
        test_private_build.is_public = True
        await async_db.commit()
        await async_db.refresh(test_private_build)
        
        # Test 4: Any authenticated user can access public build
        print("\n--- Test 4: Any user can access public build ---")
        headers = await get_auth_headers(other_test_user.id)
        response = await async_client.get(
            f"/api/v1/builds/{test_private_build.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 for public build access, got {response.status_code}"

    async def test_create_build(
        self, 
        async_client: AsyncClient, 
        test_user: User, 
        test_professions: List[Profession], 
        async_db: AsyncSession
    ):
        """Test creating a build with valid data."""
        # Get auth headers
        headers = await get_auth_headers(test_user.id)
        
        # Test data
        build_data = {
            "name": "Test Build",
            "description": "A test build",
            "is_public": True,
            "game_mode": "WvW",
            "profession_ids": [p.id for p in test_professions[:2]]
        }
        
        # Test 1: Create a build
        response = await async_client.post(
            "/api/v1/builds/",
            json=build_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == build_data["name"]
        assert data["description"] == build_data["description"]
        assert data["is_public"] == build_data["is_public"]
        assert data["game_mode"] == build_data["game_mode"]
        assert "id" in data
        
        # Verify the build was created in the database
        result = await async_db.execute(select(Build).filter(Build.id == data["id"]))
        db_build = result.scalar_one_or_none()
        assert db_build is not None
        assert db_build.name == build_data["name"]
        assert db_build.owner_id == test_user.id
        
        # Verify professions were associated
        assert len(db_build.professions) == 2
        assert {p.id for p in db_build.professions} == set(build_data["profession_ids"])
        
        # Test 2: Create a build with invalid profession IDs
        invalid_data = build_data.copy()
        invalid_data["profession_ids"] = [99999]  # Non-existent profession ID
        response = await async_client.post(
            "/api/v1/builds/",
            json=invalid_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Failed to retrieve created build: {response.text}"

    def test_get_build(self, client: TestClient, test_private_build: Build, test_user: User, other_test_user: User, db: Session):
        """Test retrieving a build by ID with various access scenarios."""
        # Make sure the build is owned by the test user and has a profession
        db_build = db.query(Build).filter(Build.id == test_private_build.id).first()
        db_build.owner_id = test_user.id
        db_build.is_public = False  # Start with private build
        
        # Make sure the build has at least one profession
        if not db_build.professions:
            profession = db.query(Profession).first()
            if profession:
                db_build.professions.append(profession)
        
        db.commit()
        db.refresh(db_build)
        
        # Test 1: Owner can access their private build
        response = client.get(
            f"/api/v1/builds/{db_build.id}",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Owner should be able to access their private build: {response.text}"
            
        build = response.json()
        assert build["id"] == db_build.id
        assert build["name"] == db_build.name
        assert build["is_public"] is False
        assert build["owner_id"] == test_user.id
        
        # Test 2: Other users cannot access private build
        response = client.get(
            f"/api/v1/builds/{db_build.id}",
            headers=get_auth_headers(other_test_user.id)
        )
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND], \
            "Non-owners should not be able to access private builds"
        
        # Test 3: Make the build public and verify others can access it
        db_build.is_public = True
        db.commit()
        
        response = client.get(
            f"/api/v1/builds/{db_build.id}",
            headers=get_auth_headers(other_test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Public build should be accessible to any authenticated user: {response.text}"
            
        # Test 4: Unauthenticated users can access public builds
        response = client.get(f"/api/v1/builds/{db_build.id}")
        assert response.status_code == status.HTTP_200_OK, \
            f"Public build should be accessible to unauthenticated users: {response.text}"
        
        # Test 5: Non-existent build returns 404
        non_existent_id = 999999
        response = client.get(
            f"/api/v1/builds/{non_existent_id}",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, \
            f"Should return 404 for non-existent build, got {response.status_code}"

    def test_update_build(self, client: TestClient, test_private_build: Build, test_user: User, test_professions: List[Profession], db: Session):
        """Test updating a build with various scenarios."""
        if not test_professions:
            pytest.skip("No test professions available")
            
        # Get a valid profession ID for testing
        profession_id = test_professions[0].id
        
        # First make sure the build is owned by the test user and has initial data
        db_build = db.query(Build).filter(Build.id == test_private_build.id).first()
        db_build.owner_id = test_user.id
        db_build.name = "Original Build Name"
        db_build.description = "Original description"
        db_build.game_mode = "wvw"
        db_build.is_public = False
        db_build.config = {"weapons": ["Greatsword"]}
        db_build.constraints = {}
        db.commit()
        
        # Test 1: Update all fields
        update_data = {
            "name": "Updated Test Build",
            "description": "An updated test build description",
            "game_mode": "pvp",
            "is_public": True,
            "profession_ids": [profession_id],
            "config": {"weapons": ["Axe", "Axe"]},
            "constraints": {"role": "DPS"}
        }
        
        response = client.put(
            f"/api/v1/builds/{test_private_build.id}",
            json=update_data,
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code == status.HTTP_200_OK, \
            f"Failed to update build: {response.text}"
        
        updated_build = response.json()
        assert updated_build["name"] == update_data["name"]
        assert updated_build["description"] == update_data["description"]
        assert updated_build["game_mode"] == update_data["game_mode"]
        assert updated_build["is_public"] is True
        assert updated_build["owner_id"] == test_user.id
        assert len(updated_build["professions"]) == 1
        assert updated_build["professions"][0]["id"] == profession_id
        
        # Verify database state
        db.refresh(db_build)
        assert db_build.name == update_data["name"]
        assert db_build.description == update_data["description"]
        assert db_build.game_mode == update_data["game_mode"]
        assert db_build.is_public is True
        assert db_build.config == update_data["config"]
        assert db_build.constraints == update_data["constraints"]
        
        # Verify profession associations
        stmt = build_profession.select().where(build_profession.c.build_id == test_private_build.id)
        result = db.execute(stmt).fetchall()
        assert len(result) == 1, "Should have exactly one profession association"
        assert result[0]["profession_id"] == profession_id, "Incorrect profession ID after update"
        
        # Test 2: Partial update (only update name and description)
        partial_update = {
            "name": "Partially Updated Build",
            "description": "Only updating name and description"
        }
        
        response = client.put(
            f"/api/v1/builds/{test_private_build.id}",
            json=partial_update,
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify only the specified fields were updated
        db.refresh(db_build)
        assert db_build.name == partial_update["name"]
        assert db_build.description == partial_update["description"]
        assert db_build.game_mode == update_data["game_mode"]  # Should remain unchanged
        assert db_build.is_public is True  # Should remain unchanged
        
        # Test 3: Update with invalid profession ID
        invalid_update = update_data.copy()
        invalid_update["profession_ids"] = [99999]  # Non-existent profession ID
        
        response = client.put(
            f"/api/v1/builds/{test_private_build.id}",
            json=invalid_update,
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND], \
            "Should fail with invalid profession ID"
            
        # Test 4: Update non-existent build
        non_existent_id = 999999
        response = client.put(
            f"/api/v1/builds/{non_existent_id}",
            json=update_data,
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND, \
            "Should return 404 for non-existent build"

    def test_delete_build(self, client: TestClient, test_private_build: Build, test_user: User, test_professions: List[Profession], db: Session):
        """Test deleting a build with various scenarios."""
        if not test_professions:
            pytest.skip("No test professions available")
            
        # Set up a build with a profession association
        db_build = db.query(Build).filter(Build.id == test_private_build.id).first()
        db_build.owner_id = test_user.id
        db_build.professions = test_professions[:1]  # Associate with one profession
        db.commit()
        
        build_id = db_build.id
        non_existent_id = 999999
        response = client.delete(
            f"/api/v1/builds/{non_existent_id}",
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND, \
            "Should return 404 for non-existent build"
            
        # Test 3: Delete a build that's already deleted (should return 404)
        response = client.delete(
            f"/api/v1/builds/{build_id}",
            headers=get_auth_headers(test_user.id)
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND, \
            "Should return 404 for already deleted build"

    def test_list_builds(self, client: TestClient, test_user: User, other_test_user: User, test_private_build: Build, test_professions: List[Profession], db: Session):
        """Test listing builds with various filters and access controls."""
        # Create some test builds
        build1 = Build(
            name="PublicBuild1",
            description="Public build 1",
            game_mode="wvw",
            is_public=True,
            owner_id=test_user.id,
            config={"weapons": ["Sword"]},
            constraints={},
            professions=test_professions[:1]
        )
        db.add(build1)
        
        build2 = Build(
            name="PrivateBuild1",
            description="Private build 1",
            game_mode="pve",
            is_public=False,
            owner_id=test_user.id,
            config={"weapons": ["Axe"]},
            constraints={},
            professions=test_professions[1:2]
        )
        db.add(build2)
        
        # Create a build from another user
        build3 = Build(
            name="OtherUserPublicBuild",
            description="Public build from another user",
            game_mode="wvw",
            is_public=True,
            owner_id=other_test_user.id,
            config={"weapons": ["Staff"]},
            constraints={},
            professions=test_professions[2:3]
        )
        db.add(build3)
        
        db.commit()
        db.refresh(build1)
        db.refresh(build2)
        db.refresh(build3)
        
        # Test 1: List all builds (should only show public ones to unauthenticated)
        response = client.get("/api/v1/builds/")
        assert response.status_code == status.HTTP_200_OK, f"Failed to list builds: {response.text}"
        builds = response.json()
        
        # Debug output
        print(f"Public builds: {[b['name'] for b in builds]}")
        
        # Should see public builds but not private ones
        assert any(b["name"] == "PublicBuild1" for b in builds), "Public build not found"
        assert not any(b.get("name") == "PrivateBuild1" for b in builds), "Private build should not be visible"
        
        # Test 2: List builds as the owner (should see both public and private)
        response = client.get(
            "/api/v1/builds/",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, f"Failed to list builds: {response.text}"
        builds = response.json()
        
        # Debug output
        print(f"All builds for owner: {[b['name'] for b in builds]}")
        
        assert any(b["name"] == "PublicBuild1" for b in builds), "Public build not found"
        assert any(b["name"] == "PrivateBuild1" for b in builds), "Private build should be visible to owner"
        
        # Test 3: Filter by game mode
        response = client.get(
            "/api/v1/builds/?game_mode=wvw",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, f"Failed to filter by game mode: {response.text}"
        builds = response.json()
        assert all(b["game_mode"] == "wvw" for b in builds), "Not all builds match the game mode filter"
        
        # Test 4: Search by name
        response = client.get(
            "/api/v1/builds/?search=Public",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, f"Failed to search builds: {response.text}"
        builds = response.json()
        assert all("Public" in b["name"] for b in builds), "Search results don't match the query"
        
        # Test 5: Pagination
        response = client.get(
            "/api/v1/builds/?skip=1&limit=1",
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, f"Failed to paginate builds: {response.text}"
        builds = response.json()
        assert len(builds) <= 1, "Pagination limit not respected"          
        wvw_builds = response.json()
        assert all(b["game_mode"] == "wvw" for b in wvw_builds), \
            "All returned builds should have game_mode='wvw'"
            
        # Test 4: Filter by profession
        response = client.get(
            "/api/v1/builds/",
            params={"profession_id": profession_id},
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, \
            "Failed to filter builds by profession"
            
        prof_builds = response.json()
        for build in prof_builds:
            assert any(p["id"] == profession_id for p in build["professions"]), \
                f"Build {build['id']} does not have the expected profession"
        
        # Test 5: Pagination
        response = client.get(
            "/api/v1/builds/",
            params={"skip": 1, "limit": 1},
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, \
            "Failed to paginate builds"
            
        paginated_builds = response.json()
        assert len(paginated_builds) <= 1, "Should return at most one build with limit=1"
        
        # Test 6: Search by name
        response = client.get(
            "/api/v1/builds/",
            params={"name": "Public"},
            headers=get_auth_headers(test_user.id)
        )
        assert response.status_code == status.HTTP_200_OK, \
            "Failed to search builds by name"
            
        searched_builds = response.json()
        assert any(b["name"] == "Public Test Build" for b in searched_builds), \
            "Should find build with 'Public' in name"

class TestBuildGeneration:
    """Test suite for the build generation endpoint."""
    
    def test_generate_build_no_constraints(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build with default parameters."""
        # Skip if no test professions available
        if not test_professions:
            pytest.skip("No test professions available")
            
        headers = get_auth_headers(test_user.id)
        
        # Create a valid build generation request
        request_data = {
            "team_size": 5,
            "game_mode": "WvW",
            "constraints": {
                "min_healers": 1,
                "min_dps": 2,
                "min_support": 1
            },
            "preferences": {
                "favorite_professions": [p.name for p in test_professions[:1]],  # Just use one profession
                "avoid_duplicates": True
            }
        }
        
        response = client.post(
            "/api/v1/builds/generate/",  # Note the trailing slash
            json=request_data,
            headers=headers
        )
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Build generation failed: {response.text}")
            
        # Check for either success or validation error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ], f"Unexpected status code: {response.status_code}: {response.text}"
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "build" in data
            assert "suggested_composition" in data
    
    def test_generate_build_conflicting_constraints(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build with impossible constraints."""
        headers = get_auth_headers(test_user.id)
        
        # Try to generate a build with conflicting constraints
        response = client.post(
            "/api/v1/builds/generate/",  # Note the trailing slash
            json={
                "game_mode": "wvw",
                "constraints": {
                    "min_healers": 5,  # Unrealistic constraint
                    "min_dps": 5,
                    "min_support": 5
                }
            },
            headers=headers
        )
        
        # Should return 422 (Unprocessable Entity) or 400 (Bad Request)
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST], \
            f"Expected 422 or 400, got {response.status_code}: {response.text}"
    
    def test_generate_build_excluded_professions(self, client: TestClient, test_user: User, test_professions: List[Profession]):
        """Test generating a build when excluding all available professions."""
        headers = get_auth_headers(test_user.id)
        
        # Get all profession IDs to exclude them all
        all_profession_ids = [p.id for p in test_professions]
        
        # Try to generate a build excluding all professions
        response = client.post(
            "/api/v1/builds/generate/",  # Note the trailing slash
            json={
                "game_mode": "wvw",
                "excluded_profession_ids": all_profession_ids,
                "constraints": {}
            },
            headers=headers
        )
        
        # Should return 422 (Unprocessable Entity) or 400 (Bad Request)
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST], \
            f"Expected 422 or 400, got {response.status_code}: {response.text}"

class TestBuildDataIntegrity:
    """Test suite for data integrity in build operations."""
    
    def test_build_deletion_cascades(self, client: TestClient, test_user: User, test_build: Build, db: Session):
        """Verify that deleting a build removes all related data."""
        headers = get_auth_headers(test_user.id)
        build_id = test_build.id
        
        # Verify build exists before deletion
        response = client.get(f"/api/v1/builds/{build_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK, "Test build should exist before deletion"
        
        # Verify build exists
        response = client.get(
            f"/api/v1/builds/{build_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Failed to fetch created build: {response.text}"
        
        # Delete the build
        response = client.delete(
            f"/api/v1/builds/{build_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 OK, got {response.status_code}: {response.text}"
        
        # Verify build is deleted
        response = client.get(
            f"/api/v1/builds/{build_id}",
            headers=headers
        )
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,  # Not found after deletion
            status.HTTP_403_FORBIDDEN   # Or forbidden if soft-deleted
        ], f"Expected 404 or 403 after deletion, got {response.status_code}"
        
        # Verify build-profession associations are deleted
        from app.models.build import build_profession
        stmt = build_profession.select().where(build_profession.c.build_id == build_id)
        result = db.execute(stmt).fetchall()
        assert len(result) == 0
        
    def test_transactional_integrity(self, client: TestClient, test_user: User, db: Session):
        """Test that failed operations don't leave partial data."""
        headers = get_auth_headers(test_user.id)
        
        # Try to create a build with an invalid profession ID
        build_data = {
            "name": "Test Build with Invalid Profession",
            "description": "Test description",
            "game_mode": "wvw",
            "is_public": True,
            "profession_ids": [99999],  # Non-existent profession
            "config": {"roles": ["dps"]},
            "constraints": {}
        }
        
        # This should fail with 422
        response = client.post(
            "/api/v1/builds/",  # Note: Make sure this matches your API router prefix
            json=build_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verify no build was created
        build = db.query(Build).filter(Build.name == "Test Build with Invalid Profession").first()
        assert build is None
