"""End-to-end tests for user CRUD operations."""

import os
import pytest
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import verify_password
from app.crud.user import user as crud_user
from app.models import Base, Role
from app.schemas.user import UserCreate

# Test data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"
TEST_USERNAME = "testuser"
TEST_FULL_NAME = "Test User"

# Test database setup
TEST_DB_URL = "sqlite+aiosqlite:///./test_e2e.db"

# Create test engine and session factory
test_engine = create_async_engine(
    TEST_DB_URL, echo=True, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Set up the test database with all tables."""
    # Remove existing test database if it exists
    if os.path.exists("test_e2e.db"):
        os.remove("test_e2e.db")

    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a default role
    async with TestingSessionLocal() as session:
        try:
            # Check if role exists
            result = await session.execute(select(Role).where(Role.name == "user"))
            role = result.scalars().first()

            if not role:
                # Create default role
                role = Role(
                    name="user",
                    description="Regular user",
                    is_default=True,
                    permission_level=1,
                )
                session.add(role)
                await session.commit()
                await session.refresh(role)
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    yield

    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

    if os.path.exists("test_e2e.db"):
        os.remove("test_e2e.db")


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            # Start a transaction
            await session.begin()
            yield session
            # Always rollback after test
            await session.rollback()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


@pytest.mark.asyncio
async def test_create_user():
    """Test creating a new user."""
    # Create a new session for this test
    async with TestingSessionLocal() as session:
        try:
            # Start a transaction
            await session.begin()

            # Test data
            user_in = UserCreate(
                email=TEST_EMAIL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                full_name=TEST_FULL_NAME,
            )

            # Create user
            user = await crud_user.create_async(session, obj_in=user_in)

            # Add role to user
            result = await session.execute(select(Role).where(Role.name == "user"))
            role = result.scalars().first()
            user.roles.append(role)
            await session.commit()
            await session.refresh(user)

            # Verify user was created
            assert user is not None
            assert user.email == TEST_EMAIL
            assert user.username == TEST_USERNAME
            assert user.full_name == TEST_FULL_NAME
            assert user.is_active is True
            assert user.is_superuser is False
            assert hasattr(user, "hashed_password")
            assert verify_password(TEST_PASSWORD, user.hashed_password)
            assert len(user.roles) == 1
            assert user.roles[0].name == "user"

            # Clean up
            await session.delete(user)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


@pytest.mark.asyncio
async def test_authenticate_user():
    """Test user authentication."""
    # Create a new session for this test
    async with TestingSessionLocal() as session:
        try:
            # Start a transaction
            await session.begin()

            # Create test user
            user_in = UserCreate(
                email=TEST_EMAIL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                full_name=TEST_FULL_NAME,
            )
            user = await crud_user.create_async(session, obj_in=user_in)

            # Add role to user
            result = await session.execute(select(Role).where(Role.name == "user"))
            role = result.scalars().first()
            user.roles.append(role)
            await session.commit()

            # Test authentication
            authenticated_user = await crud_user.authenticate_async(
                session, email=TEST_EMAIL, password=TEST_PASSWORD
            )

            # Verify authentication
            assert authenticated_user is not None
            assert authenticated_user.email == TEST_EMAIL

            # Clean up
            await session.delete(user)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
