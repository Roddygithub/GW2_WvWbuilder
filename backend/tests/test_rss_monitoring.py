"""
Tests for RSS monitoring functionality — GW2_WvWBuilder v4.3.1

Tests the RSS feed parsing and WvW relevance filtering.
"""

import pytest
from app.ai.patch_monitor import parse_rss_feed, is_wvw_relevant


def test_is_wvw_relevant_wvw_keywords():
    """Test WvW relevance detection with WvW keywords."""
    texts = [
        "WvW Balance Update - Firebrand changes",
        "World vs World meta shifts after patch",
        "New zerg compositions in WvW",
        "Havoc squad build recommendations",
        "Commander tips for large scale battles",
    ]

    for text in texts:
        assert is_wvw_relevant(text), f"Should be WvW relevant: {text}"


def test_is_wvw_relevant_balance_keywords():
    """Test WvW relevance with balance keywords."""
    texts = [
        "Balance patch notes - October 2025",
        "Nerf to Firebrand quickness",
        "Buff to Mechanist barrier",
        "Rework of Reaper specialization",
    ]

    for text in texts:
        assert is_wvw_relevant(text), f"Should be relevant (balance): {text}"


def test_is_wvw_relevant_not_relevant():
    """Test that non-WvW content is filtered out."""
    texts = [
        "New Living World episode released",
        "Guild hall decorations added",
        "Trading Post down for maintenance",
        "Fashion Wars 2 contest",
        "Achievement points guide",
    ]

    for text in texts:
        assert not is_wvw_relevant(text), f"Should NOT be relevant: {text}"


def test_is_wvw_relevant_case_insensitive():
    """Test that detection is case-insensitive."""
    texts = [
        "WVW CHANGES",
        "wvw changes",
        "WvW Changes",
        "BALANCE PATCH",
        "balance patch",
    ]

    for text in texts:
        assert is_wvw_relevant(text), f"Should be case-insensitive: {text}"


def test_is_wvw_relevant_combined():
    """Test combined title + description scenarios."""
    # Relevant: WvW in title
    text1 = "WvW Balance Update - Details about new changes to professions"
    assert is_wvw_relevant(text1)

    # Relevant: Balance in description
    text2 = "October Update - Balance changes affecting all game modes"
    assert is_wvw_relevant(text2)

    # Not relevant: Neither WvW nor balance
    text3 = "New mount skin available - Check out the gemstore"
    assert not is_wvw_relevant(text3)


def test_parse_rss_feed_structure():
    """Test that RSS parsing returns correct structure."""
    # This is a mock test - in real scenario, you'd mock the URL fetch
    # For now, test the structure expectation

    # Expected structure of parsed items
    expected_keys = ["title", "description", "link", "pub_date"]

    # Since we can't actually fetch RSS in tests without mocking,
    # we just verify the function exists and has correct signature
    import inspect

    sig = inspect.signature(parse_rss_feed)
    assert "url" in sig.parameters


def test_parse_rss_feed_error_handling():
    """Test that RSS parsing handles errors gracefully."""
    # Try parsing an invalid URL
    result = parse_rss_feed("https://invalid-url-that-does-not-exist.com/feed.rss")

    # Should return empty list on error, not crash
    assert isinstance(result, list)
    assert len(result) == 0


def test_wvw_keywords_coverage():
    """Test coverage of important WvW terms."""
    wvw_terms = [
        "wvw",
        "world vs world",
        "mcm",
        "mists",
        "zerg",
        "havoc",
        "roaming",
        "squad",
        "commander",
        "keep",
        "tower",
        "siege",
    ]

    for term in wvw_terms:
        text = f"This post is about {term} gameplay"
        assert is_wvw_relevant(text), f"Should detect WvW term: {term}"


def test_balance_keywords_coverage():
    """Test coverage of balance-related terms."""
    balance_terms = [
        "balance",
        "patch",
        "update",
        "notes",
        "nerf",
        "buff",
        "rework",
        "changes",
    ]

    for term in balance_terms:
        text = f"This post discusses {term} to game mechanics"
        assert is_wvw_relevant(text), f"Should detect balance term: {term}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
