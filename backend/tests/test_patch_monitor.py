"""
Tests for patch_monitor module — GW2_WvWBuilder v4.3

Tests the automatic patch note monitoring and change detection system.
"""

import pytest
from app.ai.patch_monitor import extract_patch_changes, filter_recent_changes
from datetime import datetime, timedelta


def test_extract_nerf_changes():
    """Test detection of nerf keywords."""
    text = """
    Firebrand: Quickness duration reduced by 15% on tome skills.
    This change aims to balance the support role in WvW.
    """
    
    changes = extract_patch_changes(text, "test")
    
    assert len(changes) > 0
    firebrand_changes = [c for c in changes if c["spec"] == "Firebrand"]
    assert len(firebrand_changes) > 0
    assert firebrand_changes[0]["change_type"] == "nerf"
    assert "15%" in text.lower()


def test_extract_buff_changes():
    """Test detection of buff keywords."""
    text = """
    Mechanist: Barrier generation increased by 20%.
    Engineers rejoice as their support build gets stronger.
    """
    
    changes = extract_patch_changes(text, "test")
    
    mechanist_changes = [c for c in changes if c["spec"] == "Mechanist"]
    assert len(mechanist_changes) > 0
    assert mechanist_changes[0]["change_type"] == "buff"


def test_extract_rework_changes():
    """Test detection of rework keywords."""
    text = """
    Weaver: Elemental attunement system has been reworked.
    This is a major change to how the spec plays.
    """
    
    changes = extract_patch_changes(text, "test")
    
    weaver_changes = [c for c in changes if c["spec"] == "Weaver"]
    assert len(weaver_changes) > 0
    assert weaver_changes[0]["change_type"] == "rework"


def test_extract_magnitude():
    """Test extraction of change magnitude."""
    text = "Scrapper: Resistance duration reduced by 25% in WvW."
    
    changes = extract_patch_changes(text, "test")
    
    scrapper_changes = [c for c in changes if c["spec"] == "Scrapper"]
    assert len(scrapper_changes) > 0
    assert scrapper_changes[0]["magnitude"] == "25%"


def test_no_changes_detected():
    """Test that non-balance text doesn't trigger false positives."""
    text = """
    New map: Obsidian Sanctum has been updated with new textures.
    Bug fix: Fixed a rendering issue with Mesmer clones.
    """
    
    changes = extract_patch_changes(text, "test")
    
    # Should not detect any balance changes
    assert len(changes) == 0


def test_filter_recent_changes():
    """Test filtering of changes by date."""
    now = datetime.now()
    
    changes = [
        {"date": now.isoformat()[:10], "spec": "Firebrand", "change_type": "nerf"},
        {"date": (now - timedelta(days=5)).isoformat()[:10], "spec": "Scrapper", "change_type": "buff"},
        {"date": (now - timedelta(days=40)).isoformat()[:10], "spec": "Herald", "change_type": "rework"},
    ]
    
    recent = filter_recent_changes(changes, days=30)
    
    assert len(recent) == 2
    assert all(c["spec"] in ["Firebrand", "Scrapper"] for c in recent)


def test_multiple_specs_in_text():
    """Test detection of multiple specs in single text."""
    text = """
    Balance Update October 2025:
    - Firebrand: Quickness reduced by 10%
    - Scrapper: Resistance improved by 15%
    - Herald: Fury generation buffed
    """
    
    changes = extract_patch_changes(text, "test")
    
    specs_found = {c["spec"] for c in changes}
    assert "Firebrand" in specs_found
    assert "Scrapper" in specs_found
    assert "Herald" in specs_found


def test_change_context_extraction():
    """Test that impact text is extracted."""
    text = "Tempest: Aura duration decreased by 2 seconds in all game modes."
    
    changes = extract_patch_changes(text, "test")
    
    tempest_changes = [c for c in changes if c["spec"] == "Tempest"]
    assert len(tempest_changes) > 0
    assert "aura" in tempest_changes[0]["impact"].lower()
    assert "decreased" in tempest_changes[0]["impact"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
