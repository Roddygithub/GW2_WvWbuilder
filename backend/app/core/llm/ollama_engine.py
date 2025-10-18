from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Tuple

import urllib.request

from .engine import LLMEngine

logger = logging.getLogger(__name__)


class OllamaEngine(LLMEngine):
    def __init__(self, model: str | None = None, endpoint: str | None = None) -> None:
        self._model = model or os.getenv("LLM_MODEL", "mistral:7b")
        self._endpoint = endpoint or os.getenv("LLM_ENDPOINT", "http://localhost:11434")

    def name(self) -> str:
        return f"ollama:{self._model}"

    def get_synergy_pairs(
        self, specs: List[str], mode: str
    ) -> Dict[Tuple[str, str], float]:
        """Query LLM for synergy ratings between specs in WvW mode (ONLY).

        Strictly filters for WvW-specific synergies and ignores PvE content.
        """
        specs_lower = [s.lower() for s in specs]
        prompt = (
            f"You are a Guild Wars 2 World vs World (WvW) expert. "
            f"Rate the synergy between the following specializations in {mode} mode "
            f"on a scale from 0.0 (no synergy) to 1.0 (perfect synergy). "
            f"IMPORTANT: Focus ONLY on WvW gameplay (zerg, havoc, roaming). "
            f"IGNORE raids, fractals, strikes, dungeons, and all PvE content. "
            f"Specs: {', '.join(specs)}. "
            "Return ONLY a JSON dict with pairs as keys (e.g., 'Firebrand-Scrapper') and scores as values. "
            'Example: {"Firebrand-Scrapper": 0.95, "Herald-Tempest": 0.80}. '
            "Consider WvW-specific synergies: boon sharing, stability stacking, cleanses, resistance, etc."
        )
        try:
            url = f"{self._endpoint}/api/generate"
            data = json.dumps(
                {
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                out = json.loads(resp.read().decode("utf-8"))
                text = out.get("response", "{}")
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    # Try to extract JSON substring
                    start = text.find("{")
                    end = text.rfind("}")
                    parsed = (
                        json.loads(text[start : end + 1])
                        if start >= 0 and end >= 0
                        else {}
                    )
                result: Dict[Tuple[str, str], float] = {}
                for k, v in parsed.items():
                    if not isinstance(k, str):
                        continue
                    parts = k.split("|")
                    if len(parts) != 2:
                        continue
                    a, b = parts[0].strip(), parts[1].strip()
                    ra, rb = self._normalize_pair(a, b)
                    try:
                        score = float(v)
                    except Exception:
                        continue
                    score = max(0.0, min(1.0, score))
                    result[(ra, rb)] = score
                return result
        except Exception as e:
            logger.warning("OllamaEngine synergy fallback: %s", e)
            return {}

    def explain_composition(self, composition: Dict, mode: str) -> str:
        """Generate a rich explanation of the composition using LLM."""
        groups_summary = []
        for grp in composition.get("groups", []):
            builds = grp.get("builds", [])
            groups_summary.append(f"Group {grp['group_id']}: {len(builds)} players")

        coverage = composition.get("coverage_by_group", [])
        avg_coverage = {}
        if coverage:
            for cov in coverage:
                for boon, val in cov.items():
                    avg_coverage[boon] = avg_coverage.get(boon, 0.0) + val
            for boon in avg_coverage:
                avg_coverage[boon] /= len(coverage)

        prompt = (
            f"You are a Guild Wars 2 World vs World (WvW) tactical expert. "
            f"Analyze this squad composition for {mode} mode. "
            f"IMPORTANT: Focus ONLY on WvW gameplay (zerg fights, havoc groups, roaming). "
            f"IGNORE all PvE content (raids, fractals, strikes, dungeons). "
            f"Groups: {', '.join(groups_summary)}. "
            f"Average boon coverage: {', '.join(f'{k}={int(v*100)}%' for k, v in avg_coverage.items())}. "
            "Provide a concise WvW tactical analysis (2-3 sentences): "
            "strengths in WvW combat, weaknesses against enemy zergs, and one key WvW-specific recommendation."
        )

        try:
            url = f"{self._endpoint}/api/generate"
            data = json.dumps(
                {
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "max_tokens": 150},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                out = json.loads(resp.read().decode("utf-8"))
                text = out.get("response", "")
                return text.strip()
        except Exception as e:
            logger.warning("OllamaEngine explain fallback: %s", e)
            return "LLM analysis unavailable. Composition follows soft-only optimization with balanced boon coverage and diversity."
