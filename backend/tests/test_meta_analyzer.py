"""
Tests for meta_analyzer module — GW2_WvWBuilder v4.3

Tests the LLM-powered analysis of balance changes.
"""

import pytest
from app.ai.meta_analyzer import (
    fallback_heuristic_analysis,
    recalculate_synergies,
)


def test_fallback_heuristic_nerf():
    """Test heuristic analysis for nerf changes."""
    change = {
        "spec": "Firebrand",
        "change_type": "nerf",
        "impact": "Quickness reduced by 15%",
        "magnitude": "15%",
    }
    
    analysis = fallback_heuristic_analysis(change)
    
    assert analysis["spec"] == "Firebrand"
    assert analysis["change_type"] == "nerf"
    assert analysis["weight_delta"] == -0.10
    assert "nerfed" in analysis["reasoning"].lower()


def test_fallback_heuristic_buff():
    """Test heuristic analysis for buff changes."""
    change = {
        "spec": "Mechanist",
        "change_type": "buff",
        "impact": "Barrier increased by 20%",
    }
    
    analysis = fallback_heuristic_analysis(change)
    
    assert analysis["spec"] == "Mechanist"
    assert analysis["change_type"] == "buff"
    assert analysis["weight_delta"] == 0.10
    assert "buffed" in analysis["reasoning"].lower()


def test_fallback_heuristic_rework():
    """Test heuristic analysis for rework changes."""
    change = {
        "spec": "Weaver",
        "change_type": "rework",
        "impact": "Attunement system changed",
    }
    
    analysis = fallback_heuristic_analysis(change)
    
    assert analysis["spec"] == "Weaver"
    assert analysis["change_type"] == "rework"
    assert analysis["weight_delta"] == 0.0
    assert "reworked" in analysis["reasoning"].lower()


def test_recalculate_synergies_no_impact():
    """Test synergy recalculation with no high-impact changes."""
    analyses = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.05,
            "synergy_impact": "low",
        }
    ]
    
    current_synergies = {
        ("firebrand", "scrapper"): 0.95,
        ("herald", "tempest"): 0.85,
    }
    
    updated = recalculate_synergies(analyses, current_synergies, llm_engine=None)
    
    # Should remain unchanged for low impact
    assert updated == current_synergies


def test_recalculate_synergies_high_impact():
    """Test synergy recalculation with high-impact nerf."""
    analyses = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.15,
            "synergy_impact": "high",
        }
    ]
    
    current_synergies = {
        ("firebrand", "scrapper"): 0.95,
        ("firebrand", "herald"): 0.90,
        ("herald", "tempest"): 0.85,
    }
    
    updated = recalculate_synergies(analyses, current_synergies, llm_engine=None)
    
    # Firebrand synergies should be reduced
    assert updated[("firebrand", "scrapper")] < 0.95
    assert updated[("firebrand", "herald")] < 0.90
    # Unrelated synergy should remain unchanged
    assert updated[("herald", "tempest")] == 0.85


def test_analysis_structure():
    """Test that analysis has all required fields."""
    change = {
        "spec": "Scrapper",
        "change_type": "buff",
        "impact": "Resistance improved",
    }
    
    analysis = fallback_heuristic_analysis(change)
    
    required_fields = ["spec", "change_type", "weight_delta", "synergy_impact", 
                       "affected_roles", "reasoning", "source_change"]
    
    for field in required_fields:
        assert field in analysis


def test_weight_delta_bounds():
    """Test that weight delta is within reasonable bounds."""
    changes = [
        {"spec": "Test1", "change_type": "nerf"},
        {"spec": "Test2", "change_type": "buff"},
        {"spec": "Test3", "change_type": "rework"},
    ]
    
    for change in changes:
        analysis = fallback_heuristic_analysis(change)
        # Weight delta should be between -0.3 and +0.3
        assert -0.3 <= analysis["weight_delta"] <= 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
