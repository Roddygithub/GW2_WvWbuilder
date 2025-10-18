from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class LLMEngine(ABC):
    """
    Abstract interface for local LLM engines used to guide soft weights (synergy, penalties).
    Implementations must be lightweight and resilient (fallback to sane defaults).
    """

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def get_synergy_pairs(
        self, specs: List[str], mode: str
    ) -> Dict[Tuple[str, str], float]:
        """
        Return a mapping of (spec_a, spec_b) -> synergy_score in [0,1].
        Only pairs present in specs should be returned. Missing pairs are assumed 0.
        """
        ...

    def _normalize_pair(self, a: str, b: str) -> Tuple[str, str]:
        ra, rb = a.strip().lower(), b.strip().lower()
        return (ra, rb) if ra <= rb else (rb, ra)
