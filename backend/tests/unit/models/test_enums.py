"""
Tests unitaires pour app/models/enums.py
"""

import pytest
from enum import Enum, IntEnum

from app.models.enums import (
    GameMode,
    RoleType,
    BuildStatus,
    CompositionStatus,
    ProfessionType,
    EliteSpecializationType,
    BuildType,
    CompositionRole,
    Visibility,
    PermissionLevel,
    TeamRole,
    TeamStatus,
)


class TestGameMode:
    """Tests pour GameMode enum."""

    def test_game_mode_values(self):
        """Test valeurs GameMode."""
        assert GameMode.WvW.value == "wvw"
        assert GameMode.PvP.value == "pvp"
        assert GameMode.PvE.value == "pve"

    def test_game_mode_count(self):
        """Test nombre de modes de jeu."""
        assert len(GameMode) == 3


class TestRoleType:
    """Tests pour RoleType enum."""

    def test_role_type_values(self):
        """Test valeurs RoleType."""
        assert RoleType.ADMIN.value == "admin"
        assert RoleType.USER.value == "user"
        assert RoleType.MODERATOR.value == "moderator"
        assert RoleType.GUEST.value == "guest"

    def test_role_type_count(self):
        """Test nombre de types de rôle."""
        assert len(RoleType) == 4


class TestBuildStatus:
    """Tests pour BuildStatus enum."""

    def test_build_status_values(self):
        """Test valeurs BuildStatus."""
        assert BuildStatus.DRAFT.value == "draft"
        assert BuildStatus.PUBLISHED.value == "published"
        assert BuildStatus.ARCHIVED.value == "archived"

    def test_build_status_count(self):
        """Test nombre de statuts de build."""
        assert len(BuildStatus) == 3


class TestCompositionStatus:
    """Tests pour CompositionStatus enum."""

    def test_composition_status_values(self):
        """Test valeurs CompositionStatus."""
        assert CompositionStatus.DRAFT.value == "draft"
        assert CompositionStatus.ACTIVE.value == "active"
        assert CompositionStatus.INACTIVE.value == "inactive"
        assert CompositionStatus.ARCHIVED.value == "archived"

    def test_composition_status_count(self):
        """Test nombre de statuts de composition."""
        assert len(CompositionStatus) == 4


class TestProfessionType:
    """Tests pour ProfessionType enum."""

    def test_profession_type_values(self):
        """Test valeurs ProfessionType."""
        assert ProfessionType.GUARDIAN.value == "Guardian"
        assert ProfessionType.WARRIOR.value == "Warrior"
        assert ProfessionType.ELEMENTALIST.value == "Elementalist"

    def test_profession_type_count(self):
        """Test nombre de professions GW2."""
        assert len(ProfessionType) == 9


class TestEliteSpecializationType:
    """Tests pour EliteSpecializationType enum."""

    def test_elite_spec_guardian(self):
        """Test spécialisations élites Guardian."""
        assert EliteSpecializationType.DRAGONHUNTER.value == "Dragonhunter"
        assert EliteSpecializationType.FIREBRAND.value == "Firebrand"
        assert EliteSpecializationType.WILLBENDER.value == "Willbender"

    def test_elite_spec_warrior(self):
        """Test spécialisations élites Warrior."""
        assert EliteSpecializationType.BERSERKER.value == "Berserker"
        assert EliteSpecializationType.SPELLBREAKER.value == "Spellbreaker"
        assert EliteSpecializationType.BLADESWORN.value == "Bladesworn"

    def test_elite_spec_count(self):
        """Test nombre total de spécialisations élites (3 par profession)."""
        assert len(EliteSpecializationType) == 27  # 9 professions * 3 specs


class TestBuildType:
    """Tests pour BuildType enum."""

    def test_build_type_values(self):
        """Test valeurs BuildType."""
        assert BuildType.POWER.value == "power"
        assert BuildType.CONDITION.value == "condition"
        assert BuildType.SUPPORT.value == "support"
        assert BuildType.ZERG.value == "zerg"

    def test_build_type_count(self):
        """Test nombre de types de build."""
        assert len(BuildType) == 8


class TestCompositionRole:
    """Tests pour CompositionRole enum."""

    def test_composition_role_values(self):
        """Test valeurs CompositionRole."""
        assert CompositionRole.COMMANDER.value == "commander"
        assert CompositionRole.SUPPORT.value == "support"
        assert CompositionRole.DPS.value == "dps"
        assert CompositionRole.HEALER.value == "healer"

    def test_composition_role_count(self):
        """Test nombre de rôles de composition."""
        assert len(CompositionRole) == 7


class TestVisibility:
    """Tests pour Visibility enum."""

    def test_visibility_values(self):
        """Test valeurs Visibility."""
        assert Visibility.PUBLIC.value == "public"
        assert Visibility.PRIVATE.value == "private"
        assert Visibility.UNLISTED.value == "unlisted"

    def test_visibility_count(self):
        """Test nombre de niveaux de visibilité."""
        assert len(Visibility) == 3


class TestPermissionLevel:
    """Tests pour PermissionLevel enum."""

    def test_permission_level_values(self):
        """Test valeurs PermissionLevel."""
        assert PermissionLevel.READ == 1
        assert PermissionLevel.COMMENT == 2
        assert PermissionLevel.EDIT == 3
        assert PermissionLevel.MANAGE == 4
        assert PermissionLevel.ADMIN == 5

    def test_permission_level_ordering(self):
        """Test ordre des niveaux de permission."""
        assert PermissionLevel.READ < PermissionLevel.COMMENT
        assert PermissionLevel.COMMENT < PermissionLevel.EDIT
        assert PermissionLevel.EDIT < PermissionLevel.MANAGE
        assert PermissionLevel.MANAGE < PermissionLevel.ADMIN

    def test_permission_level_count(self):
        """Test nombre de niveaux de permission."""
        assert len(PermissionLevel) == 5


class TestTeamRole:
    """Tests pour TeamRole enum."""

    def test_team_role_values(self):
        """Test valeurs TeamRole."""
        assert TeamRole.OWNER.value == "owner"
        assert TeamRole.ADMIN.value == "admin"
        assert TeamRole.OFFICER.value == "officer"
        assert TeamRole.MEMBER.value == "member"
        assert TeamRole.TRIAL.value == "trial"

    def test_team_role_count(self):
        """Test nombre de rôles d'équipe."""
        assert len(TeamRole) == 5


class TestTeamStatus:
    """Tests pour TeamStatus enum."""

    def test_team_status_values(self):
        """Test valeurs TeamStatus."""
        assert TeamStatus.ACTIVE.value == "active"
        assert TeamStatus.INACTIVE.value == "inactive"
        assert TeamStatus.ARCHIVED.value == "archived"

    def test_team_status_count(self):
        """Test nombre de statuts d'équipe."""
        assert len(TeamStatus) == 3
