from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

DEFAULT_WEIGHTS: Dict[str, float] = {
    "quickness": 1.0,
    "alacrity": 1.0,
    "stability": 0.9,
    "protection": 0.6,
    "might": 0.4,
    "fury": 0.3,
    "dps": 0.3,
    "sustain": 0.3,
    # Soft-only objective extras
    "dup_penalty_group": 0.20,   # penalty per extra duplicate per group
    "dup_penalty_global": 0.05,  # penalty per extra duplicate squad-wide
    "diversity_reward": 0.03,    # reward per unique spec present per group
    "synergy": 0.05,             # reward weight for synergy pairs
}


class PlayerInput(BaseModel):
    id: int
    name: str
    eligible_build_ids: List[int] = Field(default_factory=list)
    preferences: Optional[Dict[str, float]] = None


class BuildTemplateInput(BaseModel):
    id: int
    profession: str
    specialization: str
    mode: Literal["wvw", "pve"] = "wvw"


class LockConstraint(BaseModel):
    player_id: int
    build_id: Optional[int] = None
    group_id: Optional[int] = None


class TargetsConfig(BaseModel):
    stability_sources: int = 1
    resistance_uptime: float = 0.8
    protection_uptime: float = 0.6
    quickness_uptime: float = 0.9
    alacrity_uptime: float = 0.9
    might_stacks: int = 20
    fury_uptime: float = 0.3


class OptimizationRequest(BaseModel):
    players: List[PlayerInput]
    builds: List[BuildTemplateInput]
    mode: Literal["wvw", "pve"] = "wvw"
    wvw_mode: Optional[Literal["zerg", "havoc", "roaming", "defense", "gank"]] = "zerg"
    squad_size: int = 15
    weights: Dict[str, float] = Field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    targets: TargetsConfig = Field(default_factory=TargetsConfig)
    locks: List[LockConstraint] = Field(default_factory=list)
    time_limit_ms: int = 2000


class GroupAssignment(BaseModel):
    group_id: int
    players: List[int]
    builds: List[int]


class OptimizationResult(BaseModel):
    status: Literal["running", "complete", "cancelled", "timeout"] = "running"
    best_score: float = 0.0
    elapsed_ms: int = 0
    groups: List[GroupAssignment] = Field(default_factory=list)
    coverage_by_group: List[Dict[str, float]] = Field(default_factory=list)
    diagnostics: Dict[str, object] = Field(default_factory=dict)
