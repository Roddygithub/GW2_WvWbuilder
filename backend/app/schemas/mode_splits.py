from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class SplitModeData(RootModel[Dict[str, Any]]):
    # Generic per-mode container; content is flexible but must be a dict
    root: Dict[str, Any]


class SplitTrait(BaseModel):
    name: str
    profession: Optional[str] = None
    specialization: Optional[str] = None
    wvw: Dict[str, Any] = Field(default_factory=dict)
    pve: Dict[str, Any] = Field(default_factory=dict)


class SplitSkill(BaseModel):
    name: str
    profession: Optional[str] = None
    type: Optional[str] = None
    wvw: Dict[str, Any] = Field(default_factory=dict)
    pve: Dict[str, Any] = Field(default_factory=dict)


class ModeSplits(BaseModel):
    source: Optional[str] = None
    last_updated: Optional[str] = None
    version: Optional[str] = None
    coverage: Optional[Dict[str, Any]] = None
    traits: Dict[str, SplitTrait] = Field(default_factory=dict)
    skills: Dict[str, SplitSkill] = Field(default_factory=dict)

    def counts(self) -> Dict[str, int]:
        return {"traits": len(self.traits), "skills": len(self.skills)}
