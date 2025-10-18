from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Minimal wiki data for WvW-specific boon priorities and role descriptions
# In production, this could parse actual wiki pages or use cached snapshots

WIKI_BOON_PRIORITIES = {
    "zerg": ["stability", "quickness", "resistance", "protection", "might", "fury", "alacrity"],
    "havoc": ["quickness", "stability", "resistance", "might", "fury", "protection", "alacrity"],
    "roaming": ["stability", "resistance", "quickness", "might", "fury", "protection", "alacrity"],
    "defense": ["stability", "protection", "resistance", "quickness", "might", "fury", "alacrity"],
    "gank": ["stability", "quickness", "might", "fury", "resistance", "protection", "alacrity"],
}

WIKI_ROLE_DESCRIPTIONS = {
    "stability": "Prevents crowd control effects, critical for frontline engagement",
    "quickness": "Increases action speed, essential for burst damage and support",
    "resistance": "Blocks condition damage, vital against condition-heavy enemies",
    "protection": "Reduces incoming direct damage by 33%",
    "might": "Increases power and condition damage",
    "fury": "Increases critical chance by 20%",
    "alacrity": "Reduces skill cooldowns, improves sustain and utility",
    "cleanse": "Removes conditions from allies",
    "cc": "Crowd control: stuns, dazes, knockbacks",
    "range": "Long-range pressure and siege support",
    "stealth": "Invisibility for tactical positioning",
    "mobility": "Movement speed and gap closers",
}

WIKI_SPEC_NOTES = {
    "firebrand": "Core stability and quickness provider, tome heals, aegis spam",
    "scrapper": "Resistance and stability, gyro support, excellent sustain",
    "herald": "Might and fury uptime, facet sharing, good sustain",
    "tempest": "Aura sharing, cleanse, healing, resistance",
    "scourge": "Barrier support, condition pressure, boon corrupt",
    "mechanist": "Alacrity provider, barrier, ranged pressure",
    "willbender": "Burst damage, mobility, aegis",
    "spellbreaker": "Boon rip, CC, anti-support",
    "reaper": "Melee pressure, sustain, chill",
    "weaver": "Burst damage, aura sharing",
    "holosmith": "Power burst, mobility",
    "berserker": "Power DPS, CC, banner support",
}


def ingest_wiki_data() -> Dict[str, any]:
    """Return wiki-sourced WvW knowledge."""
    logger.info("Loading wiki WvW data...")
    return {
        "boon_priorities": WIKI_BOON_PRIORITIES,
        "role_descriptions": WIKI_ROLE_DESCRIPTIONS,
        "spec_notes": WIKI_SPEC_NOTES,
    }
