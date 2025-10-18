"""
Reference data for GW2 specializations (core and elite).

This module provides comprehensive mapping of all GW2 specializations,
distinguishing between core specializations and elite specializations.
"""

from typing import Dict, List, Tuple

# Elite specializations by profession (expansion-based)
ELITE_SPECS: Dict[str, List[Tuple[str, str]]] = {
    "Guardian": [
        ("Dragonhunter", "HoT"),      # Heart of Thorns
        ("Firebrand", "PoF"),         # Path of Fire
        ("Willbender", "EoD"),        # End of Dragons
    ],
    "Warrior": [
        ("Berserker", "HoT"),
        ("Spellbreaker", "PoF"),
        ("Bladesworn", "EoD"),
    ],
    "Engineer": [
        ("Scrapper", "HoT"),
        ("Holosmith", "PoF"),
        ("Mechanist", "EoD"),
    ],
    "Ranger": [
        ("Druid", "HoT"),
        ("Soulbeast", "PoF"),
        ("Untamed", "EoD"),
    ],
    "Thief": [
        ("Daredevil", "HoT"),
        ("Deadeye", "PoF"),
        ("Specter", "EoD"),
    ],
    "Elementalist": [
        ("Tempest", "HoT"),
        ("Weaver", "PoF"),
        ("Catalyst", "EoD"),
    ],
    "Mesmer": [
        ("Chronomancer", "HoT"),
        ("Mirage", "PoF"),
        ("Virtuoso", "EoD"),
    ],
    "Necromancer": [
        ("Reaper", "HoT"),
        ("Scourge", "PoF"),
        ("Harbinger", "EoD"),
    ],
    "Revenant": [
        ("Herald", "HoT"),
        ("Renegade", "PoF"),
        ("Vindicator", "EoD"),
    ],
}

# Core specializations by profession (5 per profession)
CORE_SPECS: Dict[str, List[str]] = {
    "Guardian": ["Radiance", "Valor", "Honor", "Virtues", "Zeal"],
    "Warrior": ["Strength", "Arms", "Defense", "Tactics", "Discipline"],
    "Engineer": ["Explosives", "Firearms", "Inventions", "Alchemy", "Tools"],
    "Ranger": ["Marksmanship", "Skirmishing", "Wilderness Survival", "Nature Magic", "Beastmastery"],
    "Thief": ["Deadly Arts", "Critical Strikes", "Shadow Arts", "Acrobatics", "Trickery"],
    "Elementalist": ["Fire", "Air", "Earth", "Water", "Arcane"],
    "Mesmer": ["Domination", "Dueling", "Chaos", "Inspiration", "Illusions"],
    "Necromancer": ["Spite", "Curses", "Death Magic", "Blood Magic", "Soul Reaping"],
    "Revenant": ["Corruption", "Retribution", "Salvation", "Invocation", "Devastation"],
}

# WvW meta specs (most commonly used in WvW)
WVW_META_SPECS: Dict[str, List[str]] = {
    "elite": [
        "Firebrand",      # Guardian - Top tier support
        "Scrapper",       # Engineer - Top tier support
        "Mechanist",      # Engineer - DPS/Support
        "Herald",         # Revenant - Support/DPS
        "Tempest",        # Elementalist - Healing/Auras
        "Scourge",        # Necromancer - Conditions/Barrier
        "Reaper",         # Necromancer - Power DPS
        "Willbender",     # Guardian - DPS/Mobility
        "Spellbreaker",   # Warrior - Boon Strip
        "Berserker",      # Warrior - Power DPS
        "Weaver",         # Elementalist - Power DPS
        "Holosmith",      # Engineer - Power DPS/Burst
        "Vindicator",     # Revenant - Hybrid DPS
    ],
    "core": [
        # Core builds are less common in organized WvW but can be viable in roaming
        "Guardian",       # Power DPS (core guardian)
        "Warrior",        # Power DPS/Banner support (core warrior)
    ],
}


def get_all_elite_specs() -> List[str]:
    """Get list of all elite specialization names."""
    specs = []
    for prof_specs in ELITE_SPECS.values():
        specs.extend([spec for spec, _ in prof_specs])
    return sorted(specs)


def get_all_core_specs() -> List[str]:
    """Get list of all core specialization names."""
    specs = []
    for prof_specs in CORE_SPECS.values():
        specs.extend(prof_specs)
    return sorted(specs)


def is_elite_spec(spec_name: str) -> bool:
    """Check if a specialization is elite (True) or core (False)."""
    all_elite = get_all_elite_specs()
    return spec_name in all_elite


def get_profession_for_spec(spec_name: str) -> str:
    """Get the profession for a given specialization name."""
    # Check elite specs
    for prof, specs in ELITE_SPECS.items():
        for spec, _ in specs:
            if spec.lower() == spec_name.lower():
                return prof
    
    # Check core specs
    for prof, specs in CORE_SPECS.items():
        for spec in specs:
            if spec.lower() == spec_name.lower():
                return prof
    
    return ""


def get_expansion_for_elite(spec_name: str) -> str:
    """Get the expansion that introduced an elite spec."""
    for prof, specs in ELITE_SPECS.items():
        for spec, expansion in specs:
            if spec.lower() == spec_name.lower():
                return expansion
    return ""


def get_specs_by_profession(profession: str, include_core: bool = True, include_elite: bool = True) -> List[str]:
    """Get all specializations for a profession."""
    specs = []
    
    if include_core and profession in CORE_SPECS:
        specs.extend(CORE_SPECS[profession])
    
    if include_elite and profession in ELITE_SPECS:
        specs.extend([spec for spec, _ in ELITE_SPECS[profession]])
    
    return specs


def get_wvw_meta_specs(elite_only: bool = False) -> List[str]:
    """Get list of WvW meta specializations."""
    if elite_only:
        return WVW_META_SPECS["elite"]
    return WVW_META_SPECS["elite"] + WVW_META_SPECS["core"]


# Statistics
TOTAL_PROFESSIONS = 9
TOTAL_CORE_SPECS_PER_PROF = 5
TOTAL_ELITE_SPECS_PER_PROF = 3
TOTAL_CORE_SPECS = TOTAL_PROFESSIONS * TOTAL_CORE_SPECS_PER_PROF  # 45
TOTAL_ELITE_SPECS = TOTAL_PROFESSIONS * TOTAL_ELITE_SPECS_PER_PROF  # 27
TOTAL_SPECS = TOTAL_CORE_SPECS + TOTAL_ELITE_SPECS  # 72
