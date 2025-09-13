"""Tests for base_models."""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Import the models to test
from app.models.base_models import User, Role, Profession, EliteSpecialization, Composition, CompositionTag, Build

# Test cases
@pytest.mark.asyncio
async def test_user_model():
    """Test User model initialization."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_superuser is False

@pytest.mark.asyncio
async def test_role_model():
    """Test Role model initialization."""
    role = Role(
        name="test_role",
        description="Test Role",
        permission_level=1,
        is_default=False
    )
    assert role.name == "test_role"
    assert role.permission_level == 1
    assert role.is_default is False

@pytest.mark.asyncio
async def test_profession_model():
    """Test Profession model initialization."""
    profession = Profession(
        name="Test Profession",
        icon_url="http://example.com/icon.png",
        description="Test Description"
    )
    assert profession.name == "Test Profession"
    assert profession.icon_url == "http://example.com/icon.png"

@pytest.mark.asyncio
async def test_elite_specialization_model():
    """Test EliteSpecialization model initialization."""
    elite_spec = EliteSpecialization(
        name="Test Elite Spec",
        profession_id=1,
        icon_url="http://example.com/spec.png"
    )
    assert elite_spec.name == "Test Elite Spec"
    assert elite_spec.profession_id == 1

@pytest.mark.asyncio
async def test_composition_model():
    """Test Composition model initialization."""
    composition = Composition(
        name="Test Composition",
        description="Test Description",
        squad_size=10,
        is_public=True,
        created_by=1
    )
    assert composition.name == "Test Composition"
    assert composition.squad_size == 10
    assert composition.is_public is True

@pytest.mark.asyncio
async def test_build_model():
    """Test Build model initialization."""
    build = Build(
        name="Test Build",
        description="Test Description",
        game_mode="wvw",
        team_size=5,
        is_public=False,
        created_by_id=1,
        config={"trait1": 1, "trait2": 2},
        constraints={"max_players": 10}
    )
    assert build.name == "Test Build"
    assert build.game_mode == "wvw"
    assert build.team_size == 5
    assert build.is_public is False

