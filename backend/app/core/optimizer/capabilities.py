from __future__ import annotations

from typing import Dict, Any

from app.core.optimizer.mode_effects import SPLIT_BALANCE_DATA
from app.core.kb.store import get_capability_from_kb
from app.schemas.optimization import BuildTemplateInput


BOON_KEYS = [
    "quickness",
    "alacrity",
    "stability",
    "resistance",
    "protection",
    "might",
    "fury",
]


def _normalize(result: Dict[str, float]) -> Dict[str, float]:
    # cap into [0,1], might capped separately later by solver
    out: Dict[str, float] = {}
    for k, v in result.items():
        if k == "might":
            out[k] = max(0.0, v)  # might left as raw stacks contribution (0..25)
        else:
            out[k] = max(0.0, min(1.0, v))
    return out


def _approx_from_splits(profession: str, specialization: str, mode: str) -> Dict[str, float]:
    # Aggregate contributions from traits/skills matching profession/specialization.
    traits = SPLIT_BALANCE_DATA.get("traits", {})
    skills = SPLIT_BALANCE_DATA.get("skills", {})

    agg: Dict[str, float] = {k: 0.0 for k in BOON_KEYS}

    def add_boon(boon: str, value: float) -> None:
        if boon not in agg:
            return
        agg[boon] += value

    # Traits
    for _id, t in traits.items():
        if t.get("profession") != profession:
            continue
        if t.get("specialization") and t.get("specialization") != specialization:
            continue
        data = t.get(mode, {})
        # Direct boon field
        boon = data.get("boon")
        if boon:
            contrib = float(data.get("uptime_contribution", 0.1))
            if boon == "might":
                stacks = float(data.get("stacks", 0))
                if stacks:
                    add_boon("might", stacks)
                else:
                    # treat duration-based might as small contribution
                    add_boon("might", 2.0)
            else:
                add_boon(boon, contrib)
        # Heuristic keys
        for k, v in list(data.items()):
            if k.endswith("_duration") and isinstance(v, str):
                # e.g., quickness_duration: "2s" -> add ~0.1
                key = k.replace("_duration", "")
                if key in agg:
                    add_boon(key, 0.1)
            if k.endswith("_stacks") and isinstance(v, (int, float)):
                key = k.replace("_stacks", "")
                if key == "might":
                    add_boon("might", float(v))
                elif key in agg:
                    add_boon(key, min(1.0, float(v) * 0.05))
    # Skills (AOE often affect uptime/radius)
    for _id, s in skills.items():
        if s.get("profession") != profession:
            continue
        data = s.get(mode, {})
        # Heuristic: wells/tomes/overloads contribute small amounts
        name = (s.get("name") or "").lower()
        small = 0.05
        if any(tag in name for tag in ["well", "tome", "overload", "gyro", "sphere", "summit", "orders"]):
            # check specific hints
            if "alacrity" in str(data).lower():
                add_boon("alacrity", small)
            if "quickness" in str(data).lower():
                add_boon("quickness", small)
            if "stability" in str(data).lower():
                add_boon("stability", small)
            if "protection" in str(data).lower():
                add_boon("protection", small)
            if "fury" in str(data).lower():
                add_boon("fury", small)
            if "might" in str(data).lower():
                add_boon("might", 2.0)
            if "resistance" in str(data).lower():
                add_boon("resistance", small)

    return _normalize(agg)


def compute_capability_vector(build: BuildTemplateInput, mode: str) -> Dict[str, float]:
    """Return a capability vector for the build using WvW/PvE splits, with fallbacks.
    Keys: quickness, alacrity, stability, resistance, protection, might, fury, dps, sustain
    """
    profession = build.profession
    spec = build.specialization
    # 0) Prefer KB capability if available
    kb_vec = get_capability_from_kb(profession, spec)
    if kb_vec is not None:
        # KB includes only boons/dps/sustain ready to use
        return kb_vec.model_dump()

    # 1) Else approximate from splits and apply fallbacks
    boons = _approx_from_splits(profession, spec, mode)

    # Fallback boon contributions for key WvW specs if splits are incomplete
    key = f"{profession.lower()}:{spec.lower()}"
    fallback_boons: Dict[str, Dict[str, float]] = {
        "guardian:firebrand": {
            "quickness": 0.6,
            "stability": 0.6,
            "protection": 0.5,
            "fury": 0.1,
            "might": 6.0,
        },
        "engineer:scrapper": {
            "stability": 0.4,
            "resistance": 0.6,
            "quickness": 0.3,
            "protection": 0.2,
            "fury": 0.1,
            "might": 4.0,
        },
        "revenant:herald": {
            "quickness": 0.5,
            "protection": 0.5,
            "fury": 0.8,
            "might": 15.0,
        },
        "elementalist:tempest": {
            "resistance": 0.6,
            "protection": 0.4,
            "fury": 0.2,
            "might": 8.0,
        },
        "necromancer:scourge": {
            "resistance": 0.2,
            "fury": 0.2,
            "might": 10.0,
        },
        "engineer:mechanist": {
            "alacrity": 0.6,
            "fury": 0.2,
            "might": 10.0,
        },
    }
    if key in fallback_boons:
        fb = fallback_boons[key]
        merged: Dict[str, float] = dict(boons)
        for k2, v2 in fb.items():
            merged[k2] = max(merged.get(k2, 0.0), float(v2))
        boons = _normalize(merged)

    # Fallbacks for dps/sustain per spec (heuristic)
    dps = 0.5
    sustain = 0.5
    heur = {
        "guardian:firebrand": (0.5, 0.8),
        "engineer:scrapper": (0.5, 0.7),
        "revenant:herald": (0.6, 0.6),
        "elementalist:tempest": (0.4, 0.8),
        "necromancer:scourge": (0.6, 0.7),
        "engineer:mechanist": (0.6, 0.5),
    }
    if key in heur:
        dps, sustain = heur[key]

    out: Dict[str, float] = {**boons, "dps": dps, "sustain": sustain}
    return out
