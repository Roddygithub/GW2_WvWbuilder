from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Boon(BaseModel):
    key: str
    description: Optional[str] = None


class RoleVector(BaseModel):
    stability: float = 0.0
    resistance: float = 0.0
    quickness: float = 0.0
    alacrity: float = 0.0
    protection: float = 0.0
    might: float = 0.0
    fury: float = 0.0
    cleanse: float = 0.0
    cc: float = 0.0
    range: float = 0.0
    stealth: float = 0.0
    mobility: float = 0.0


class CapabilityVector(BaseModel):
    quickness: float = 0.0
    alacrity: float = 0.0
    stability: float = 0.0
    resistance: float = 0.0
    protection: float = 0.0
    might: float = 0.0
    fury: float = 0.0
    dps: float = 0.5
    sustain: float = 0.5


class BuildTemplateKB(BaseModel):
    id: int
    profession: str
    specialization: str
    is_elite: bool = (
        True  # True for elite specializations (Firebrand, Scrapper, etc.), False for core
    )
    capability: CapabilityVector


class KnowledgeBase(BaseModel):
    builds: List[BuildTemplateKB] = []
    meta: Dict[str, Any] = {}

    def capability_map(self) -> Dict[str, Dict[str, float]]:
        m: Dict[str, Dict[str, float]] = {}
        for b in self.builds:
            key = f"{b.profession.lower()}:{b.specialization.lower()}"
            m[key] = b.capability.model_dump()
        return m
