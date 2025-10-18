"""
Tests for meta_weights_updater module — GW2_WvWBuilder v4.3

Tests the dynamic weight management system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from app.ai.meta_weights_updater import MetaWeightsUpdater


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def updater(temp_data_dir):
    """Create a MetaWeightsUpdater with temporary directory."""
    return MetaWeightsUpdater(data_dir=temp_data_dir)


def test_initial_weights(updater):
    """Test that initial weights are all 1.0."""
    weights = updater.get_weights()

    assert len(weights) > 0
    assert all(weight == 1.0 for weight in weights.values())


def test_get_weight(updater):
    """Test getting weight for a specific spec."""
    weight = updater.get_weight("firebrand")

    assert weight == 1.0


def test_apply_weight_adjustment(updater):
    """Test applying a weight adjustment."""
    analyses = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.15,
            "reasoning": "Test nerf",
        }
    ]

    updated_weights = updater.apply_weight_adjustments(analyses)

    assert updated_weights["firebrand"] == 0.85
    assert len(updater.get_history()) == 1


def test_weight_clamping_lower(updater):
    """Test that weights are clamped to minimum 0.1."""
    analyses = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -1.5,  # Would result in negative
            "reasoning": "Extreme nerf",
        }
    ]

    updated_weights = updater.apply_weight_adjustments(analyses)

    assert updated_weights["firebrand"] >= 0.1


def test_weight_clamping_upper(updater):
    """Test that weights are clamped to maximum 2.0."""
    analyses = [
        {
            "spec": "Mechanist",
            "change_type": "buff",
            "weight_delta": 2.5,  # Would result in > 2.0
            "reasoning": "Extreme buff",
        }
    ]

    updated_weights = updater.apply_weight_adjustments(analyses)

    assert updated_weights["mechanist"] <= 2.0


def test_multiple_adjustments(updater):
    """Test applying multiple adjustments in sequence."""
    # First adjustment
    analyses1 = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.10,
            "reasoning": "First nerf",
        }
    ]
    updater.apply_weight_adjustments(analyses1)

    # Second adjustment
    analyses2 = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.05,
            "reasoning": "Second nerf",
        }
    ]
    updater.apply_weight_adjustments(analyses2)

    # Should be 1.0 - 0.10 - 0.05 = 0.85
    assert updater.get_weight("firebrand") == 0.85
    assert len(updater.get_history()) == 2


def test_history_tracking(updater):
    """Test that history is properly tracked."""
    analyses = [
        {
            "spec": "Scrapper",
            "change_type": "buff",
            "weight_delta": 0.10,
            "reasoning": "Test buff",
        }
    ]

    updater.apply_weight_adjustments(analyses)
    history = updater.get_history()

    assert len(history) == 1
    entry = history[0]
    assert "timestamp" in entry
    assert "adjustments" in entry
    assert len(entry["adjustments"]) == 1
    assert entry["adjustments"][0]["spec"] == "scrapper"
    assert entry["adjustments"][0]["delta"] == 0.10


def test_reset_to_defaults(updater):
    """Test resetting all weights to 1.0."""
    # Apply some adjustments
    analyses = [
        {
            "spec": "Firebrand",
            "change_type": "nerf",
            "weight_delta": -0.15,
            "reasoning": "Test",
        },
        {
            "spec": "Scrapper",
            "change_type": "buff",
            "weight_delta": 0.10,
            "reasoning": "Test",
        },
    ]
    updater.apply_weight_adjustments(analyses)

    # Reset
    updater.reset_to_defaults()

    weights = updater.get_weights()
    assert all(weight == 1.0 for weight in weights.values())
    assert len(updater.get_history()) > 1  # Should have reset entry


def test_synergy_updates(updater):
    """Test applying synergy updates."""
    synergies = {
        ("firebrand", "scrapper"): 0.90,
        ("herald", "tempest"): 0.85,
    }

    updater.apply_synergy_updates(synergies)

    assert updater.get_synergy("firebrand", "scrapper") == 0.90
    assert updater.get_synergy("herald", "tempest") == 0.85


def test_get_synergy_normalized(updater):
    """Test that get_synergy normalizes spec order."""
    synergies = {
        ("firebrand", "scrapper"): 0.95,
    }
    updater.apply_synergy_updates(synergies)

    # Should work regardless of order
    assert updater.get_synergy("firebrand", "scrapper") == 0.95
    assert updater.get_synergy("scrapper", "firebrand") == 0.95


def test_persistence(temp_data_dir):
    """Test that data is persisted across instances."""
    # First instance
    updater1 = MetaWeightsUpdater(data_dir=temp_data_dir)
    analyses = [
        {
            "spec": "Reaper",
            "change_type": "rework",
            "weight_delta": -0.15,
            "reasoning": "Test",
        },
    ]
    updater1.apply_weight_adjustments(analyses)

    # Second instance should load the same data
    updater2 = MetaWeightsUpdater(data_dir=temp_data_dir)

    assert updater2.get_weight("reaper") == 0.85
    assert len(updater2.get_history()) == 1


def test_history_limit(updater):
    """Test that history can be limited."""
    # Create multiple entries
    specs = [
        "firebrand",
        "scrapper",
        "herald",
        "tempest",
        "scourge",
        "mechanist",
        "reaper",
        "weaver",
        "holosmith",
        "berserker",
    ]

    for i, spec in enumerate(specs):
        analyses = [
            {
                "spec": spec,
                "change_type": "nerf",
                "weight_delta": -0.05,
                "reasoning": f"Test {i}",
            },
        ]
        updater.apply_weight_adjustments(analyses)

    # Get limited history
    limited = updater.get_history(limit=5)

    assert len(limited) == 5
    # Should get the most recent ones (last spec was berserker, at end of list)
    assert "berserker" in str(limited[-1])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
