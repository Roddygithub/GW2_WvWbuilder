"""Test configuration and fixtures for unit tests."""
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db, get_current_user
from app.models.base_models import User
from app.db.base import Base

# Test database configuration for async tests
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the get_current_user dependency for testing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def override_get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Override for the get_current_user dependency for testing."""
    if not token.startswith("test_token:"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_id = int(token.split(":")[1])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Apply the override
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="module")
def client():
    """Create a test client with overridden dependencies."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def async_db():
    """Create a database session for async tests."""
    # Create an async engine
    engine = create_async_engine(
        TEST_ASYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
    
    # Clean up
    await engine.dispose()
