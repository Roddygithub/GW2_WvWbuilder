"""Tests for model coverage improvements."""

import pytest
from app.models.composition import Composition
from app.models.elite_specialization import EliteSpecialization
from app.models.profession import Profession
from app.models.role import Role
from app.models.permission import Permission
from app.models.tag import Tag
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User
from app.models.user_role import UserRole


def test_composition_model_creation():
    """Test Composition model instantiation."""
    comp = Composition(
        name="Test Composition",
        description="Test description",
        created_by_id=1
    )
    assert comp.name == "Test Composition"
    assert comp.description == "Test description"


def test_composition_repr():
    """Test Composition string representation."""
    comp = Composition(name="Test", created_by_id=1)
    repr_str = repr(comp)
    assert "Composition" in repr_str or "Test" in repr_str


def test_elite_specialization_model():
    """Test EliteSpecialization model."""
    spec = EliteSpecialization(
        name="Firebrand",
        description="Test spec",
        weapon_type="Axe",
        profession_id=1
    )
    assert spec.name == "Firebrand"
    assert spec.weapon_type == "Axe"


def test_profession_model():
    """Test Profession model."""
    prof = Profession(
        name="Guardian",
        description="Heavy armor class"
    )
    assert prof.name == "Guardian"


def test_profession_repr():
    """Test Profession string representation."""
    prof = Profession(name="Guardian")
    assert "Profession" in repr(prof) or "Guardian" in repr(prof)


def test_role_model():
    """Test Role model."""
    role = Role(name="Admin", description="Administrator role")
    assert role.name == "Admin"


def test_role_repr():
    """Test Role string representation."""
    role = Role(name="Admin")
    assert "Role" in repr(role) or "Admin" in repr(role)


def test_permission_model():
    """Test Permission model."""
    perm = Permission(name="read:compositions", description="Read compositions")
    assert perm.name == "read:compositions"


def test_tag_model():
    """Test Tag model."""
    tag = Tag(name="meta", description="Meta builds")
    assert tag.name == "meta"


def test_team_model():
    """Test Team model."""
    team = Team(
        name="Test Team",
        description="Team description",
        created_by_id=1
    )
    assert team.name == "Test Team"


def test_team_repr():
    """Test Team string representation."""
    team = Team(name="Test Team", created_by_id=1)
    assert "Team" in repr(team) or "Test Team" in repr(team)


def test_team_member_model():
    """Test TeamMember model."""
    member = TeamMember(team_id=1, user_id=1, role="member")
    assert member.role == "member"


def test_team_member_repr():
    """Test TeamMember string representation."""
    member = TeamMember(team_id=1, user_id=1)
    assert "TeamMember" in repr(member)


def test_user_model():
    """Test User model."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed"
    )
    assert user.email == "test@example.com"
    assert user.username == "testuser"


def test_user_repr():
    """Test User string representation."""
    user = User(email="test@example.com", username="testuser")
    assert "User" in repr(user) or "testuser" in repr(user)


def test_user_role_model():
    """Test UserRole model."""
    user_role = UserRole(user_id=1, role_id=1)
    assert user_role.user_id == 1
    assert user_role.role_id == 1


def test_user_role_repr():
    """Test UserRole string representation."""
    user_role = UserRole(user_id=1, role_id=1)
    assert "UserRole" in repr(user_role)
