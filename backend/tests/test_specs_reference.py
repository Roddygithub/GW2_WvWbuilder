"""
Tests for specs_reference module - Elite vs Core specializations.
"""

import pytest
from app.core.kb.specs_reference import (
    get_all_elite_specs,
    get_all_core_specs,
    is_elite_spec,
    get_profession_for_spec,
    get_expansion_for_elite,
    get_specs_by_profession,
    get_wvw_meta_specs,
    TOTAL_ELITE_SPECS,
    TOTAL_CORE_SPECS,
)


def test_total_specs_count():
    """Test that we have the correct total number of specializations."""
    elite_specs = get_all_elite_specs()
    core_specs = get_all_core_specs()

    assert len(elite_specs) == TOTAL_ELITE_SPECS  # 27 elite specs (9 profs × 3)
    assert len(core_specs) == TOTAL_CORE_SPECS  # 45 core specs (9 profs × 5)


def test_is_elite_spec():
    """Test is_elite_spec correctly identifies elite vs core."""
    # Elite specs
    assert is_elite_spec("Firebrand") is True
    assert is_elite_spec("Scrapper") is True
    assert is_elite_spec("Herald") is True
    assert is_elite_spec("Tempest") is True
    assert is_elite_spec("Scourge") is True

    # Core specs
    assert is_elite_spec("Radiance") is False
    assert is_elite_spec("Valor") is False
    assert is_elite_spec("Strength") is False

    # Non-existent spec
    assert is_elite_spec("FakeSpec") is False


def test_get_profession_for_spec():
    """Test profession lookup for specializations."""
    # Elite specs
    assert get_profession_for_spec("Firebrand") == "Guardian"
    assert get_profession_for_spec("Scrapper") == "Engineer"
    assert get_profession_for_spec("Herald") == "Revenant"
    assert get_profession_for_spec("Tempest") == "Elementalist"
    assert get_profession_for_spec("Scourge") == "Necromancer"

    # Core specs
    assert get_profession_for_spec("Radiance") == "Guardian"
    assert get_profession_for_spec("Strength") == "Warrior"
    assert get_profession_for_spec("Fire") == "Elementalist"

    # Case insensitive
    assert get_profession_for_spec("firebrand") == "Guardian"
    assert get_profession_for_spec("SCRAPPER") == "Engineer"


def test_get_expansion_for_elite():
    """Test expansion identification for elite specs."""
    # Heart of Thorns (HoT)
    assert get_expansion_for_elite("Dragonhunter") == "HoT"
    assert get_expansion_for_elite("Berserker") == "HoT"
    assert get_expansion_for_elite("Scrapper") == "HoT"
    assert get_expansion_for_elite("Herald") == "HoT"
    assert get_expansion_for_elite("Tempest") == "HoT"
    assert get_expansion_for_elite("Reaper") == "HoT"

    # Path of Fire (PoF)
    assert get_expansion_for_elite("Firebrand") == "PoF"
    assert get_expansion_for_elite("Spellbreaker") == "PoF"
    assert get_expansion_for_elite("Holosmith") == "PoF"
    assert get_expansion_for_elite("Weaver") == "PoF"
    assert get_expansion_for_elite("Scourge") == "PoF"

    # End of Dragons (EoD)
    assert get_expansion_for_elite("Willbender") == "EoD"
    assert get_expansion_for_elite("Bladesworn") == "EoD"
    assert get_expansion_for_elite("Mechanist") == "EoD"
    assert get_expansion_for_elite("Vindicator") == "EoD"

    # Core spec (no expansion)
    assert get_expansion_for_elite("Radiance") == ""


def test_get_specs_by_profession():
    """Test getting all specs for a profession."""
    # Guardian - all specs (5 core + 3 elite)
    guardian_all = get_specs_by_profession("Guardian")
    assert len(guardian_all) == 8
    assert "Radiance" in guardian_all
    assert "Firebrand" in guardian_all
    assert "Dragonhunter" in guardian_all
    assert "Willbender" in guardian_all

    # Guardian - elite only
    guardian_elite = get_specs_by_profession("Guardian", include_core=False)
    assert len(guardian_elite) == 3
    assert "Firebrand" in guardian_elite
    assert "Radiance" not in guardian_elite

    # Guardian - core only
    guardian_core = get_specs_by_profession("Guardian", include_elite=False)
    assert len(guardian_core) == 5
    assert "Radiance" in guardian_core
    assert "Firebrand" not in guardian_core


def test_wvw_meta_specs():
    """Test WvW meta specializations list."""
    meta_all = get_wvw_meta_specs()
    meta_elite = get_wvw_meta_specs(elite_only=True)

    # Meta elite specs
    assert "Firebrand" in meta_elite
    assert "Scrapper" in meta_elite
    assert "Herald" in meta_elite
    assert "Tempest" in meta_elite
    assert "Scourge" in meta_elite

    # All meta specs include elite + core
    assert len(meta_all) >= len(meta_elite)


def test_elite_specs_uniqueness():
    """Test that elite specs are unique across professions."""
    elite_specs = get_all_elite_specs()
    assert len(elite_specs) == len(set(elite_specs))  # No duplicates


def test_all_professions_have_specs():
    """Test that all 9 professions have their specializations."""
    professions = [
        "Guardian",
        "Warrior",
        "Engineer",
        "Ranger",
        "Thief",
        "Elementalist",
        "Mesmer",
        "Necromancer",
        "Revenant",
    ]

    for prof in professions:
        specs = get_specs_by_profession(prof)
        assert len(specs) == 8  # 5 core + 3 elite

        core_specs = get_specs_by_profession(prof, include_elite=False)
        assert len(core_specs) == 5

        elite_specs = get_specs_by_profession(prof, include_core=False)
        assert len(elite_specs) == 3


def test_known_wvw_specs():
    """Test that key WvW specs are properly identified."""
    wvw_specs = {
        "Firebrand": ("Guardian", "PoF", True),
        "Scrapper": ("Engineer", "HoT", True),
        "Mechanist": ("Engineer", "EoD", True),
        "Herald": ("Revenant", "HoT", True),
        "Tempest": ("Elementalist", "HoT", True),
        "Scourge": ("Necromancer", "PoF", True),
        "Reaper": ("Necromancer", "HoT", True),
        "Willbender": ("Guardian", "EoD", True),
        "Spellbreaker": ("Warrior", "PoF", True),
    }

    for spec, (prof, expansion, is_elite) in wvw_specs.items():
        assert get_profession_for_spec(spec) == prof
        assert get_expansion_for_elite(spec) == expansion
        assert is_elite_spec(spec) == is_elite


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
