"""
Tests unitaires pour app/schemas/build.py - Validations
"""
import pytest
from pydantic import ValidationError

from app.schemas.build import GameMode, RoleType, BuildBase


class TestGameModeEnum:
    """Tests pour GameMode enum."""

    def test_game_mode_values(self):
        """Test valeurs GameMode."""
        assert GameMode.WVW.value == "wvw"
        assert GameMode.PVP.value == "pvp"
        assert GameMode.PVE.value == "pve"
        assert GameMode.RAIDS.value == "raids"
        assert GameMode.FRACTALS.value == "fractals"


class TestRoleTypeEnum:
    """Tests pour RoleType enum."""

    def test_role_type_values(self):
        """Test valeurs RoleType."""
        assert RoleType.HEALER.value == "healer"
        assert RoleType.DPS.value == "dps"
        assert RoleType.SUPPORT.value == "support"
        assert RoleType.QUICKNESS.value == "quickness"
        assert RoleType.ALACRITY.value == "alacrity"


class TestBuildBaseValidation:
    """Tests pour validations BuildBase schema."""

    def test_build_base_valid_minimal(self):
        """Test création BuildBase avec données minimales valides."""
        build = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW
        )
        assert build.name == "Test Build"
        assert build.game_mode == GameMode.WVW
        assert build.team_size == 5  # default
        assert build.is_public is True  # default

    def test_build_base_valid_full(self):
        """Test création BuildBase avec toutes les données."""
        build = BuildBase(
            name="WvW Zerg Firebrand",
            description="Support build for WvW zergs",
            game_mode=GameMode.WVW,
            team_size=50,
            is_public=False,
            config={"weapons": ["Axe", "Shield"]},
            constraints={}
        )
        assert build.name == "WvW Zerg Firebrand"
        assert build.description == "Support build for WvW zergs"
        assert build.team_size == 50
        assert build.is_public is False

    def test_build_base_name_too_short(self):
        """Test validation nom trop court (< 3 caractères)."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="AB",  # Trop court
                game_mode=GameMode.WVW
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_build_base_name_too_long(self):
        """Test validation nom trop long (> 100 caractères)."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="A" * 101,  # Trop long
                game_mode=GameMode.WVW
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_build_base_description_too_long(self):
        """Test validation description trop longue (> 1000 caractères)."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="Test Build",
                description="A" * 1001,  # Trop long
                game_mode=GameMode.WVW
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_build_base_team_size_too_small(self):
        """Test validation team_size trop petit (< 1)."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="Test Build",
                game_mode=GameMode.WVW,
                team_size=0  # Invalide
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("team_size",) for e in errors)

    def test_build_base_team_size_too_large(self):
        """Test validation team_size trop grand (> 50)."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="Test Build",
                game_mode=GameMode.WVW,
                team_size=51  # Invalide
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("team_size",) for e in errors)

    def test_build_base_team_size_boundary_values(self):
        """Test valeurs limites pour team_size."""
        # Minimum valide
        build_min = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW,
            team_size=1
        )
        assert build_min.team_size == 1

        # Maximum valide
        build_max = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW,
            team_size=50
        )
        assert build_max.team_size == 50

    def test_build_base_invalid_game_mode(self):
        """Test validation game_mode invalide."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="Test Build",
                game_mode="invalid_mode"  # type: ignore
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("game_mode",) for e in errors)

    def test_build_base_missing_required_fields(self):
        """Test validation champs requis manquants."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase()  # type: ignore
        errors = exc_info.value.errors()
        # name et game_mode sont requis
        assert len(errors) >= 2

    def test_build_base_extra_fields_forbidden(self):
        """Test que les champs supplémentaires sont interdits."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(
                name="Test Build",
                game_mode=GameMode.WVW,
                extra_field="not allowed"  # type: ignore
            )
        errors = exc_info.value.errors()
        assert any("extra_field" in str(e) for e in errors)

    def test_build_base_config_optional(self):
        """Test que config est optionnel."""
        build = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW
        )
        assert build.config is None

    def test_build_base_config_dict(self):
        """Test que config accepte un dictionnaire."""
        config_data = {
            "weapons": ["Axe", "Shield"],
            "traits": ["Radiance", "Honor"],
            "skills": ["Mantra of Potence"]
        }
        build = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW,
            config=config_data
        )
        assert build.config == config_data

    def test_build_base_is_public_default(self):
        """Test valeur par défaut de is_public."""
        build = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW
        )
        assert build.is_public is True

    def test_build_base_is_public_false(self):
        """Test is_public=False."""
        build = BuildBase(
            name="Test Build",
            game_mode=GameMode.WVW,
            is_public=False
        )
        assert build.is_public is False
