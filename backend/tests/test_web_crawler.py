"""
Tests for web_crawler module - GW2 community sources crawling.
"""

import pytest
from app.core.kb.web_crawler import (
    extract_build_info,
    extract_synergies_from_crawl,
)


def test_extract_build_info_elite_specs():
    """Test extraction of elite specializations from text."""
    text = "Firebrand and Scrapper work well together in WvW. Herald provides boons."
    info = extract_build_info(text, "test")

    assert "Firebrand" in info["elite_specializations"]
    assert "Scrapper" in info["elite_specializations"]
    assert "Herald" in info["elite_specializations"]
    assert info["source"] == "test"


def test_extract_build_info_boons():
    """Test extraction of boons from text."""
    text = "This build provides quickness, stability, and resistance to the group."
    info = extract_build_info(text, "test")

    assert "quickness" in info["boons"]
    assert "stability" in info["boons"]
    assert "resistance" in info["boons"]


def test_extract_build_info_roles():
    """Test extraction of roles from text."""
    text = "Support healer with cleanse capabilities and CC for the squad."
    info = extract_build_info(text, "test")

    assert "support" in info["roles"]
    assert "healer" in info["roles"]
    assert "cleanse" in info["roles"]
    assert "cc" in info["roles"]


def test_extract_synergies_from_crawl():
    """Test synergy extraction from crawl data."""
    crawl_data = {
        "metabattle": [
            {
                "source": "metabattle",
                "synergies": [("firebrand", "scrapper"), ("herald", "tempest")],
            }
        ],
        "hardstuck": [
            {
                "source": "hardstuck",
                "synergies": [("firebrand", "scrapper"), ("scourge", "reaper")],
            }
        ],
    }

    synergies = extract_synergies_from_crawl(crawl_data)

    # Synergies should be normalized (sorted order)
    assert ("firebrand", "scrapper") in synergies or (
        "scrapper",
        "firebrand",
    ) in synergies
    assert ("herald", "tempest") in synergies or ("tempest", "herald") in synergies


def test_extract_build_info_professions():
    """Test extraction of professions from text."""
    text = "Guardian and Warrior are the backbone of any WvW squad. Engineer provides support."
    info = extract_build_info(text, "test")

    assert "Guardian" in info["professions"]
    assert "Warrior" in info["professions"]
    assert "Engineer" in info["professions"]


def test_extract_build_info_empty_text():
    """Test extraction with empty text."""
    info = extract_build_info("", "test")

    assert info["source"] == "test"
    assert len(info["professions"]) == 0
    assert len(info["specializations"]) == 0
    assert len(info["boons"]) == 0


def test_extract_build_info_mixed_content():
    """Test extraction with mixed content (elite specs + boons + roles)."""
    text = """
    Firebrand provides quickness and stability to the group.
    Scrapper offers resistance and sustain.
    This is a support composition with high dps potential.
    Herald brings might and fury to allies.
    """
    info = extract_build_info(text, "test")

    # Elite specs
    assert "Firebrand" in info["elite_specializations"]
    assert "Scrapper" in info["elite_specializations"]
    assert "Herald" in info["elite_specializations"]

    # Boons
    assert "quickness" in info["boons"]
    assert "stability" in info["boons"]
    assert "resistance" in info["boons"]
    assert "might" in info["boons"]
    assert "fury" in info["boons"]

    # Roles
    assert "support" in info["roles"]
    assert "dps" in info["roles"]
    assert "sustain" in info["roles"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
