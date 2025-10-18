#!/usr/bin/env python3
"""
Test script for Split Balance Database v3.6
Validates the expanded database with 41 items
"""

import sys
import json
from pathlib import Path

def test_split_balance_data():
    """Test loading and validation of split balance data"""
    
    # Load data
    data_file = Path(__file__).parent / "data" / "wvw_pve_split_balance.json"
    
    print("=" * 60)
    print("🧪 Testing Split Balance Database v3.6")
    print("=" * 60)
    
    # Test 1: File exists and is valid JSON
    print("\n1. Loading JSON file...")
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
        print("   ✅ File loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load: {e}")
        return False
    
    # Test 2: Check structure
    print("\n2. Validating structure...")
    required_keys = ["source", "last_updated", "version", "traits", "skills"]
    missing_keys = [k for k in required_keys if k not in data]
    
    if missing_keys:
        print(f"   ❌ Missing keys: {missing_keys}")
        return False
    print("   ✅ All required keys present")
    
    # Test 3: Count items
    print("\n3. Counting items...")
    traits_count = len(data["traits"])
    skills_count = len(data["skills"])
    total_count = traits_count + skills_count
    
    print(f"   Traits: {traits_count}")
    print(f"   Skills: {skills_count}")
    print(f"   Total: {total_count}")
    
    expected_traits = 20
    expected_skills = 21
    expected_total = 41
    
    if traits_count == expected_traits:
        print(f"   ✅ Traits count correct ({expected_traits})")
    else:
        print(f"   ❌ Expected {expected_traits} traits, got {traits_count}")
        return False
    
    if skills_count == expected_skills:
        print(f"   ✅ Skills count correct ({expected_skills})")
    else:
        print(f"   ❌ Expected {expected_skills} skills, got {skills_count}")
        return False
    
    # Test 4: Validate trait structure
    print("\n4. Validating trait structure...")
    errors = []
    for trait_id, trait_data in data["traits"].items():
        required_fields = ["name", "pve", "wvw"]
        missing = [f for f in required_fields if f not in trait_data]
        if missing:
            errors.append(f"Trait {trait_id} missing: {missing}")
    
    if errors:
        print(f"   ❌ Validation errors:\n      " + "\n      ".join(errors[:5]))
        return False
    print(f"   ✅ All {traits_count} traits valid")
    
    # Test 5: Validate skill structure
    print("\n5. Validating skill structure...")
    errors = []
    for skill_id, skill_data in data["skills"].items():
        required_fields = ["name", "pve", "wvw"]
        missing = [f for f in required_fields if f not in skill_data]
        if missing:
            errors.append(f"Skill {skill_id} missing: {missing}")
    
    if errors:
        print(f"   ❌ Validation errors:\n      " + "\n      ".join(errors[:5]))
        return False
    print(f"   ✅ All {skills_count} skills valid")
    
    # Test 6: Check for duplicates
    print("\n6. Checking for duplicate IDs...")
    all_ids = list(data["traits"].keys()) + list(data["skills"].keys())
    duplicates = [id for id in all_ids if all_ids.count(id) > 1]
    
    if duplicates:
        print(f"   ❌ Duplicate IDs found: {duplicates}")
        return False
    print("   ✅ No duplicate IDs")
    
    # Test 7: Check profession coverage
    print("\n7. Analyzing profession coverage...")
    professions = set()
    for trait in data["traits"].values():
        if "profession" in trait:
            professions.add(trait["profession"])
    for skill in data["skills"].values():
        if "profession" in skill:
            professions.add(skill["profession"])
    
    print(f"   Professions covered: {len(professions)}")
    print(f"   {sorted(professions)}")
    
    if len(professions) >= 8:
        print(f"   ✅ Good coverage ({len(professions)}/9 professions)")
    else:
        print(f"   ⚠️ Limited coverage ({len(professions)}/9 professions)")
    
    # Test 8: Verify expansion (v3.5 had 8 items)
    print("\n8. Verifying expansion...")
    previous_total = 8
    expansion = total_count - previous_total
    expansion_percent = (expansion / previous_total) * 100
    
    print(f"   v3.5.2: {previous_total} items")
    print(f"   v3.6.0: {total_count} items")
    print(f"   Expansion: +{expansion} items (+{expansion_percent:.0f}%)")
    
    if expansion >= 30:
        print(f"   ✅ Major expansion achieved!")
    else:
        print(f"   ❌ Expansion too small")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Version: {data.get('version', 'unknown')}")
    print(f"Last Updated: {data.get('last_updated', 'unknown')}")
    print(f"Total Items: {total_count}")
    print(f"Professions: {len(professions)}/9")
    print(f"Coverage: {data.get('coverage', {}).get('estimated_meta_coverage', 'unknown')}")
    print("\n✅ ALL TESTS PASSED!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_split_balance_data()
    sys.exit(0 if success else 1)
