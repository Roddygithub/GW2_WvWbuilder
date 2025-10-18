"""
Meta-based constraints for WvW optimizer.

Based on community meta compositions from:
- MetaBattle (https://metabattle.com/wiki/WvW)
- GuildJen (https://guildjen.com/gw2-wvw-zerg-builds/)
- Hardstuck (https://hardstuck.gg/gw2/guides/events/squads-and-commanding/)
- Reddit WvW Community

Version: v3.7.3
Date: 2025-10-17
"""

from typing import Dict, List, Tuple
from ortools.sat.python import cp_model


# Build specialization mapping (to be updated with actual IDs from database)
BUILD_SPECS = {
    "Firebrand": 101,
    "Scrapper": 102,
    "Herald": 103,
    "Tempest": 104,
    "Scourge": 105,
    "Mechanist": 106,
    "Reaper": 107,
    "Weaver": 108,
    "Holosmith": 109,
    "Berserker": 110,
    "Mirage": 111,
    "Vindicator": 112,
    "Dragonhunter": 113,
    "Willbender": 114,
    "Chronomancer": 115,
    "Specter": 116,
    "Catalyst": 117,
    "Druid": 118,
    "Spellbreaker": 119,
    "Daredevil": 120,
}


def get_mode_constraints(mode: str, squad_size: int) -> Dict:
    """
    Returns constraints, targets, and weights for a given WvW mode.

    Args:
        mode: "zerg" (25-50), "havoc" (10-20), or "roaming" (1-5)
        squad_size: Number of players

    Returns:
        Dict with keys: "build_constraints", "targets", "weights"
    """
    if squad_size >= 25:
        return get_zerg_constraints(squad_size)
    elif squad_size >= 10:
        return get_havoc_constraints(squad_size)
    else:
        return get_roaming_constraints(squad_size)


def get_zerg_constraints(squad_size: int) -> Dict:
    """
    Constraints for Zerg mode (25-50 players).

    Meta composition:
    - Firebrand: 20% (8-12 for 50p)
    - Scrapper: 10-16% (5-10 for 50p)
    - Herald: 10% (4-7 for 50p)
    - Tempest: 6-10% (2-6 for 50p)
    - Scourge: 12% (3-10 for 50p)
    - DPS: 44-54% (22-27 for 50p)
    """
    # Scale constraints based on squad size
    scale = squad_size / 50.0

    build_constraints = {
        "Firebrand": {
            "min": max(2, int(8 * scale)),
            "max": int(12 * scale),
            "per_group_min": 1,  # At least 1 per subgroup
        },
        "Scrapper": {
            "min": max(1, int(5 * scale)),
            "max": int(10 * scale),
            "per_group_min": 0,  # 0 or 1 per subgroup
        },
        "Herald": {
            "min": max(1, int(4 * scale)),
            "max": int(7 * scale),
            "per_group_min": 0,
        },
        "Tempest": {
            "min": max(1, int(2 * scale)),
            "max": int(6 * scale),
            "per_group_min": 0,
        },
        "Scourge": {
            "min": max(1, int(3 * scale)),
            "max": int(10 * scale),
            "per_group_min": 0,
        },
    }

    targets = {
        "quickness_uptime": 0.95,  # 95% (critical)
        "alacrity_uptime": 0.70,  # 70% (useful)
        "resistance_uptime": 0.85,  # 85% (vs conditions)
        "protection_uptime": 0.70,  # 70% (mitigation)
        "stability_sources": 3,  # 3 sources minimum
        "might_stacks": 20,  # 20 stacks
        "fury_uptime": 0.80,  # 80%
    }

    weights = {
        "quickness": 1.0,  # Maximum priority
        "stability": 1.0,  # Critical in Zerg
        "resistance": 0.95,  # Very important (conditions)
        "might": 0.85,  # Important (DPS)
        "fury": 0.80,  # Important (crit)
        "protection": 0.75,  # Mitigation
        "alacrity": 0.70,  # Useful but not critical
        "dps": 0.60,  # Moderate
        "sustain": 0.55,  # Moderate
    }

    return {
        "build_constraints": build_constraints,
        "targets": targets,
        "weights": weights,
    }


def get_havoc_constraints(squad_size: int) -> Dict:
    """
    Constraints for Havoc mode (10-20 players).

    Meta composition:
    - Firebrand: 20% (2-4 for 15p)
    - Scrapper: 13% (1-3 for 15p)
    - Herald: 13% (1-3 for 15p)
    - Tempest: 7% (0-2 for 15p)
    - Scourge: 13% (1-4 for 15p)
    - DPS: 47-60% (7-9 for 15p)
    """
    scale = squad_size / 15.0

    build_constraints = {
        "Firebrand": {
            "min": max(1, int(2 * scale)),
            "max": int(4 * scale),
            "per_group_min": 1,
        },
        "Scrapper": {
            "min": max(1, int(1 * scale)),
            "max": int(3 * scale),
            "per_group_min": 0,
        },
        "Herald": {
            "min": max(1, int(1 * scale)),
            "max": int(3 * scale),
            "per_group_min": 0,
        },
        "Tempest": {
            "min": 0,
            "max": int(2 * scale),
            "per_group_min": 0,
        },
        "Scourge": {
            "min": max(1, int(1 * scale)),
            "max": int(4 * scale),
            "per_group_min": 0,
        },
    }

    targets = {
        "quickness_uptime": 0.90,  # 90%
        "alacrity_uptime": 0.60,  # 60% (less critical)
        "resistance_uptime": 0.80,  # 80%
        "protection_uptime": 0.65,  # 65%
        "stability_sources": 2,  # 2 sources minimum
        "might_stacks": 18,  # 18 stacks
        "fury_uptime": 0.75,  # 75%
    }

    weights = {
        "quickness": 1.0,
        "stability": 1.0,
        "resistance": 0.90,
        "dps": 0.80,  # More important in Havoc
        "might": 0.75,
        "fury": 0.70,
        "protection": 0.65,
        "sustain": 0.60,
        "alacrity": 0.55,  # Less critical
    }

    return {
        "build_constraints": build_constraints,
        "targets": targets,
        "weights": weights,
    }


def get_roaming_constraints(squad_size: int) -> Dict:
    """
    Constraints for Roaming mode (1-5 players).

    Meta composition:
    - Self-sufficient builds (Celestial, Hybrid)
    - No strict composition requirements
    - Focus on burst, sustain, and mobility
    """
    build_constraints = {
        # No strict constraints, but encourage diversity
        # Max 2 of the same build
        "_max_same_build": 2,
        # At least 1 sustain build (Scrapper, Tempest, Druid)
        "_min_sustain_builds": 1,
        # At least 1 burst build (Weaver, Willbender, Berserker)
        "_min_burst_builds": 1,
    }

    targets = {
        "quickness_uptime": 0.50,  # 50% (personal)
        "alacrity_uptime": 0.30,  # 30% (personal)
        "resistance_uptime": 0.60,  # 60%
        "protection_uptime": 0.50,  # 50%
        "stability_sources": 1,  # 1 source minimum
        "might_stacks": 15,  # 15 stacks
        "fury_uptime": 0.70,  # 70%
    }

    weights = {
        "dps": 1.0,  # Maximum priority (burst)
        "sustain": 0.95,  # Very important (survival)
        "mobility": 0.90,  # Very important (kiting)
        "stability": 0.80,
        "resistance": 0.75,
        "might": 0.60,
        "fury": 0.60,
        "quickness": 0.40,  # Less critical
        "alacrity": 0.30,  # Less critical
    }

    return {
        "build_constraints": build_constraints,
        "targets": targets,
        "weights": weights,
    }


def apply_meta_constraints(
    model: cp_model.CpModel,
    x: Dict,  # x[i, j]: player i assigned to build j
    g: Dict,  # g[i, k]: player i assigned to group k
    players: List,
    builds: List,
    build_index: Dict[int, int],
    group_count: int,
    mode: str,
    squad_size: int,
) -> Tuple[Dict, Dict]:
    """
    Apply meta-based constraints to the CP-SAT model.

    Returns:
        Tuple of (targets, weights) for the objective function
    """
    meta = get_mode_constraints(mode, squad_size)
    build_constraints = meta["build_constraints"]

    # Map build names to IDs
    spec_to_id = {spec: bid for spec, bid in BUILD_SPECS.items()}

    # Apply build count constraints
    for spec_name, constraints in build_constraints.items():
        if spec_name.startswith("_"):
            # Special constraint (handled separately)
            continue

        build_id = spec_to_id.get(spec_name)
        if not build_id or build_id not in build_index:
            continue

        j = build_index[build_id]
        build_count = sum(x[(i, j)] for i in range(len(players)) if (i, j) in x)

        # Min/Max constraints
        if "min" in constraints:
            model.Add(build_count >= constraints["min"])
        if "max" in constraints:
            model.Add(build_count <= constraints["max"])

        # Per-group constraints
        if "per_group_min" in constraints and constraints["per_group_min"] > 0:
            for k in range(group_count):
                group_build_count = sum(
                    x[(i, j)] * g[(i, k)]
                    for i in range(len(players))
                    if (i, j) in x and (i, k) in g
                )
                model.Add(group_build_count >= constraints["per_group_min"])

    # Apply special constraints
    if "_max_same_build" in build_constraints:
        max_same = build_constraints["_max_same_build"]
        for j in range(len(builds)):
            build_count = sum(x[(i, j)] for i in range(len(players)) if (i, j) in x)
            model.Add(build_count <= max_same)

    return meta["targets"], meta["weights"]


def get_meta_description(mode: str, squad_size: int) -> str:
    """
    Returns a human-readable description of the meta constraints.
    """
    if squad_size >= 25:
        return (
            f"Zerg mode ({squad_size} players): "
            f"20% Firebrand, 12% Scrapper, 10% Herald, 8% Tempest, 12% Scourge, 48% DPS"
        )
    elif squad_size >= 10:
        return (
            f"Havoc mode ({squad_size} players): "
            f"20% Firebrand, 13% Scrapper, 13% Herald, 7% Tempest, 13% Scourge, 53% DPS"
        )
    else:
        return (
            f"Roaming mode ({squad_size} players): "
            f"Self-sufficient builds, focus on burst/sustain/mobility"
        )
