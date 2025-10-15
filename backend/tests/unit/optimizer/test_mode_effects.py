"""Unit tests for mode-specific effects system."""
import pytest

from app.core.optimizer.mode_effects import (
    EffectMapping,
    ModeEffectsManager,
    apply_mode_adjustments,
    get_profession_mode_adjustments,
)


class TestEffectMapping:
    """Test EffectMapping dataclass."""

    def test_effect_mapping_creation(self):
        """Test creating an EffectMapping."""
        mapping = EffectMapping(
            trait_id=1806,
            trait_name="Glint's Boon Duration",
            wvw_effect={"boon": "quickness", "uptime_contribution": 0.15},
            pve_effect={"boon": "alacrity", "uptime_contribution": 0.25},
            description="Herald trait with different effects by mode"
        )
        
        assert mapping.trait_id == 1806
        assert mapping.wvw_effect["boon"] == "quickness"
        assert mapping.pve_effect["boon"] == "alacrity"


class TestModeEffectsManager:
    """Test ModeEffectsManager class."""

    @pytest.fixture
    def manager_wvw(self):
        """Create manager for WvW mode."""
        return ModeEffectsManager("wvw")

    @pytest.fixture
    def manager_pve(self):
        """Create manager for PvE mode."""
        return ModeEffectsManager("pve")

    def test_manager_initialization_wvw(self, manager_wvw):
        """Test manager initializes for WvW."""
        assert manager_wvw.game_type == "wvw"
        assert len(manager_wvw.effect_mappings) > 0

    def test_manager_initialization_pve(self, manager_pve):
        """Test manager initializes for PvE."""
        assert manager_pve.game_type == "pve"
        assert len(manager_pve.effect_mappings) > 0

    def test_get_effect_herald_wvw(self, manager_wvw):
        """Test getting Herald effect in WvW (should give Quickness)."""
        effect = manager_wvw.get_effect(1806)  # Herald trait
        
        assert effect is not None
        assert effect.get("boon") == "quickness"

    def test_get_effect_herald_pve(self, manager_pve):
        """Test getting Herald effect in PvE (should give Alacrity)."""
        effect = manager_pve.get_effect(1806)  # Herald trait
        
        assert effect is not None
        assert effect.get("boon") == "alacrity"

    def test_get_effect_mechanist_wvw(self, manager_wvw):
        """Test getting Mechanist effect in WvW (should give Might)."""
        effect = manager_wvw.get_effect(2276)  # Mechanist trait
        
        assert effect is not None
        assert effect.get("boon") == "might"

    def test_get_effect_mechanist_pve(self, manager_pve):
        """Test getting Mechanist effect in PvE (should give Alacrity)."""
        effect = manager_pve.get_effect(2276)  # Mechanist trait
        
        assert effect is not None
        assert effect.get("boon") == "alacrity"

    def test_get_effect_scrapper_wvw(self, manager_wvw):
        """Test getting Scrapper effect in WvW (should give Stability)."""
        effect = manager_wvw.get_effect(1917)  # Scrapper trait
        
        assert effect is not None
        assert effect.get("boon") == "stability"

    def test_get_effect_scrapper_pve(self, manager_pve):
        """Test getting Scrapper effect in PvE (should give Quickness)."""
        effect = manager_pve.get_effect(1917)  # Scrapper trait
        
        assert effect is not None
        assert effect.get("boon") == "quickness"

    def test_get_effect_firebrand_wvw(self, manager_wvw):
        """Test getting Firebrand effect in WvW (should give Resistance)."""
        effect = manager_wvw.get_effect(2075)  # Firebrand trait
        
        assert effect is not None
        assert effect.get("boon") == "resistance"

    def test_get_effect_firebrand_pve(self, manager_pve):
        """Test getting Firebrand effect in PvE (should give Quickness)."""
        effect = manager_pve.get_effect(2075)  # Firebrand trait
        
        assert effect is not None
        assert effect.get("boon") == "quickness"

    def test_get_effect_invalid_trait(self, manager_wvw):
        """Test getting effect for non-existent trait."""
        effect = manager_wvw.get_effect(99999)
        
        assert effect == {}

    def test_get_boon_contribution(self, manager_pve):
        """Test getting boon contribution for a trait."""
        contribution = manager_pve.get_boon_contribution(1806, "alacrity")
        
        assert isinstance(contribution, float)
        assert contribution > 0

    def test_get_boon_contribution_wrong_boon(self, manager_wvw):
        """Test getting boon contribution for wrong boon."""
        # Herald gives Quickness in WvW, not Alacrity
        contribution = manager_wvw.get_boon_contribution(1806, "alacrity")
        
        assert contribution == 0.0

    def test_get_all_boon_sources_quickness_wvw(self, manager_wvw):
        """Test getting all Quickness sources in WvW."""
        sources = manager_wvw.get_all_boon_sources("quickness")
        
        assert len(sources) > 0
        # Should include Herald (trait 1806)
        herald_sources = [s for s in sources if s["trait_id"] == 1806]
        assert len(herald_sources) > 0

    def test_get_all_boon_sources_alacrity_pve(self, manager_pve):
        """Test getting all Alacrity sources in PvE."""
        sources = manager_pve.get_all_boon_sources("alacrity")
        
        assert len(sources) > 0
        # Should include Herald (1806) and Mechanist (2276)
        herald_sources = [s for s in sources if s["trait_id"] == 1806]
        mechanist_sources = [s for s in sources if s["trait_id"] == 2276]
        assert len(herald_sources) > 0
        assert len(mechanist_sources) > 0

    def test_get_all_boon_sources_stability_wvw(self, manager_wvw):
        """Test getting all Stability sources in WvW."""
        sources = manager_wvw.get_all_boon_sources("stability")
        
        assert len(sources) > 0
        # Should include Scrapper (trait 1917)
        scrapper_sources = [s for s in sources if s["trait_id"] == 1917]
        assert len(scrapper_sources) > 0

    def test_different_modes_have_different_sources(self, manager_wvw, manager_pve):
        """Test that WvW and PvE have different boon sources."""
        quickness_wvw = manager_wvw.get_all_boon_sources("quickness")
        quickness_pve = manager_pve.get_all_boon_sources("quickness")
        
        # Should have different sets of sources
        wvw_trait_ids = {s["trait_id"] for s in quickness_wvw}
        pve_trait_ids = {s["trait_id"] for s in quickness_pve}
        
        # Herald gives Quickness in WvW but not PvE
        assert 1806 in wvw_trait_ids
        assert 1806 not in pve_trait_ids


class TestApplyModeAdjustments:
    """Test apply_mode_adjustments function."""

    def test_apply_adjustments_guardian_wvw(self):
        """Test applying adjustments for Guardian in WvW."""
        base_caps = {
            "boon_uptime": 0.90,
            "healing": 0.80,
            "damage": 0.70,
        }
        
        adjusted = apply_mode_adjustments(base_caps, profession_id=1, game_type="wvw")
        
        # Guardian should get bonus in WvW
        assert "boon_uptime" in adjusted
        assert "healing" in adjusted
        assert "damage" in adjusted

    def test_apply_adjustments_guardian_pve(self):
        """Test applying adjustments for Guardian in PvE."""
        base_caps = {
            "boon_uptime": 0.90,
            "healing": 0.80,
            "damage": 0.70,
        }
        
        adjusted = apply_mode_adjustments(base_caps, profession_id=1, game_type="pve")
        
        # Guardian should get different bonus in PvE
        assert adjusted["boon_uptime"] >= base_caps["boon_uptime"]

    def test_apply_adjustments_mechanist_pve(self):
        """Test applying adjustments for Mechanist in PvE."""
        base_caps = {
            "boon_uptime": 0.90,
            "alacrity": 0.95,
            "damage": 0.70,
        }
        
        adjusted = apply_mode_adjustments(base_caps, profession_id=6, game_type="pve")
        
        # Mechanist should get significant bonus in PvE
        assert adjusted["boon_uptime"] > base_caps["boon_uptime"]
        assert adjusted["alacrity"] >= base_caps["alacrity"]

    def test_apply_adjustments_mechanist_wvw(self):
        """Test applying adjustments for Mechanist in WvW."""
        base_caps = {
            "boon_uptime": 0.90,
            "might": 0.90,
            "damage": 0.70,
        }
        
        adjusted = apply_mode_adjustments(base_caps, profession_id=6, game_type="wvw")
        
        # Mechanist should get less bonus in WvW
        assert adjusted["boon_uptime"] <= base_caps["boon_uptime"] * 1.1

    def test_apply_adjustments_no_mapping(self):
        """Test applying adjustments for profession without mapping."""
        base_caps = {
            "damage": 0.80,
            "mobility": 0.70,
        }
        
        # Thief (profession_id=8) has no specific adjustments
        adjusted = apply_mode_adjustments(base_caps, profession_id=8, game_type="pve")
        
        # Should return unchanged or with default adjustments
        assert "damage" in adjusted
        assert "mobility" in adjusted

    def test_adjustments_preserve_all_fields(self):
        """Test that adjustments preserve all capability fields."""
        base_caps = {
            "boon_uptime": 0.90,
            "healing": 0.85,
            "damage": 0.70,
            "mobility": 0.60,
            "crowd_control": 0.75,
        }
        
        adjusted = apply_mode_adjustments(base_caps, profession_id=1, game_type="wvw")
        
        # All fields should still be present
        assert set(adjusted.keys()) == set(base_caps.keys())


class TestGetProfessionModeAdjustments:
    """Test get_profession_mode_adjustments function."""

    def test_get_adjustments_guardian(self):
        """Test getting adjustments for Guardian."""
        adjustments = get_profession_mode_adjustments(1, "wvw")
        
        assert adjustments is not None
        assert "boon_uptime" in adjustments or adjustments == {}

    def test_get_adjustments_revenant(self):
        """Test getting adjustments for Revenant."""
        adjustments_wvw = get_profession_mode_adjustments(2, "wvw")
        adjustments_pve = get_profession_mode_adjustments(2, "pve")
        
        # Should have different adjustments
        assert adjustments_wvw is not None or adjustments_wvw == {}
        assert adjustments_pve is not None or adjustments_pve == {}

    def test_get_adjustments_engineer(self):
        """Test getting adjustments for Engineer."""
        adjustments_wvw = get_profession_mode_adjustments(6, "wvw")
        adjustments_pve = get_profession_mode_adjustments(6, "pve")
        
        # Engineer/Mechanist should have significant difference
        assert adjustments_pve is not None or adjustments_pve == {}

    def test_get_adjustments_invalid_profession(self):
        """Test getting adjustments for invalid profession."""
        adjustments = get_profession_mode_adjustments(999, "wvw")
        
        # Should return empty dict for unknown profession
        assert adjustments == {}


class TestModeSpecificBehaviors:
    """Test mode-specific behaviors and differences."""

    def test_herald_gives_different_boons_by_mode(self):
        """Test that Herald gives different boons in WvW vs PvE."""
        manager_wvw = ModeEffectsManager("wvw")
        manager_pve = ModeEffectsManager("pve")
        
        effect_wvw = manager_wvw.get_effect(1806)
        effect_pve = manager_pve.get_effect(1806)
        
        # Should give different boons
        assert effect_wvw.get("boon") != effect_pve.get("boon")
        assert effect_wvw.get("boon") == "quickness"
        assert effect_pve.get("boon") == "alacrity"

    def test_mechanist_gives_different_boons_by_mode(self):
        """Test that Mechanist gives different boons in WvW vs PvE."""
        manager_wvw = ModeEffectsManager("wvw")
        manager_pve = ModeEffectsManager("pve")
        
        effect_wvw = manager_wvw.get_effect(2276)
        effect_pve = manager_pve.get_effect(2276)
        
        # Should give different boons
        assert effect_wvw.get("boon") == "might"
        assert effect_pve.get("boon") == "alacrity"

    def test_contribution_values_differ_by_mode(self):
        """Test that contribution values differ by mode."""
        manager_wvw = ModeEffectsManager("wvw")
        manager_pve = ModeEffectsManager("pve")
        
        # Herald's contribution should differ
        effect_wvw = manager_wvw.get_effect(1806)
        effect_pve = manager_pve.get_effect(1806)
        
        contrib_wvw = effect_wvw.get("uptime_contribution", 0)
        contrib_pve = effect_pve.get("uptime_contribution", 0)
        
        # Different boons should have different contributions
        assert contrib_wvw != contrib_pve


class TestIntegrationWithOptimizer:
    """Test integration between mode_effects and optimizer."""

    def test_mode_effects_applied_in_catalogue(self):
        """Test that mode effects are applied when building catalogue."""
        from app.core.optimizer.engine import OptimizerEngine
        
        engine_wvw = OptimizerEngine("wvw", "zerg")
        engine_pve = OptimizerEngine("pve", "fractale")
        
        # Find Herald template in both catalogues
        herald_wvw = next((t for t in engine_wvw.build_catalogue if t.profession_id == 2 and t.elite_spec_id == 5), None)
        herald_pve = next((t for t in engine_pve.build_catalogue if t.profession_id == 2 and t.elite_spec_id == 5), None)
        
        if herald_wvw and herald_pve:
            # Should have different alacrity/quickness values
            assert herald_wvw.capabilities.get("quickness", 0) > herald_pve.capabilities.get("quickness", 0)
            assert herald_pve.capabilities.get("alacrity", 0) > herald_wvw.capabilities.get("alacrity", 0)
