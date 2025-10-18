from __future__ import annotations

from typing import Dict

# Presets for different WvW modes (soft-only, no hard quotas)
# These are default weight configurations that can be overridden by user sliders

PRESET_WEIGHTS: Dict[str, Dict[str, float]] = {
    "zerg": {
        # Zerg: stability and quickness critical, resistance high
        "quickness": 1.0,
        "alacrity": 0.7,
        "stability": 1.0,
        "resistance": 0.95,
        "protection": 0.75,
        "might": 0.85,
        "fury": 0.8,
        "dps": 0.6,
        "sustain": 0.55,
        # Soft-only extras
        "dup_penalty_group": 0.25,
        "dup_penalty_global": 0.08,
        "diversity_reward": 0.04,
        "synergy": 0.06,
    },
    "havoc": {
        # Havoc: quickness/stability still important, DPS higher
        "quickness": 1.0,
        "alacrity": 0.55,
        "stability": 1.0,
        "resistance": 0.9,
        "protection": 0.65,
        "might": 0.75,
        "fury": 0.7,
        "dps": 0.8,
        "sustain": 0.6,
        # Soft-only extras
        "dup_penalty_group": 0.2,
        "dup_penalty_global": 0.05,
        "diversity_reward": 0.05,
        "synergy": 0.05,
    },
    "roaming": {
        # Roaming: DPS and sustain priority, less group boons
        "quickness": 0.4,
        "alacrity": 0.3,
        "stability": 0.8,
        "resistance": 0.75,
        "protection": 0.5,
        "might": 0.6,
        "fury": 0.6,
        "dps": 1.0,
        "sustain": 0.95,
        # Soft-only extras
        "dup_penalty_group": 0.3,
        "dup_penalty_global": 0.1,
        "diversity_reward": 0.06,
        "synergy": 0.04,
    },
    "defense": {
        # Defense: stability, protection, sustain
        "quickness": 0.9,
        "alacrity": 0.6,
        "stability": 1.0,
        "resistance": 0.85,
        "protection": 0.9,
        "might": 0.7,
        "fury": 0.6,
        "dps": 0.5,
        "sustain": 0.8,
        # Soft-only extras
        "dup_penalty_group": 0.2,
        "dup_penalty_global": 0.05,
        "diversity_reward": 0.03,
        "synergy": 0.05,
    },
    "gank": {
        # Gank: burst DPS, stability for engage, mobility
        "quickness": 1.0,
        "alacrity": 0.5,
        "stability": 0.9,
        "resistance": 0.7,
        "protection": 0.6,
        "might": 0.85,
        "fury": 0.85,
        "dps": 0.95,
        "sustain": 0.6,
        # Soft-only extras
        "dup_penalty_group": 0.25,
        "dup_penalty_global": 0.07,
        "diversity_reward": 0.05,
        "synergy": 0.06,
    },
}

PRESET_TARGETS: Dict[str, Dict[str, float]] = {
    "zerg": {
        "quickness_uptime": 0.95,
        "alacrity_uptime": 0.7,
        "resistance_uptime": 0.85,
        "protection_uptime": 0.7,
        "stability_sources": 3,
        "might_stacks": 20,
        "fury_uptime": 0.8,
    },
    "havoc": {
        "quickness_uptime": 0.9,
        "alacrity_uptime": 0.6,
        "resistance_uptime": 0.8,
        "protection_uptime": 0.65,
        "stability_sources": 2,
        "might_stacks": 18,
        "fury_uptime": 0.75,
    },
    "roaming": {
        "quickness_uptime": 0.5,
        "alacrity_uptime": 0.3,
        "resistance_uptime": 0.6,
        "protection_uptime": 0.5,
        "stability_sources": 1,
        "might_stacks": 15,
        "fury_uptime": 0.7,
    },
    "defense": {
        "quickness_uptime": 0.9,
        "alacrity_uptime": 0.6,
        "resistance_uptime": 0.85,
        "protection_uptime": 0.85,
        "stability_sources": 3,
        "might_stacks": 18,
        "fury_uptime": 0.7,
    },
    "gank": {
        "quickness_uptime": 0.95,
        "alacrity_uptime": 0.5,
        "resistance_uptime": 0.7,
        "protection_uptime": 0.6,
        "stability_sources": 2,
        "might_stacks": 20,
        "fury_uptime": 0.85,
    },
}


def get_preset_weights(mode: str) -> Dict[str, float]:
    """Get preset weights for a WvW mode."""
    return PRESET_WEIGHTS.get(mode.lower(), PRESET_WEIGHTS["zerg"]).copy()


def get_preset_targets(mode: str) -> Dict[str, float]:
    """Get preset targets for a WvW mode."""
    return PRESET_TARGETS.get(mode.lower(), PRESET_TARGETS["zerg"]).copy()
