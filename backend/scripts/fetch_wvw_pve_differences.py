#!/usr/bin/env python3
"""
Fetch all WvW/PvE differences from GW2 API

This script queries the official GW2 API to find all traits and skills
that have different effects in WvW vs PvE modes.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any
from pathlib import Path

API_BASE = "https://api.guildwars2.com/v2"

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Any:
    """Fetch JSON from URL"""
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        return None

async def fetch_all_traits(session: aiohttp.ClientSession) -> List[Dict]:
    """Fetch all traits from GW2 API"""
    print("Fetching all trait IDs...")
    trait_ids = await fetch_json(session, f"{API_BASE}/traits")
    
    if not trait_ids:
        print("Failed to fetch trait IDs")
        return []
    
    print(f"Found {len(trait_ids)} traits. Fetching details...")
    
    # Fetch in batches of 200 (API limit)
    traits = []
    batch_size = 200
    
    for i in range(0, len(trait_ids), batch_size):
        batch = trait_ids[i:i+batch_size]
        ids_str = ",".join(map(str, batch))
        url = f"{API_BASE}/traits?ids={ids_str}"
        
        batch_traits = await fetch_json(session, url)
        if batch_traits:
            traits.extend(batch_traits)
        
        print(f"Progress: {len(traits)}/{len(trait_ids)} traits fetched")
        await asyncio.sleep(0.1)  # Rate limiting
    
    return traits

async def fetch_all_skills(session: aiohttp.ClientSession) -> List[Dict]:
    """Fetch all skills from GW2 API"""
    print("\nFetching all skill IDs...")
    skill_ids = await fetch_json(session, f"{API_BASE}/skills")
    
    if not skill_ids:
        print("Failed to fetch skill IDs")
        return []
    
    print(f"Found {len(skill_ids)} skills. Fetching details...")
    
    # Fetch in batches
    skills = []
    batch_size = 200
    
    for i in range(0, len(skill_ids), batch_size):
        batch = skill_ids[i:i+batch_size]
        ids_str = ",".join(map(str, batch))
        url = f"{API_BASE}/skills?ids={ids_str}"
        
        batch_skills = await fetch_json(session, url)
        if batch_skills:
            skills.extend(batch_skills)
        
        print(f"Progress: {len(skills)}/{len(skill_ids)} skills fetched")
        await asyncio.sleep(0.1)
    
    return skills

def has_game_mode_differences(item: Dict) -> bool:
    """
    Check if a trait/skill has different effects in PvP/WvW vs PvE
    
    GW2 API indicates this with:
    - Different facts in facts_pvp/facts_pve
    - Different attributes in attributes_pvp/attributes_pve
    - Traited facts differences
    """
    # Check for PvP-specific facts (WvW uses same as PvP)
    if "facts" in item and "facts_pvp" in item:
        return item["facts"] != item["facts_pvp"]
    
    # Check for traited facts differences
    if "traited_facts" in item and "traited_facts_pvp" in item:
        return item["traited_facts"] != item["traited_facts_pvp"]
    
    return False

def analyze_differences(item: Dict) -> Dict[str, Any]:
    """Analyze the specific differences between PvE and PvP/WvW"""
    differences = {
        "id": item["id"],
        "name": item["name"],
        "type": "trait" if "specialization" in item else "skill",
        "pve_effects": [],
        "wvw_effects": [],
    }
    
    # Compare facts
    pve_facts = item.get("facts", [])
    wvw_facts = item.get("facts_pvp", pve_facts)
    
    # Extract key effects
    for fact in pve_facts:
        if fact.get("type") in ["Buff", "AttributeAdjust", "Damage", "Number", "Duration"]:
            differences["pve_effects"].append({
                "type": fact.get("type"),
                "text": fact.get("text", ""),
                "value": fact.get("value") or fact.get("percent"),
                "status": fact.get("status"),
            })
    
    for fact in wvw_facts:
        if fact.get("type") in ["Buff", "AttributeAdjust", "Damage", "Number", "Duration"]:
            differences["wvw_effects"].append({
                "type": fact.get("type"),
                "text": fact.get("text", ""),
                "value": fact.get("value") or fact.get("percent"),
                "status": fact.get("status"),
            })
    
    return differences

async def main():
    """Main function to fetch and analyze GW2 mode differences"""
    print("=" * 60)
    print("GW2 WvW/PvE Differences Analyzer")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Fetch all traits
        traits = await fetch_all_traits(session)
        
        # Fetch all skills
        skills = await fetch_all_skills(session)
        
        print("\n" + "=" * 60)
        print("Analyzing differences...")
        print("=" * 60)
        
        # Find traits with differences
        trait_differences = []
        for trait in traits:
            if has_game_mode_differences(trait):
                diff = analyze_differences(trait)
                trait_differences.append(diff)
        
        # Find skills with differences
        skill_differences = []
        for skill in skills:
            if has_game_mode_differences(skill):
                diff = analyze_differences(skill)
                skill_differences.append(diff)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  Total traits analyzed: {len(traits)}")
        print(f"  Traits with WvW/PvE differences: {len(trait_differences)}")
        print(f"  Total skills analyzed: {len(skills)}")
        print(f"  Skills with WvW/PvE differences: {len(skill_differences)}")
        
        # Show examples
        print(f"\n🔍 Examples of differences found:\n")
        
        for i, diff in enumerate(trait_differences[:10], 1):
            print(f"{i}. {diff['name']} (Trait ID: {diff['id']})")
            if diff['pve_effects'] and diff['wvw_effects']:
                pve = diff['pve_effects'][0]
                wvw = diff['wvw_effects'][0]
                print(f"   PvE: {pve.get('text', 'N/A')} = {pve.get('value', 'N/A')}")
                print(f"   WvW: {wvw.get('text', 'N/A')} = {wvw.get('value', 'N/A')}")
            print()
        
        # Save to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "gw2_mode_differences.json"
        
        data = {
            "generated_at": "2025-10-17",
            "source": "GW2 API v2",
            "stats": {
                "total_traits": len(traits),
                "traits_with_differences": len(trait_differences),
                "total_skills": len(skills),
                "skills_with_differences": len(skill_differences),
            },
            "trait_differences": trait_differences,
            "skill_differences": skill_differences,
        }
        
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Data saved to: {output_file}")
        print(f"\n📄 Use this file in the optimizer to get accurate mode-specific effects!")

if __name__ == "__main__":
    asyncio.run(main())
