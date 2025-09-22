"""Test configuration and fixtures for unit tests."""

import pytest
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.main import app
from app.api.deps import get_async_db, get_current_user_dep
from app.models import User, Base, Profession, EliteSpecialization, Role, Permission

# Test database configuration for async tests
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the get_current_user dependency for testing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def override_get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
):
    """Override for the get_current_user dependency for testing."""
    if not token.startswith("test_token:"):
        raise HTTPException(status_code=401, detail="Invalid token format")

    user_id = int(token.split(":")[1])
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Apply the override
app.dependency_overrides[get_current_user_dep] = override_get_current_user


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
        echo=True  # Enable SQL logging for debugging
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Create a new session for the test
    async with async_session() as session:
        try:
            # Create test data
            from app.core.security import get_password_hash
            
            # Create roles and permissions
            admin_role = Role(name="admin", description="Administrator role")
            user_role = Role(name="user", description="Regular user role")
            session.add_all([admin_role, user_role])
            await session.flush()
            
            # Create admin user
            admin_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                full_name="Admin User"
            )
            admin_user.roles.append(admin_role)
            session.add(admin_user)
            
            # Create regular user
            test_user = User(
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                is_active=True,
                is_superuser=False,
                full_name="Test User"
            )
            test_user.roles.append(user_role)
            session.add(test_user)
            
            # Create test profession
            profession = Profession(
                name="Test Profession",
                description="Test profession description",
                is_active=True
            )
            session.add(profession)
            
            await session.commit()
            
            yield session
            
            # Clean up
            await session.rollback()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    # Clean up engine
    await engine.dispose()
