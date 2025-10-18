#!/usr/bin/env python3
"""
Diagnostic script to verify WvW filtering in web crawler.

This script tests the WvW detection and filtering mechanism to ensure
that only WvW-relevant content is processed by the LLM.
"""

from web_crawler import extract_build_info


def test_wvw_detection():
    """Test WvW vs PvE detection."""

    test_cases = [
        {
            "name": "WvW zerg text",
            "text": "This Firebrand build is perfect for WvW zerg play. Provides stability and quickness to the squad.",
            "expected_is_wvw": True,
        },
        {
            "name": "PvE raid text",
            "text": "This Firebrand build is optimized for raids. High DPS on golem benchmark with excellent burst damage for boss encounters.",
            "expected_is_wvw": False,
        },
        {
            "name": "PvE fractal text",
            "text": "Great for challenge mote fractals. Works well in 5-man instanced content with high CC and burst.",
            "expected_is_wvw": False,
        },
        {
            "name": "WvW roaming text",
            "text": "Excellent roaming build for solo WvW play. Good dueling potential with strong sustain.",
            "expected_is_wvw": True,
        },
        {
            "name": "WvW havoc text",
            "text": "Perfect for havoc squad. Provides boon strip and corruption for enemy zergs.",
            "expected_is_wvw": True,
        },
        {
            "name": "Mixed content (WvW dominant)",
            "text": "This Scrapper build works in WvW and PvE. Best for zerg fights in mists. Can also do fractals.",
            "expected_is_wvw": True,  # WvW score should be higher
        },
        {
            "name": "Mixed content (PvE dominant)",
            "text": "Optimized for raids and fractals. Can work in WvW but not recommended for serious play.",
            "expected_is_wvw": False,  # PvE keywords dominate
        },
    ]

    print("=" * 70)
    print("WvW Detection Diagnostic")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for test in test_cases:
        info = extract_build_info(test["text"], "test")
        is_wvw = info["is_wvw"]
        wvw_score = info["wvw_score"]
        expected = test["expected_is_wvw"]

        status = "✅ PASS" if is_wvw == expected else "❌ FAIL"
        if is_wvw == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} {test['name']}")
        print(f"  Text: {test['text'][:60]}...")
        print(f"  Expected WvW: {expected}")
        print(f"  Detected WvW: {is_wvw}")
        print(f"  WvW Score: {wvw_score:.1f}")
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    import sys

    success = test_wvw_detection()
    sys.exit(0 if success else 1)
