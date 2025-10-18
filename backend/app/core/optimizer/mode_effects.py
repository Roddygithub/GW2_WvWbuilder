"""
Mode-specific effects mapping for traits, skills, and buffs.

In GW2, some traits and skills have different effects in WvW vs PvE.
This module maps these differences to ensure correct optimization.

Note: GW2 API does not expose split balances. This data is maintained
manually from community documentation (MetaBattle, GW2Wiki, Snowcrows).
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class EffectMapping:
    """Mapping of an effect in different game modes."""

    trait_id: int
    trait_name: str
    wvw_effect: Dict[str, Any]
    pve_effect: Dict[str, Any]
    description: str


def load_split_balance_data() -> Dict[str, Any]:
    """Load WvW/PvE split balance data from JSON file."""
    data_file = (
        Path(__file__).parent.parent.parent / "data" / "wvw_pve_split_balance.json"
    )

    if data_file.exists():
        with open(data_file, "r") as f:
            return json.load(f)

    return {"traits": {}, "skills": {}}


# Load split balance data
SPLIT_BALANCE_DATA = load_split_balance_data()


# Convert to EffectMapping format for backward compatibility
MODE_SPECIFIC_EFFECTS = [
    # Herald - Glint's Boon Duration
    EffectMapping(
        trait_id=1806,
        trait_name="Glint's Boon Duration",
        wvw_effect={
            "boon": "quickness",
            "duration_increase": 0.20,  # 20% en McM
            "uptime_contribution": 0.15,
        },
        pve_effect={
            "boon": "alacrity",
            "duration_increase": 0.33,  # 33% en PvE
            "uptime_contribution": 0.25,
        },
        description="Donne Quickness en McM, Alacrity en PvE",
    ),
    # Scrapper - Applied Force
    EffectMapping(
        trait_id=1917,
        trait_name="Applied Force",
        wvw_effect={
            "boon": "stability",
            "stacks": 3,
            "duration": 4,
            "uptime_contribution": 0.20,
        },
        pve_effect={
            "boon": "quickness",
            "duration": 3,
            "uptime_contribution": 0.30,
        },
        description="Donne Stability en McM, Quickness en PvE",
    ),
    # Firebrand - Liberator's Vow
    EffectMapping(
        trait_id=2075,
        trait_name="Liberator's Vow",
        wvw_effect={
            "boon": "resistance",
            "duration": 3,
            "uptime_contribution": 0.25,
        },
        pve_effect={
            "boon": "quickness",
            "duration": 2,
            "uptime_contribution": 0.20,
        },
        description="Donne Resistance en McM, Quickness en PvE",
    ),
    # Mechanist - Mech Frame: Channeling Conduits
    EffectMapping(
        trait_id=2276,
        trait_name="Mech Frame: Channeling Conduits",
        wvw_effect={
            "boon": "might",
            "stacks": 5,
            "duration": 10,
            "uptime_contribution": 0.30,
        },
        pve_effect={
            "boon": "alacrity",
            "duration": 3,
            "uptime_contribution": 0.40,
        },
        description="Donne Might en McM, Alacrity en PvE",
    ),
    # Tempest - Harmonious Conduit
    EffectMapping(
        trait_id=1952,
        trait_name="Harmonious Conduit",
        wvw_effect={
            "boon": "protection",
            "duration": 4,
            "uptime_contribution": 0.20,
        },
        pve_effect={
            "boon": "alacrity",
            "duration": 2,
            "uptime_contribution": 0.15,
        },
        description="Donne Protection en McM, Alacrity en PvE",
    ),
]


class ModeEffectsManager:
    """Manager for mode-specific effects."""

    def __init__(self, game_type: str):
        """
        Initialize with game type.

        Args:
            game_type: "wvw" or "pve"
        """
        self.game_type = game_type
        self._effects_map = {
            effect.trait_id: effect for effect in MODE_SPECIFIC_EFFECTS
        }

    def get_effect(self, trait_id: int) -> Dict[str, Any]:
        """
        Get the effect for a trait in the current game mode.

        Args:
            trait_id: Trait ID

        Returns:
            Effect dictionary for the current mode
        """
        if trait_id not in self._effects_map:
            return {}

        effect_mapping = self._effects_map[trait_id]

        if self.game_type == "wvw":
            return effect_mapping.wvw_effect
        else:
            return effect_mapping.pve_effect

    def get_boon_contribution(self, trait_id: int, boon_name: str) -> float:
        """
        Get the contribution of a trait to a specific boon in the current mode.

        Args:
            trait_id: Trait ID
            boon_name: Boon name (e.g., "quickness", "alacrity")

        Returns:
            Uptime contribution (0.0 to 1.0)
        """
        effect = self.get_effect(trait_id)

        if not effect:
            return 0.0

        if effect.get("boon") == boon_name:
            return effect.get("uptime_contribution", 0.0)

        return 0.0

    def get_all_boon_sources(self, boon_name: str) -> List[Dict[str, Any]]:
        """
        Get all traits that provide a specific boon in the current mode.

        Args:
            boon_name: Boon name

        Returns:
            List of trait effects that provide this boon
        """
        sources = []

        for trait_id, effect_mapping in self._effects_map.items():
            effect = self.get_effect(trait_id)

            if effect.get("boon") == boon_name:
                sources.append(
                    {
                        "trait_id": trait_id,
                        "trait_name": effect_mapping.trait_name,
                        "contribution": effect.get("uptime_contribution", 0.0),
                        "effect": effect,
                    }
                )

        return sources

    def get_mode_differences(self) -> List[Dict[str, Any]]:
        """
        Get all traits that have different effects between modes.

        Returns:
            List of trait differences
        """
        differences = []

        for effect_mapping in MODE_SPECIFIC_EFFECTS:
            differences.append(
                {
                    "trait_id": effect_mapping.trait_id,
                    "trait_name": effect_mapping.trait_name,
                    "wvw_boon": effect_mapping.wvw_effect.get("boon"),
                    "pve_boon": effect_mapping.pve_effect.get("boon"),
                    "description": effect_mapping.description,
                }
            )

        return differences


def get_profession_mode_adjustments(
    profession_id: int, game_type: str
) -> Dict[str, float]:
    """
    Get profession-specific adjustments for a game mode.

    Some professions are stronger in certain modes due to trait differences.

    Args:
        profession_id: Profession ID
        game_type: "wvw" or "pve"

    Returns:
        Adjustment multipliers for capabilities
    """
    adjustments = {
        # Guardian (1) - Stronger in PvE for quickness
        1: {
            "wvw": {"boon_uptime": 1.0, "healing": 1.1, "damage": 0.9},
            "pve": {"boon_uptime": 1.2, "healing": 1.0, "damage": 1.0},
        },
        # Revenant (2) - Herald stronger in PvE for alacrity
        2: {
            "wvw": {"boon_uptime": 1.1, "damage": 1.0, "survivability": 1.0},
            "pve": {"boon_uptime": 1.3, "damage": 1.1, "survivability": 0.9},
        },
        # Engineer (6) - Mechanist stronger in PvE for alacrity
        6: {
            "wvw": {"boon_uptime": 0.9, "damage": 1.0, "healing": 0.9},
            "pve": {"boon_uptime": 1.4, "damage": 1.1, "healing": 1.0},
        },
        # Elementalist (5) - Tempest different boon focus
        5: {
            "wvw": {"boon_uptime": 1.0, "healing": 1.2, "damage": 0.9},
            "pve": {"boon_uptime": 1.1, "healing": 1.0, "damage": 1.0},
        },
    }

    if profession_id not in adjustments:
        return {"boon_uptime": 1.0, "healing": 1.0, "damage": 1.0, "survivability": 1.0}

    return adjustments[profession_id].get(game_type, {})


def apply_mode_adjustments(
    capabilities: Dict[str, float], profession_id: int, game_type: str
) -> Dict[str, float]:
    """
    Apply mode-specific adjustments to build capabilities.

    Args:
        capabilities: Base capabilities
        profession_id: Profession ID
        game_type: "wvw" or "pve"

    Returns:
        Adjusted capabilities
    """
    adjustments = get_profession_mode_adjustments(profession_id, game_type)
    adjusted = capabilities.copy()

    for key, multiplier in adjustments.items():
        if key in adjusted:
            adjusted[key] *= multiplier

    return adjusted


def get_trait_split_data(trait_id: int, game_type: str = "wvw") -> Dict[str, Any]:
    """
    Get WvW/PvE split balance data for a specific trait.

    Args:
        trait_id: Trait ID
        game_type: "wvw" or "pve"

    Returns:
        Dict with trait effects for the specified mode
    """
    trait_str = str(trait_id)
    trait_data = SPLIT_BALANCE_DATA.get("traits", {}).get(trait_str, {})

    if not trait_data:
        return {}

    return trait_data.get(game_type, {})


def get_skill_split_data(skill_id: int, game_type: str = "wvw") -> Dict[str, Any]:
    """
    Get WvW/PvE split balance data for a specific skill.

    Args:
        skill_id: Skill ID
        game_type: "wvw" or "pve"

    Returns:
        Dict with skill effects for the specified mode
    """
    skill_str = str(skill_id)
    skill_data = SPLIT_BALANCE_DATA.get("skills", {}).get(skill_str, {})

    if not skill_data:
        return {}

    return skill_data.get(game_type, {})


def get_all_split_traits() -> List[str]:
    """Get list of all trait IDs that have split balances."""
    return list(SPLIT_BALANCE_DATA.get("traits", {}).keys())


def get_all_split_skills() -> List[str]:
    """Get list of all skill IDs that have split balances."""
    return list(SPLIT_BALANCE_DATA.get("skills", {}).keys())


def has_split_balance(item_id: int, item_type: str = "trait") -> bool:
    """
    Check if a trait or skill has different effects in WvW vs PvE.

    Args:
        item_id: Trait or skill ID
        item_type: "trait" or "skill"

    Returns:
        True if item has split balance
    """
    item_str = str(item_id)

    if item_type == "trait":
        return item_str in SPLIT_BALANCE_DATA.get("traits", {})
    elif item_type == "skill":
        return item_str in SPLIT_BALANCE_DATA.get("skills", {})

    return False
