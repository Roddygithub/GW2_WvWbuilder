"""Basic integration tests for the Builds API endpoints."""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator, Dict, Any

from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.models import User, Build, Profession, Role, user_roles
from app.core.security import create_access_token, get_password_hash
from app.crud import CRUDUser, user as user_crud

# Test database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# Test user data
@pytest.fixture(scope="module")
def test_user() -> Dict[str, Any]:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_superuser": False,
        "full_name": "Test User"
    }

# Test build data
@pytest.fixture(scope="module")
def test_build_data() -> Dict[str, Any]:
    return {
        "name": "Test Build",
        "description": "A test build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2, 3]
    }

# Test professions
@pytest.fixture(scope="module")
def test_professions() -> list[Dict[str, Any]]:
    return [
        {"id": 1, "name": "Guardian", "description": "A guardian profession"},
        {"id": 2, "name": "Warrior", "description": "A warrior profession"},
        {"id": 3, "name": "Engineer", "description": "An engineer profession"}
    ]

# Test token
@pytest.fixture(scope="module")
def test_token(test_user: Dict[str, Any]) -> str:
    return create_access_token(subject=test_user["username"])

# Test client with auth header
@pytest.fixture(scope="module")
def auth_headers(test_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {test_token}"}

# Initialize test database
@pytest.fixture(scope="module", autouse=True)
def init_test_db(test_user: Dict[str, Any], test_professions: list[Dict[str, Any]]) -> None:
    db = next(override_get_db())
    try:
        # Add test professions
        for prof in test_professions:
            db_prof = Profession(**prof)
            db.add(db_prof)
        
        # Add test user
        db_user = User(**test_user)
        db.add(db_user)
        
        db.commit()
        yield  # Test runs here
        
    finally:
        # Clean up
        db.rollback()
        db.close()

def test_create_build(client: TestClient, test_build_data: Dict[str, Any], auth_headers: Dict[str, str]) -> None:
    # Test create build endpoint
    response = client.post(
        "/api/v1/builds/",
        json=test_build_data,
        headers=auth_headers
    )
    
    # Check response status code and data
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    
    # Verify the build data
    assert data["name"] == test_build_data["name"]
    assert data["description"] == test_build_data["description"]
    assert data["game_mode"] == test_build_data["game_mode"]
    assert data["team_size"] == test_build_data["team_size"]
    assert data["is_public"] == test_build_data["is_public"]
    assert len(data["professions"]) == len(test_build_data["profession_ids"])
    
    # Verify the build was saved to the database
    db = next(override_get_db())
    try:
        build = db.query(Build).filter(Build.name == test_build_data["name"]).first()
        assert build is not None
        assert build.description == test_build_data["description"]
    finally:
        db.close()
