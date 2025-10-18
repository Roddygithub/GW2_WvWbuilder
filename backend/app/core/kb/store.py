from __future__ import annotations

import json
import os
from typing import Optional

from .schemas import KnowledgeBase, BuildTemplateKB, CapabilityVector

KB_PATH = os.getenv("GW2_WVWB_KB_PATH", os.path.join(os.path.dirname(__file__), "../../var/kb.json"))
KB_PATH = os.path.abspath(KB_PATH)

_cached_kb: Optional[KnowledgeBase] = None


def load_kb() -> KnowledgeBase:
    global _cached_kb
    if _cached_kb is not None:
        return _cached_kb
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            _cached_kb = KnowledgeBase.model_validate(data)
            return _cached_kb
    except FileNotFoundError:
        _cached_kb = KnowledgeBase(builds=[], meta={"status": "empty"})
        return _cached_kb


def save_kb(kb: KnowledgeBase) -> None:
    global _cached_kb
    os.makedirs(os.path.dirname(KB_PATH), exist_ok=True)
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
    _cached_kb = kb


def get_capability_from_kb(profession: str, specialization: str) -> Optional[CapabilityVector]:
    kb = load_kb()
    key = f"{profession.lower()}:{specialization.lower()}"
    m = kb.capability_map()
    vec = m.get(key)
    if vec:
        return CapabilityVector.model_validate(vec)
    return None
