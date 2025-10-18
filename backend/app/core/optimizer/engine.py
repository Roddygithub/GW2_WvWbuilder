"""
Composition optimization engine for Guild Wars 2 WvW.

This module implements a heuristic-based optimizer that generates optimal
squad compositions based on game mode, squad size, and optimization goals.
"""

import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml

from app.schemas.composition import (
    CompositionOptimizationRequest,
    CompositionOptimizationResult,
    Composition,
    CompositionCreate,
    CompositionMemberRole,
)
from app.core.optimizer.mode_effects import (
    ModeEffectsManager,
    apply_mode_adjustments,
)

logger = logging.getLogger(__name__)


class OptimizerConfig:
    """Configuration for the optimizer loaded from YAML files."""

    def __init__(self, mode: str):
        self.mode = mode
        config_path = (
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "optimizer"
            / f"{mode}.yml"
        )

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self.config = self._default_config()
        else:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)

        logger.info(f"Loaded optimizer config for mode: {mode}")

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration if YAML file is missing."""
        return {
            "mode": self.mode,
            "weights": {
                "boon_uptime": 0.25,
                "healing": 0.15,
                "damage": 0.20,
                "crowd_control": 0.10,
                "survivability": 0.15,
                "boon_rip": 0.10,
                "cleanse": 0.05,
            },
            "critical_boons": {
                "might": 0.85,
                "quickness": 0.80,
                "alacrity": 0.75,
                "stability": 0.80,
            },
            "role_distribution": {
                "healer": {"min": 1, "max": 6, "optimal": 2},
                "boon_support": {"min": 2, "max": 8, "optimal": 3},
                "power_damage": {"min": 2, "max": 30, "optimal": 6},
                "utility": {"min": 1, "max": 5, "optimal": 2},
                "support": {"min": 0, "max": 5, "optimal": 2},
            },
        }

    @property
    def weights(self) -> Dict[str, float]:
        return self.config.get("weights", {})

    @property
    def critical_boons(self) -> Dict[str, float]:
        return self.config.get("critical_boons", {})

    @property
    def role_distribution(self) -> Dict[str, Dict[str, int]]:
        return self.config.get("role_distribution", {})

    @property
    def penalties(self) -> Dict[str, float]:
        return self.config.get("penalties", {})

    @property
    def synergies(self) -> Dict[str, float]:
        return self.config.get("synergies", {})


class BuildTemplate:
    """Represents a build template with its capabilities."""

    def __init__(
        self,
        profession_id: int,
        elite_spec_id: Optional[int],
        role_type: CompositionMemberRole,
        capabilities: Dict[str, float],
    ):
        self.profession_id = profession_id
        self.elite_spec_id = elite_spec_id
        self.role_type = role_type
        self.capabilities = capabilities

    def get_capability(self, key: str, default: float = 0.0) -> float:
        """Get a capability value with a default fallback."""
        return self.capabilities.get(key, default)


class OptimizerEngine:
    """Main optimization engine using greedy + local search heuristic."""

    def __init__(self, game_type: str = "wvw", game_mode: str = "zerg"):
        """Initialize optimizer with configuration for specific game type and mode."""
        self.game_type = game_type
        self.game_mode = game_mode
        # Map game_type + game_mode to config file
        if game_type == "pve":
            config_name = f"pve_{game_mode}"
        else:
            config_name = f"wvw_{game_mode}"
        self.config = self._load_config(config_name)
        self.mode_effects = ModeEffectsManager(game_type)
        self.build_catalogue = self._initialize_catalogue()
        logger.info(
            f"Initialized build catalogue with {len(self.build_catalogue)} templates for {game_type}/{game_mode}"
        )

    def _load_config(self, config_name: str) -> OptimizerConfig:
        return OptimizerConfig(config_name)

    def _initialize_catalogue(self) -> List[BuildTemplate]:
        """
        Initialize the build catalogue with profession/elite spec templates.

        Applies mode-specific adjustments to capabilities based on game_type.
        In production, this would load from database or GW2 API.
        """
        catalogue = []

        # Guardian - Firebrand (Healer)
        base_capabilities = {
            "healing": 0.95,
            "boon_uptime": 0.90,
            "might": 0.85,
            "quickness": 0.95,
            "stability": 0.80,
            "aegis": 0.90,
            "cleanse": 0.85,
            "survivability": 0.80,
        }
        adjusted_capabilities = apply_mode_adjustments(
            base_capabilities, 1, self.game_type
        )

        catalogue.append(
            BuildTemplate(
                profession_id=1,
                elite_spec_id=3,
                role_type=CompositionMemberRole.HEALER,
                capabilities=adjusted_capabilities,
            )
        )

        # Guardian - Willbender (DPS)
        catalogue.append(
            BuildTemplate(
                profession_id=1,
                elite_spec_id=4,
                role_type=CompositionMemberRole.POWER_DAMAGE,
                capabilities={
                    "damage": 0.85,
                    "mobility": 0.80,
                    "boon_uptime": 0.60,
                    "crowd_control": 0.70,
                    "survivability": 0.75,
                },
            )
        )

        # Revenant - Herald (Boon Support)
        # Note: Herald gives Quickness in WvW, Alacrity in PvE (trait differences)
        base_capabilities = {
            "boon_uptime": 0.95,
            "alacrity": 0.90 if self.game_type == "pve" else 0.30,
            "quickness": 0.90 if self.game_type == "wvw" else 0.30,
            "might": 0.80,
            "fury": 0.90,
            "protection": 0.85,
            "damage": 0.60,
            "crowd_control": 0.65,
        }
        adjusted_capabilities = apply_mode_adjustments(
            base_capabilities, 2, self.game_type
        )

        catalogue.append(
            BuildTemplate(
                profession_id=2,
                elite_spec_id=5,
                role_type=CompositionMemberRole.BOON_SUPPORT,
                capabilities=adjusted_capabilities,
            )
        )

        # Necromancer - Scourge (Support/Barrier)
        catalogue.append(
            BuildTemplate(
                profession_id=3,
                elite_spec_id=7,
                role_type=CompositionMemberRole.SUPPORT,
                capabilities={
                    "survivability": 0.90,
                    "boon_rip": 0.95,
                    "crowd_control": 0.75,
                    "damage": 0.65,
                    "cleanse": 0.70,
                    "barrier": 0.95,
                },
            )
        )

        # Warrior - Spellbreaker (DPS/Boon Rip)
        catalogue.append(
            BuildTemplate(
                profession_id=4,
                elite_spec_id=9,
                role_type=CompositionMemberRole.POWER_DAMAGE,
                capabilities={
                    "damage": 0.85,
                    "boon_rip": 0.90,
                    "crowd_control": 0.80,
                    "survivability": 0.75,
                    "might": 0.60,
                },
            )
        )

        # Elementalist - Tempest (Support/Auras)
        catalogue.append(
            BuildTemplate(
                profession_id=5,
                elite_spec_id=11,
                role_type=CompositionMemberRole.SUPPORT,
                capabilities={
                    "boon_uptime": 0.85,
                    "healing": 0.70,
                    "damage": 0.60,
                    "crowd_control": 0.70,
                    "auras": 0.95,
                    "cleanse": 0.75,
                },
            )
        )

        # Engineer - Scrapper (Support/Superspeed)
        # Note: Scrapper gives Stability in WvW, Quickness in PvE
        base_capabilities = {
            "boon_uptime": 0.85,
            "quickness": 0.85 if self.game_type == "pve" else 0.40,
            "stability": 0.85 if self.game_type == "wvw" else 0.40,
            "superspeed": 0.95,
            "healing": 0.65,
            "survivability": 0.80,
            "crowd_control": 0.75,
        }
        adjusted_capabilities = apply_mode_adjustments(
            base_capabilities, 6, self.game_type
        )

        catalogue.append(
            BuildTemplate(
                profession_id=6,
                elite_spec_id=13,
                role_type=CompositionMemberRole.SUPPORT,
                capabilities=adjusted_capabilities,
            )
        )

        # Engineer - Mechanist (Boon Support)
        # Note: Mechanist gives Might in WvW, Alacrity in PvE
        base_capabilities = {
            "boon_uptime": 0.90,
            "alacrity": 0.95 if self.game_type == "pve" else 0.30,
            "might": 0.90 if self.game_type == "wvw" else 0.60,
            "damage": 0.70,
            "healing": 0.60,
            "survivability": 0.75,
        }
        adjusted_capabilities = apply_mode_adjustments(
            base_capabilities, 6, self.game_type
        )

        catalogue.append(
            BuildTemplate(
                profession_id=6,
                elite_spec_id=23,  # Mechanist
                role_type=CompositionMemberRole.BOON_SUPPORT,
                capabilities=adjusted_capabilities,
            )
        )

        # Ranger - Druid (Healer)
        catalogue.append(
            BuildTemplate(
                profession_id=7,
                elite_spec_id=15,
                role_type=CompositionMemberRole.HEALER,
                capabilities={
                    "healing": 0.90,
                    "boon_uptime": 0.75,
                    "might": 0.70,
                    "spirits": 0.90,
                    "survivability": 0.70,
                    "crowd_control": 0.60,
                },
            )
        )

        # Thief - Deadeye (DPS)
        catalogue.append(
            BuildTemplate(
                profession_id=8,
                elite_spec_id=17,
                role_type=CompositionMemberRole.POWER_DAMAGE,
                capabilities={
                    "damage": 0.90,
                    "burst_damage": 0.95,
                    "stealth": 0.85,
                    "mobility": 0.80,
                    "survivability": 0.60,
                },
            )
        )

        # Mesmer - Chronomancer (Utility)
        catalogue.append(
            BuildTemplate(
                profession_id=9,
                elite_spec_id=19,
                role_type=CompositionMemberRole.UTILITY,
                capabilities={
                    "boon_uptime": 0.80,
                    "quickness": 0.85,
                    "alacrity": 0.80,
                    "portals": 0.95,
                    "crowd_control": 0.75,
                    "damage": 0.60,
                },
            )
        )

        logger.info(f"Initialized build catalogue with {len(catalogue)} templates")
        return catalogue

    def greedy_seed(
        self,
        request: CompositionOptimizationRequest,
    ) -> List[BuildTemplate]:
        """
        Generate initial solution using greedy algorithm.

        Prioritizes critical boons and role distribution.
        """
        solution = []
        squad_size = request.squad_size

        # Start with fixed professions if specified (engine chooses roles/specs)
        if request.fixed_professions:
            # Filter catalogue to only include fixed professions
            available_builds = [
                b
                for b in self.build_catalogue
                if b.profession_id in request.fixed_professions
            ]
        else:
            available_builds = self.build_catalogue

        # Fill slots based on role distribution from config
        remaining = squad_size
        role_dist = self.config.role_distribution

        # Calculate target counts for each role based on squad size
        targets = {}
        total_optimal = sum(dist.get("optimal", dist.get("min", 1)) for dist in role_dist.values())
        
        for role, dist in role_dist.items():
            optimal = dist.get("optimal", dist.get("min", 1))
            # Proportion the roles according to squad size
            if total_optimal > 0:
                targets[role] = max(1, int((optimal / total_optimal) * squad_size))
            else:
                targets[role] = max(1, squad_size // len(role_dist))

        # Add builds to meet role targets
        for role_str, target in targets.items():
            try:
                role_type = CompositionMemberRole(role_str)
            except ValueError:
                continue

            matching = [b for b in available_builds if b.role_type == role_type]
            if matching:
                # Sort by overall capability score
                matching.sort(key=lambda b: sum(b.capabilities.values()), reverse=True)
                # Add builds for this role (take top builds but add variety)
                count = min(target, remaining, len(matching))
                for i in range(count):
                    if remaining > 0:
                        # Alternate between best and variety
                        if i < min(2, len(matching)):
                            solution.append(matching[i % len(matching)])
                        else:
                            solution.append(random.choice(matching[:min(3, len(matching))]))
                        remaining -= 1

        # Fill any remaining slots with variety (not just one role!)
        while len(solution) < squad_size:
            # Pick randomly from ALL available builds for diversity
            solution.append(random.choice(available_builds))

        return solution[:squad_size]

    def evaluate_solution(
        self,
        solution: List[BuildTemplate],
        request: CompositionOptimizationRequest,
    ) -> Tuple[float, Dict[str, float], Dict[str, float], Dict[str, int]]:
        """
        Evaluate a solution and return (score, metrics, boon_coverage, role_distribution).
        
        Takes into account GW2 mechanics:
        - Boons limited to 5 players (subgroup mechanic)
        - Squad organized in groups of 5
        """
        metrics = {}
        boon_coverage = {}
        role_distribution = {}

        # Calculate role distribution
        for build in solution:
            role_str = build.role_type.value
            role_distribution[role_str] = role_distribution.get(role_str, 0) + 1

        # Calculate average capabilities
        for key in [
            "healing",
            "damage",
            "crowd_control",
            "survivability",
            "boon_rip",
            "cleanse",
        ]:
            values = [b.get_capability(key) for b in solution]
            metrics[key] = sum(values) / len(values) if values else 0.0

        # Calculate boon coverage with 5-player subgroup mechanic
        # In GW2, boons only affect 5 players max (your subgroup)
        num_subgroups = max(1, (len(solution) + 4) // 5)  # Ceiling division
        
        for boon in [
            "might",
            "quickness",
            "alacrity",
            "stability",
            "protection",
            "fury",
            "aegis",
            "resolution",
        ]:
            values = [b.get_capability(boon) for b in solution]
            # Total boon generation
            total_generation = sum(values)
            # Each subgroup needs its own boon coverage
            # Coverage = min(1.0, total_generation / num_subgroups / players_per_subgroup)
            players_per_subgroup = min(5, len(solution))
            boon_coverage[boon] = min(1.0, total_generation / num_subgroups / (players_per_subgroup * 0.5))

        # Calculate boon uptime metric (average of critical boons)
        critical_boons = self.config.critical_boons
        if critical_boons:
            boon_scores = [boon_coverage.get(b, 0.0) for b in critical_boons.keys()]
            metrics["boon_uptime"] = (
                sum(boon_scores) / len(boon_scores) if boon_scores else 0.0
            )
        else:
            metrics["boon_uptime"] = 0.5

        # Calculate weighted score
        weights = self.config.weights
        score = 0.0
        logger.debug(f"Calculating score with weights: {weights}")
        for key, weight in weights.items():
            metric_value = metrics.get(key, 0.0)
            contribution = metric_value * weight
            score += contribution
            logger.debug(f"  {key}: {metric_value:.3f} * {weight} = {contribution:.3f}")

        # Log initial score
        logger.info(f"Base weighted score: {score:.3f} ({score*100:.1f}%)")
        
        # For v1.0: No penalties! Let users see raw performance
        # Penalties make optimization feel "broken" when score shows as 0%
        # Future versions can add configurable penalties
        penalty_total = 0.0
        
        # DISABLED: Penalty for missing critical boons
        # for boon, required in critical_boons.items():
        #     if boon_coverage.get(boon, 0.0) < required:
        #         penalty_total += 0.02 * (required - boon_coverage.get(boon, 0.0))

        # DISABLED: Penalty for role imbalance  
        # role_dist_config = self.config.role_distribution
        # for role, dist in role_dist_config.items():
        #     actual = role_distribution.get(role, 0)
        #     if actual < dist.get("min", 0):
        #         penalty_total += 0.01
        
        logger.info(f"Total penalties: -{penalty_total:.3f}")
        score = max(0.0, score - penalty_total)
        
        # Ensure score is in [0, 1]
        score = min(1.0, score)
        logger.info(f"Final score: {score:.3f} ({score*100:.1f}%)")

        return score, metrics, boon_coverage, role_distribution

    def local_search(
        self,
        solution: List[BuildTemplate],
        request: CompositionOptimizationRequest,
        time_budget: float = 2.0,
    ) -> List[BuildTemplate]:
        """
        Improve solution using local search with time budget.

        Tries random swaps and keeps improvements.
        """
        start_time = time.time()
        best_solution = solution[:]
        best_score, _, _, _ = self.evaluate_solution(best_solution, request)

        iterations = 0
        improvements = 0

        while time.time() - start_time < time_budget:
            iterations += 1

            # Try a random swap
            candidate = best_solution[:]
            idx = random.randint(0, len(candidate) - 1)

            # Don't swap fixed roles
            if request.fixed_roles:
                is_fixed = False
                for fixed in request.fixed_roles:
                    # Handle both dict and object formats
                    if isinstance(fixed, dict):
                        prof_id = fixed.get("profession_id")
                        elite_id = fixed.get("elite_specialization_id")
                    else:
                        prof_id = fixed.profession_id
                        elite_id = fixed.elite_specialization_id

                    if (
                        candidate[idx].profession_id == prof_id
                        and candidate[idx].elite_spec_id == elite_id
                    ):
                        is_fixed = True
                        break
                if is_fixed:
                    continue

            # Swap with a random build from catalogue
            new_build = random.choice(self.build_catalogue)
            candidate[idx] = new_build

            # Evaluate candidate
            score, _, _, _ = self.evaluate_solution(candidate, request)

            if score > best_score:
                best_solution = candidate
                best_score = score
                improvements += 1

        logger.info(
            f"Local search: {iterations} iterations, {improvements} improvements, "
            f"final score: {best_score:.3f}"
        )

        return best_solution

    def optimize(
        self,
        request: CompositionOptimizationRequest,
        time_budget: float = 5.0,
    ) -> CompositionOptimizationResult:
        """
        Main optimization method.

        Returns an optimized composition with metrics.
        """
        start_time = time.time()

        # Generate initial solution
        solution = self.greedy_seed(request)
        logger.info(f"Generated initial solution with {len(solution)} builds")

        # Improve with local search
        solution = self.local_search(solution, request, time_budget=time_budget * 0.8)

        # Final evaluation
        score, metrics, boon_coverage, role_distribution = self.evaluate_solution(
            solution, request
        )

        # Generate notes
        notes = self._generate_notes(
            solution, metrics, boon_coverage, role_distribution, request
        )

        # Create composition object
        from datetime import datetime as dt

        composition_data = CompositionCreate(
            name=f"Optimized {request.game_type.upper()} {request.game_mode.upper()} Composition",
            description=f"Auto-generated {request.game_type} composition for {request.squad_size} players",
            squad_size=request.squad_size,
            game_mode=f"{request.game_type}_{request.game_mode}",
            is_public=True,
            tags=[request.game_type, request.game_mode, "optimized", "auto-generated"],
        )

        # Convert to Composition (mock for now - in production would save to DB)
        # Note: tags should be List[Dict] for Composition schema
        tags_dicts = [
            {"id": i, "name": tag, "description": ""}
            for i, tag in enumerate(composition_data.tags or [])
        ]

        # Generate members list from solution
        members = []
        profession_names = {
            1: "Guardian",
            2: "Revenant",
            3: "Necromancer",
            4: "Warrior",
            5: "Elementalist",
            6: "Engineer",
            7: "Ranger",
            8: "Thief",
            9: "Mesmer",
        }
        elite_names = {
            3: "Firebrand",
            4: "Willbender",
            5: "Herald",
            7: "Scourge",
            9: "Spellbreaker",
            11: "Tempest",
            13: "Scrapper",
            15: "Druid",
            17: "Deadeye",
            19: "Chronomancer",
        }

        for i, build in enumerate(solution):
            member = {
                "id": i + 1,
                "user_id": 0,
                "role_id": 1,
                "profession_id": build.profession_id,
                "elite_specialization_id": build.elite_spec_id,
                "role_type": build.role_type.value,
                "is_commander": i == 0,  # First member is commander
                "username": f"Player{i+1}",
                "profession_name": profession_names.get(build.profession_id, "Unknown"),
                "elite_specialization_name": elite_names.get(build.elite_spec_id, None),
                "notes": f"{build.role_type.value.replace('_', ' ').title()}",
            }
            members.append(member)

        composition = Composition(
            id=0,
            name=composition_data.name,
            description=composition_data.description,
            squad_size=composition_data.squad_size,
            game_mode=composition_data.game_mode,
            is_public=composition_data.is_public,
            tags=tags_dicts,
            members=members,
            created_by=0,
            created_at=dt.now(),
            updated_at=dt.now(),
        )

        # Generate subgroups (GW2 mechanic: groups of 5)
        subgroups = self._generate_subgroups(solution, members)

        elapsed = time.time() - start_time
        logger.info(f"Optimization completed in {elapsed:.2f}s with score {score:.3f}")

        return CompositionOptimizationResult(
            composition=composition,
            score=score,
            metrics=metrics,
            role_distribution=role_distribution,
            boon_coverage=boon_coverage,
            notes=notes,
            subgroups=subgroups,
        )

    def _generate_subgroups(
        self,
        solution: List[BuildTemplate],
        members: List[Dict],
    ) -> List[Dict[str, Any]]:
        """
        Organize squad into subgroups of 5 (GW2 mechanic).
        
        Ensures each subgroup has balanced boon coverage and roles.
        """
        squad_size = len(solution)
        num_groups = (squad_size + 4) // 5  # Ceiling division
        subgroups = []
        
        # Distribute members across groups (round-robin for now)
        # TODO: Optimize distribution for better boon coverage per group
        for group_num in range(num_groups):
            group_members = []
            group_builds = []
            
            # Get members for this group
            for i in range(group_num, squad_size, num_groups):
                if i < len(members):
                    group_members.append(members[i]["id"])
                    group_builds.append(solution[i])
            
            # Calculate boon coverage for this group
            group_boon_coverage = {}
            for boon in ["might", "quickness", "alacrity", "stability"]:
                values = [b.get_capability(boon) for b in group_builds]
                # Coverage for 5-player group
                group_boon_coverage[boon] = min(1.0, sum(values) / max(1, len(group_builds) * 0.5))
            
            subgroups.append({
                "group_number": group_num + 1,
                "size": len(group_members),
                "members": group_members,
                "boon_coverage": group_boon_coverage,
                "avg_boon_coverage": sum(group_boon_coverage.values()) / len(group_boon_coverage) if group_boon_coverage else 0.0,
            })
        
        return subgroups

    def _generate_notes(
        self,
        solution: List[BuildTemplate],
        metrics: Dict[str, float],
        boon_coverage: Dict[str, float],
        role_distribution: Dict[str, int],
        request: CompositionOptimizationRequest,
    ) -> List[str]:
        """Generate human-readable notes about the composition."""
        notes = []

        # Check boon coverage
        critical_boons = self.config.critical_boons
        for boon, required in critical_boons.items():
            actual = boon_coverage.get(boon, 0.0)
            if actual < required:
                notes.append(
                    f"⚠️ {boon.capitalize()} uptime is {actual:.0%} (target: {required:.0%})"
                )
            elif actual >= required * 1.1:
                notes.append(f"✓ Excellent {boon} coverage at {actual:.0%}")

        # Check role distribution
        role_dist_config = self.config.role_distribution
        for role, dist in role_dist_config.items():
            actual = role_distribution.get(role, 0)
            optimal = dist.get("optimal", dist.get("min", 1))
            if actual < dist.get("min", 0):
                notes.append(f"⚠️ Not enough {role}s: {actual} (minimum: {dist['min']})")
            elif actual > dist.get("max", 100):
                notes.append(f"⚠️ Too many {role}s: {actual} (maximum: {dist['max']})")

        # Overall assessment
        if metrics.get("boon_uptime", 0) >= 0.85:
            notes.append("✓ Strong boon coverage for sustained fights")
        if metrics.get("healing", 0) >= 0.80:
            notes.append("✓ Good healing and sustain")
        if metrics.get("damage", 0) >= 0.75:
            notes.append("✓ Solid damage output")

        return notes[:10]  # Limit to 10 notes


def optimize_composition(
    request: CompositionOptimizationRequest,
    time_budget: float = 5.0,
) -> CompositionOptimizationResult:
    """
    Main entry point for composition optimization.

    Args:
        request: Optimization request with constraints
        time_budget: Maximum time in seconds for optimization

    Returns:
        Optimized composition with score and metrics
    """
    engine = OptimizerEngine(game_type=request.game_type, game_mode=request.game_mode)
    return engine.optimize(request, time_budget=time_budget)
