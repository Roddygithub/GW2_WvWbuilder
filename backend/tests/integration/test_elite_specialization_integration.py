"""Integration tests for EliteSpecialization and related models."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.profession import Profession
from app.models.elite_specialization import EliteSpecialization
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.elite_specialization import GameMode
from app.core.security import get_password_hash

# Fixtures


@pytest_asyncio.fixture
async def test_profession(async_session: AsyncSession):
    """Create a test profession."""
    profession = Profession(
        name="Necromancer",
        description="Master of the dark arts",
        icon_url="https://example.com/necromancer.png",
        is_active=True,
    )
    async_session.add(profession)
    await async_session.commit()
    await async_session.refresh(profession)
    return profession


@pytest_asyncio.fixture
async def test_elite_specs(async_session: AsyncSession, test_profession):
    """Create test elite specializations."""
    specs = [
        EliteSpecialization(
            name="Reaper",
            profession_id=test_profession.id,
            description="Greatsword-wielding melee specialist",
            weapon_type="Greatsword",
            background_url="https://example.com/reaper_bg.jpg",
            is_active=True,
            game_mode_affinity=[GameMode.WVW, GameMode.PVE],
            profession=test_profession,
        ),
        EliteSpecialization(
            name="Scourge",
            profession_id=test_profession.id,
            description="Support and condition damage specialist",
            weapon_type="Torch",
            background_url="https://example.com/scourge_bg.jpg",
            is_active=True,
            game_mode_affinity=[GameMode.WVW, GameMode.PVP],
            profession=test_profession,
        ),
    ]

    async_session.add_all(specs)
    await async_session.commit()
    for spec in specs:
        await async_session.refresh(spec)
    return specs


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession):
    """Create a test user."""
    # Create roles if they don't exist
    admin_role = Role(name="admin", description="Administrator")
    user_role = Role(name="user", description="Regular user")
    async_session.add_all([admin_role, user_role])
    await async_session.commit()

    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # Assign admin role using the UserRole model
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    async_session.add(user_role)
    await async_session.commit()

    return user


# Test cases


@pytest.mark.asyncio
async def test_get_elite_specs_by_profession(
    async_client: AsyncClient,
    test_profession: Profession,
    test_elite_specs: list[EliteSpecialization],
):
    """Test getting elite specs filtered by profession."""
    response = await async_client.get(
        f"/api/v1/elite-specializations/by-profession/{test_profession.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(spec["profession_id"] == test_profession.id for spec in data)


@pytest.mark.asyncio
async def test_get_elite_specs_by_game_mode(
    async_client: AsyncClient, test_elite_specs: list[EliteSpecialization]
):
    """Test getting elite specs filtered by game mode."""
    # Test WVW mode (both specs should be returned)
    response = await async_client.get("/api/v1/elite-specializations/by-game-mode/WVW")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

    # Test PVE mode (only Reaper should be returned)
    response = await async_client.get("/api/v1/elite-specializations/by-game-mode/PVE")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Reaper"


@pytest.mark.asyncio
async def test_elite_spec_creation_with_build(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_elite_specs: list[EliteSpecialization],
    test_user: User,
):
    """Test creating a build with an elite specialization."""
    # Get auth token
    login_data = {"username": "testuser", "password": "testpassword"}
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a build with the first elite spec
    build_data = {
        "name": "Test Build",
        "description": "Test build with elite spec",
        "elite_specialization_id": test_elite_specs[0].id,
        "is_public": True,
        "game_mode": "WVW",
    }

    response = await async_client.post(
        "/api/v1/builds/", json=build_data, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Verify the build was created with the correct elite spec
    build_data = response.json()
    assert build_data["elite_specialization_id"] == test_elite_specs[0].id

    # Verify the profession is correctly associated
    response = await async_client.get(
        f"/api/v1/builds/{build_data['id']}", headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    build_data = response.json()
    assert "elite_specialization" in build_data
    assert build_data["elite_specialization"]["id"] == test_elite_specs[0].id
    assert "profession" in build_data["elite_specialization"]
    assert (
        build_data["elite_specialization"]["profession"]["id"]
        == test_elite_specs[0].profession_id
    )
