"""Unit tests for optimizer engine."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.core.optimizer.engine import (
    OptimizerEngine,
    OptimizerConfig,
    BuildTemplate,
    optimize_composition,
)
from app.schemas.composition import (
    CompositionOptimizationRequest,
    CompositionOptimizationResult,
    CompositionMemberRole,
)


class TestOptimizerConfig:
    """Test OptimizerConfig class."""

    def test_load_wvw_zerg_config(self):
        """Test loading WvW zerg configuration."""
        config = OptimizerConfig("zerg")
        
        assert config.mode == "zerg"
        assert "quickness" in config.critical_boons
        assert "alacrity" in config.critical_boons
        assert config.weights["boon_uptime"] > 0
        assert len(config.weights) > 0

    def test_load_pve_fractale_config(self):
        """Test loading PvE fractale configuration."""
        config = OptimizerConfig("fractale")
        
        assert config.mode == "fractale"
        assert "quickness" in config.critical_boons
        assert "alacrity" in config.critical_boons
        assert config.weights["damage"] >= 0

    def test_invalid_config_uses_defaults(self):
        """Test that invalid config name uses defaults."""
        config = OptimizerConfig("invalid_mode")
        # Should use default config
        assert config.mode == "invalid_mode"
        assert len(config.weights) > 0


class TestBuildTemplate:
    """Test BuildTemplate class."""

    def test_build_template_creation(self):
        """Test creating a build template."""
        template = BuildTemplate(
            profession_id=1,
            elite_spec_id=3,
            role_type=CompositionMemberRole.HEALER,
            capabilities={
                "healing": 0.95,
                "boon_uptime": 0.90,
                "quickness": 0.95,
            }
        )
        
        assert template.profession_id == 1
        assert template.elite_spec_id == 3
        assert template.role_type == CompositionMemberRole.HEALER
        assert template.capabilities["healing"] == 0.95
        assert template.capabilities["quickness"] == 0.95


class TestOptimizerEngine:
    """Test OptimizerEngine class."""

    @pytest.fixture
    def engine_wvw(self):
        """Create optimizer engine for WvW zerg."""
        return OptimizerEngine(game_type="wvw", game_mode="zerg")

    @pytest.fixture
    def engine_pve(self):
        """Create optimizer engine for PvE fractale."""
        return OptimizerEngine(game_type="pve", game_mode="fractale")

    @pytest.fixture
    def request_wvw(self):
        """Create optimization request for WvW."""
        return CompositionOptimizationRequest(
            squad_size=15,
            game_type="wvw",
            game_mode="zerg",
        )

    @pytest.fixture
    def request_pve(self):
        """Create optimization request for PvE."""
        return CompositionOptimizationRequest(
            squad_size=5,
            game_type="pve",
            game_mode="fractale",
        )

    def test_engine_initialization_wvw(self, engine_wvw):
        """Test engine initializes correctly for WvW."""
        assert engine_wvw.game_type == "wvw"
        assert engine_wvw.game_mode == "zerg"
        assert engine_wvw.config is not None
        assert engine_wvw.mode_effects is not None
        assert len(engine_wvw.build_catalogue) > 0

    def test_engine_initialization_pve(self, engine_pve):
        """Test engine initializes correctly for PvE."""
        assert engine_pve.game_type == "pve"
        assert engine_pve.game_mode == "fractale"
        assert engine_pve.config is not None
        assert len(engine_pve.build_catalogue) > 0

    def test_greedy_seed_generates_valid_solution(self, engine_wvw, request_wvw):
        """Test that greedy seed generates a valid solution."""
        solution = engine_wvw.greedy_seed(request_wvw)
        
        assert len(solution) == request_wvw.squad_size
        assert all(isinstance(template, BuildTemplate) for template in solution)
        
        # Check that roles are distributed
        roles = [t.role_type for t in solution]
        assert CompositionMemberRole.HEALER in roles or CompositionMemberRole.SUPPORT in roles

    def test_evaluate_solution_returns_score(self, engine_wvw, request_wvw):
        """Test that evaluate_solution returns a valid score."""
        solution = engine_wvw.greedy_seed(request_wvw)
        score, details = engine_wvw.evaluate_solution(solution, request_wvw)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert "boon_coverage" in details
        assert "role_distribution" in details

    def test_evaluate_solution_calculates_boon_coverage(self, engine_pve, request_pve):
        """Test that evaluate_solution calculates boon coverage correctly."""
        solution = engine_pve.greedy_seed(request_pve)
        score, details = engine_pve.evaluate_solution(solution, request_pve)
        
        boon_coverage = details["boon_coverage"]
        assert "quickness" in boon_coverage
        assert "alacrity" in boon_coverage
        assert all(0.0 <= v <= 1.0 for v in boon_coverage.values())

    def test_local_search_improves_or_maintains_score(self, engine_wvw, request_wvw):
        """Test that local search improves or maintains score."""
        initial_solution = engine_wvw.greedy_seed(request_wvw)
        initial_score, _ = engine_wvw.evaluate_solution(initial_solution, request_wvw)
        
        improved_solution, improved_score = engine_wvw.local_search(
            initial_solution, 
            initial_score, 
            request_wvw,
            time_budget=1.0
        )
        
        # Local search should not make solution worse
        assert improved_score >= initial_score - 0.01  # Allow small float errors
        assert len(improved_solution) == len(initial_solution)

    def test_optimize_respects_time_budget(self, engine_wvw, request_wvw):
        """Test that optimize respects time budget."""
        import time
        
        time_budget = 2.0
        start_time = time.time()
        result = engine_wvw.optimize(request_wvw, time_budget=time_budget)
        elapsed_time = time.time() - start_time
        
        # Should complete within time budget + some overhead (20%)
        assert elapsed_time < time_budget * 1.2
        assert result is not None

    def test_optimize_returns_valid_result(self, engine_pve, request_pve):
        """Test that optimize returns a valid result."""
        result = engine_pve.optimize(request_pve, time_budget=2.0)
        
        assert isinstance(result, CompositionOptimizationResult)
        assert result.composition is not None
        assert result.global_score > 0
        assert len(result.composition.members) == request_pve.squad_size
        assert result.metrics is not None

    def test_optimize_with_fixed_professions(self, engine_pve):
        """Test optimize with fixed professions constraint."""
        request = CompositionOptimizationRequest(
            squad_size=5,
            game_type="pve",
            game_mode="fractale",
            fixed_professions=[1, 1, 2],  # 2 Guardians, 1 Revenant
        )
        
        result = engine_pve.optimize(request, time_budget=2.0)
        
        # Check that fixed professions are respected
        professions = [m.profession_id for m in result.composition.members]
        assert professions.count(1) >= 2  # At least 2 Guardians
        assert 2 in professions  # At least 1 Revenant

    def test_optimize_pve_fractale_composition(self, engine_pve, request_pve):
        """Test optimizing a PvE fractale composition."""
        result = engine_pve.optimize(request_pve, time_budget=2.0)
        
        # PvE fractale should have good boon coverage
        assert result.metrics["boon_coverage"]["quickness"] > 0.5
        assert result.metrics["boon_coverage"]["alacrity"] > 0.5
        assert result.global_score > 0.6

    def test_optimize_wvw_zerg_composition(self, engine_wvw, request_wvw):
        """Test optimizing a WvW zerg composition."""
        result = engine_wvw.optimize(request_wvw, time_budget=3.0)
        
        # WvW should prioritize stability and healing
        assert result.metrics["boon_coverage"].get("stability", 0) > 0.3
        assert result.metrics.get("healing", 0) > 0.5
        assert result.global_score > 0.6

    def test_optimize_respects_min_boon_uptime(self, engine_pve):
        """Test that optimizer respects minimum boon uptime constraints."""
        request = CompositionOptimizationRequest(
            squad_size=5,
            game_type="pve",
            game_mode="fractale",
            min_boon_uptime={"quickness": 0.9, "alacrity": 0.9}
        )
        
        result = engine_pve.optimize(request, time_budget=2.0)
        
        # Should meet minimum requirements (or get close)
        assert result.metrics["boon_coverage"]["quickness"] >= 0.8
        assert result.metrics["boon_coverage"]["alacrity"] >= 0.8


class TestOptimizeCompositionFunction:
    """Test optimize_composition entry point function."""

    def test_optimize_composition_wvw(self):
        """Test optimize_composition for WvW."""
        request = CompositionOptimizationRequest(
            squad_size=10,
            game_type="wvw",
            game_mode="roaming",
        )
        
        result = optimize_composition(request, time_budget=2.0)
        
        assert isinstance(result, CompositionOptimizationResult)
        assert result.composition.squad_size == 10
        assert len(result.composition.members) == 10

    def test_optimize_composition_pve(self):
        """Test optimize_composition for PvE."""
        request = CompositionOptimizationRequest(
            squad_size=5,
            game_type="pve",
            game_mode="fractale",
        )
        
        result = optimize_composition(request, time_budget=2.0)
        
        assert isinstance(result, CompositionOptimizationResult)
        assert result.composition.squad_size == 5
        assert len(result.composition.members) == 5

    def test_optimize_composition_respects_game_type(self):
        """Test that game_type affects the optimization."""
        request_wvw = CompositionOptimizationRequest(
            squad_size=10,
            game_type="wvw",
            game_mode="zerg",
        )
        
        request_pve = CompositionOptimizationRequest(
            squad_size=10,
            game_type="pve",
            game_mode="raid",
        )
        
        result_wvw = optimize_composition(request_wvw, time_budget=2.0)
        result_pve = optimize_composition(request_pve, time_budget=2.0)
        
        # Results should be different due to mode-specific effects
        # WvW and PvE have different trait behaviors (e.g., Herald)
        assert result_wvw.composition.name != result_pve.composition.name


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_optimize_minimum_squad_size(self):
        """Test optimizing with minimum squad size (1)."""
        engine = OptimizerEngine(game_type="pve", game_mode="openworld")
        request = CompositionOptimizationRequest(
            squad_size=1,
            game_type="pve",
            game_mode="openworld",
        )
        
        result = engine.optimize(request, time_budget=1.0)
        
        assert len(result.composition.members) == 1
        assert result.global_score > 0

    def test_optimize_large_squad_size(self):
        """Test optimizing with large squad size."""
        engine = OptimizerEngine(game_type="wvw", game_mode="zerg")
        request = CompositionOptimizationRequest(
            squad_size=50,
            game_type="wvw",
            game_mode="zerg",
        )
        
        # Should complete even with large squad
        result = engine.optimize(request, time_budget=5.0)
        
        assert len(result.composition.members) == 50
        assert result.global_score > 0

    def test_optimize_with_empty_fixed_professions(self):
        """Test optimize with empty fixed_professions list."""
        engine = OptimizerEngine(game_type="pve", game_mode="fractale")
        request = CompositionOptimizationRequest(
            squad_size=5,
            game_type="pve",
            game_mode="fractale",
            fixed_professions=[],
        )
        
        result = engine.optimize(request, time_budget=2.0)
        
        assert len(result.composition.members) == 5
        assert result.global_score > 0
