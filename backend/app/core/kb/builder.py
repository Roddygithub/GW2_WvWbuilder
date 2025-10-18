from __future__ import annotations

import logging
from typing import List, Dict, Tuple, Any

from app.schemas.optimization import BuildTemplateInput
from app.core.optimizer.capabilities import compute_capability_vector
from .schemas import KnowledgeBase, BuildTemplateKB, CapabilityVector
from .store import load_kb, save_kb
from .ingest_gw2 import ingest_all
from .ingest_wiki import ingest_wiki_data

logger = logging.getLogger(__name__)


def build_kb_from_builds(
    builds: List[BuildTemplateInput], mode: str = "wvw"
) -> KnowledgeBase:
    kb_builds: List[BuildTemplateKB] = []
    for b in builds:
        vec = compute_capability_vector(b, mode)
        kb_builds.append(
            BuildTemplateKB(
                id=b.id,
                profession=b.profession,
                specialization=b.specialization,
                capability=CapabilityVector(**vec),
            )
        )
    kb = KnowledgeBase(builds=kb_builds, meta={"mode": mode, "source": "bootstrap"})
    return kb


def ensure_kb_initialized(builds: List[BuildTemplateInput], mode: str = "wvw") -> None:
    kb = load_kb()
    # Initialize only if empty
    if not kb.builds:
        new_kb = build_kb_from_builds(builds, mode)
        save_kb(new_kb)


def analyze_skill_boon_contribution(skill: Dict[str, Any]) -> Dict[str, float]:
    """Analyze a skill dict from GW2 API and extract boon contributions."""
    contrib = {}
    facts = skill.get("facts", [])
    for fact in facts:
        ftype = fact.get("type", "")
        if ftype == "Buff":
            status = fact.get("status", "").lower()
            duration = fact.get("duration", 0)
            # Map status to boon keys
            boon_map = {
                "quickness": "quickness",
                "alacrity": "alacrity",
                "stability": "stability",
                "resistance": "resistance",
                "protection": "protection",
                "might": "might",
                "fury": "fury",
            }
            for key, boon in boon_map.items():
                if key in status:
                    # Heuristic: duration in seconds → uptime contribution
                    uptime = min(1.0, duration / 10.0) if duration else 0.1
                    contrib[boon] = contrib.get(boon, 0.0) + uptime
        elif ftype == "AttributeAdjust":
            attr = fact.get("target", "").lower()
            if "might" in attr:
                stacks = fact.get("value", 1)
                contrib["might"] = contrib.get("might", 0.0) + float(stacks)
    return contrib


def analyze_trait_boon_contribution(trait: Dict[str, Any]) -> Dict[str, float]:
    """Analyze a trait dict from GW2 API and extract boon contributions."""
    contrib = {}
    facts = trait.get("facts", [])
    for fact in facts:
        ftype = fact.get("type", "")
        if ftype == "Buff":
            status = fact.get("status", "").lower()
            duration = fact.get("duration", 0)
            boon_map = {
                "quickness": "quickness",
                "alacrity": "alacrity",
                "stability": "stability",
                "resistance": "resistance",
                "protection": "protection",
                "might": "might",
                "fury": "fury",
            }
            for key, boon in boon_map.items():
                if key in status:
                    uptime = min(1.0, duration / 15.0) if duration else 0.05
                    contrib[boon] = contrib.get(boon, 0.0) + uptime
    return contrib


def build_kb_from_gw2_data(mode: str = "wvw") -> KnowledgeBase:
    """Build KB from GW2 API ingestion + wiki data."""
    logger.info("Building KB from GW2 API + wiki data...")
    gw2_data = ingest_all()
    wiki_data = ingest_wiki_data()

    # Map specializations to professions and elite status
    spec_to_prof: Dict[str, str] = {}
    spec_is_elite: Dict[str, bool] = {}
    spec_id_to_name: Dict[int, str] = {}

    for spec in gw2_data.get("specializations", []):
        spec_name = spec["name"].lower()
        spec_id = spec.get("id")
        spec_to_prof[spec_name] = spec.get("profession", "").lower()
        spec_is_elite[spec_name] = spec.get("elite", False)
        if spec_id:
            spec_id_to_name[spec_id] = spec_name

    # Aggregate skill/trait contributions per spec
    spec_contributions: Dict[str, Dict[str, float]] = {}

    for skill in gw2_data.get("skills", []):
        profs = skill.get("professions", [])
        spec_ref = skill.get("specialization")
        contrib = analyze_skill_boon_contribution(skill)
        if spec_ref and contrib:
            # Handle both ID (int) and name (str)
            if isinstance(spec_ref, int):
                key = spec_id_to_name.get(spec_ref)
                if not key:
                    continue  # Skip unknown spec ID
            else:
                key = spec_ref.lower()

            if key not in spec_contributions:
                spec_contributions[key] = {}
            for boon, val in contrib.items():
                spec_contributions[key][boon] = (
                    spec_contributions[key].get(boon, 0.0) + val
                )

    for trait in gw2_data.get("traits", []):
        spec_id = trait.get("specialization")
        contrib = analyze_trait_boon_contribution(trait)
        if spec_id and contrib:
            # Find spec name by id
            spec_obj = next(
                (
                    s
                    for s in gw2_data.get("specializations", [])
                    if s.get("id") == spec_id
                ),
                None,
            )
            if spec_obj:
                key = spec_obj["name"].lower()
                if key not in spec_contributions:
                    spec_contributions[key] = {}
                for boon, val in contrib.items():
                    spec_contributions[key][boon] = (
                        spec_contributions[key].get(boon, 0.0) + val
                    )

    # Normalize and cap contributions
    for spec, contribs in spec_contributions.items():
        for boon in contribs:
            if boon == "might":
                contribs[boon] = min(25.0, contribs[boon])
            else:
                contribs[boon] = min(1.0, contribs[boon])

    # Build BuildTemplateKB entries for known elite specs
    kb_builds: List[BuildTemplateKB] = []
    build_id = 200  # Start from 200 to avoid conflicts

    known_specs = [
        ("Guardian", "Firebrand"),
        ("Engineer", "Scrapper"),
        ("Engineer", "Mechanist"),
        ("Revenant", "Herald"),
        ("Elementalist", "Tempest"),
        ("Necromancer", "Scourge"),
        ("Guardian", "Willbender"),
        ("Warrior", "Spellbreaker"),
        ("Warrior", "Berserker"),
        ("Necromancer", "Reaper"),
        ("Elementalist", "Weaver"),
        ("Engineer", "Holosmith"),
    ]

    for prof, spec in known_specs:
        key = spec.lower()
        contrib = spec_contributions.get(key, {})
        # Merge with fallback heuristics from capabilities.py
        cap_vec = CapabilityVector(
            quickness=contrib.get("quickness", 0.0),
            alacrity=contrib.get("alacrity", 0.0),
            stability=contrib.get("stability", 0.0),
            resistance=contrib.get("resistance", 0.0),
            protection=contrib.get("protection", 0.0),
            might=contrib.get("might", 0.0),
            fury=contrib.get("fury", 0.0),
            dps=0.5,  # Default, can refine later
            sustain=0.5,
        )
        kb_builds.append(
            BuildTemplateKB(
                id=build_id,
                profession=prof,
                specialization=spec,
                is_elite=spec_is_elite.get(
                    spec.lower(), True
                ),  # Default to True for known elite specs
                capability=cap_vec,
            )
        )
        build_id += 1

    kb = KnowledgeBase(
        builds=kb_builds,
        meta={
            "mode": mode,
            "source": "gw2_api_ingestion",
            "wiki_data": wiki_data,
        },
    )

    logger.info(f"KB built with {len(kb_builds)} elite spec templates")
    return kb


def refresh_kb(mode: str = "wvw") -> None:
    """Refresh KB from GW2 API and save."""
    logger.info("Refreshing KB from GW2 API...")
    kb = build_kb_from_gw2_data(mode)
    save_kb(kb)
    logger.info("KB refresh complete")
