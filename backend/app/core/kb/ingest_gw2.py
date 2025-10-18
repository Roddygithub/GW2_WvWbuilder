from __future__ import annotations

import logging
import urllib.request
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

GW2_API_BASE = "https://api.guildwars2.com/v2"


def fetch_json(url: str, timeout: int = 10) -> Optional[Any]:
    """Fetch JSON from URL with timeout and error handling."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GW2_WvWBuilder/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def fetch_professions() -> List[Dict[str, Any]]:
    """Fetch all professions from GW2 API."""
    ids = fetch_json(f"{GW2_API_BASE}/professions")
    if not ids:
        return []
    profs = []
    for pid in ids:
        data = fetch_json(f"{GW2_API_BASE}/professions/{pid}")
        if data:
            profs.append(data)
    return profs


def fetch_specializations() -> List[Dict[str, Any]]:
    """Fetch all specializations (core + elite) from GW2 API.
    
    Each specialization has:
    - id: int
    - name: str
    - profession: str
    - elite: bool (True for elite specs like Firebrand, False for core specs)
    - major_traits: List[int]
    - minor_traits: List[int]
    """
    ids = fetch_json(f"{GW2_API_BASE}/specializations")
    if not ids:
        return []
    specs = []
    for sid in ids:
        data = fetch_json(f"{GW2_API_BASE}/specializations/{sid}")
        if data:
            specs.append(data)
    logger.info(f"Fetched {len(specs)} specializations ({len([s for s in specs if s.get('elite')])} elite, {len([s for s in specs if not s.get('elite')])} core)")
    return specs


def fetch_skills(skill_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Fetch skills by IDs or all if None."""
    if skill_ids is None:
        ids = fetch_json(f"{GW2_API_BASE}/skills")
        if not ids:
            return []
        # Limit to first 500 for performance (can batch later)
        skill_ids = ids[:500]
    
    skills = []
    # Batch fetch (API supports ?ids=1,2,3...)
    batch_size = 200
    for i in range(0, len(skill_ids), batch_size):
        batch = skill_ids[i:i+batch_size]
        ids_str = ",".join(str(x) for x in batch)
        data = fetch_json(f"{GW2_API_BASE}/skills?ids={ids_str}")
        if data:
            skills.extend(data)
    return skills


def fetch_traits(trait_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Fetch traits by IDs or all if None."""
    if trait_ids is None:
        ids = fetch_json(f"{GW2_API_BASE}/traits")
        if not ids:
            return []
        trait_ids = ids[:500]
    
    traits = []
    batch_size = 200
    for i in range(0, len(trait_ids), batch_size):
        batch = trait_ids[i:i+batch_size]
        ids_str = ",".join(str(x) for x in batch)
        data = fetch_json(f"{GW2_API_BASE}/traits?ids={ids_str}")
        if data:
            traits.extend(data)
    return traits


def fetch_items_stats() -> Dict[str, Any]:
    """Fetch itemstats (stat combos like Berserker, Marauder, etc.)."""
    ids = fetch_json(f"{GW2_API_BASE}/itemstats")
    if not ids:
        return {}
    stats = {}
    for sid in ids[:50]:  # Limit to common stat combos
        data = fetch_json(f"{GW2_API_BASE}/itemstats/{sid}")
        if data:
            stats[data.get("id")] = data
    return stats


def ingest_all() -> Dict[str, Any]:
    """Ingest all GW2 data and return structured dict."""
    logger.info("Starting GW2 API ingestion...")
    
    data = {
        "professions": fetch_professions(),
        "specializations": fetch_specializations(),
        "skills": fetch_skills(),
        "traits": fetch_traits(),
        "itemstats": fetch_items_stats(),
    }
    
    logger.info(f"Ingested {len(data['professions'])} professions, "
                f"{len(data['specializations'])} specializations, "
                f"{len(data['skills'])} skills, "
                f"{len(data['traits'])} traits")
    
    return data
