"""
Meta Weights Updater — GW2_WvWBuilder v4.3

Dynamically adjusts specialization weights based on patch analysis.
Persists weight history and provides rollback capabilities.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MetaWeightsUpdater:
    """Manages dynamic weight adjustments for specializations."""

    def __init__(self, data_dir: str = "app/var"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.weights_file = self.data_dir / "meta_weights.json"
        self.history_file = self.data_dir / "meta_history.json"
        self.synergies_file = self.data_dir / "synergy_matrix.json"

        self.current_weights = self._load_weights()
        self.current_synergies = self._load_synergies()
        self.history = self._load_history()

    def _load_weights(self) -> Dict[str, float]:
        """Load current weights from disk."""
        if not self.weights_file.exists():
            # Initialize with default weights (1.0 for all)
            from app.core.kb.specs_reference import get_all_elite_specs

            specs = get_all_elite_specs()
            default_weights = {spec.lower(): 1.0 for spec in specs}
            self._save_weights(default_weights)
            return default_weights

        with open(self.weights_file, "r") as f:
            return json.load(f)

    def _save_weights(self, weights: Dict[str, float]) -> None:
        """Save weights to disk."""
        with open(self.weights_file, "w") as f:
            json.dump(weights, f, indent=2)

    def _load_synergies(self) -> Dict[tuple, float]:
        """Load synergy matrix from disk."""
        if not self.synergies_file.exists():
            return {}

        with open(self.synergies_file, "r") as f:
            data = json.load(f)
            # Convert string keys to tuples
            return {tuple(k.split("-")): v for k, v in data.items()}

    def _save_synergies(self, synergies: Dict) -> None:
        """Save synergy matrix to disk."""
        # Convert tuple keys to strings
        serializable = {"-".join(k): v for k, v in synergies.items()}
        with open(self.synergies_file, "w") as f:
            json.dump(serializable, f, indent=2)

    def _load_history(self) -> List[Dict]:
        """Load weight adjustment history."""
        if not self.history_file.exists():
            return []

        with open(self.history_file, "r") as f:
            return json.load(f)

    def _save_history(self) -> None:
        """Save history to disk."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def apply_weight_adjustments(self, analyses: List[Dict]) -> Dict[str, float]:
        """Apply weight adjustments from patch analyses.

        Args:
            analyses: List of change analyses with weight_delta

        Returns:
            Updated weights dict
        """
        logger.info(f"Applying {len(analyses)} weight adjustments...")

        updated_weights = self.current_weights.copy()
        adjustments = []

        for analysis in analyses:
            spec = analysis["spec"].lower()
            delta = analysis.get("weight_delta", 0.0)

            if spec not in updated_weights:
                updated_weights[spec] = 1.0  # Initialize if new

            old_weight = updated_weights[spec]
            new_weight = max(0.1, min(2.0, old_weight + delta))  # Clamp [0.1, 2.0]
            updated_weights[spec] = new_weight

            adjustments.append(
                {
                    "spec": spec,
                    "old_weight": old_weight,
                    "new_weight": new_weight,
                    "delta": delta,
                    "change_type": analysis["change_type"],
                    "reasoning": analysis.get("reasoning", ""),
                }
            )

            logger.info(
                f"  {spec}: {old_weight:.2f} → {new_weight:.2f} (Δ{delta:+.2f})"
            )

        # Record in history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "adjustments": adjustments,
            "source": "patch_analysis",
        }
        self.history.append(history_entry)

        # Persist
        self.current_weights = updated_weights
        self._save_weights(updated_weights)
        self._save_history()

        logger.info(f"Weight adjustments saved. History entries: {len(self.history)}")
        return updated_weights

    def apply_synergy_updates(self, updated_synergies: Dict) -> None:
        """Apply updated synergy matrix."""
        logger.info(f"Updating {len(updated_synergies)} synergy pairs...")

        self.current_synergies = updated_synergies
        self._save_synergies(updated_synergies)

        logger.info("Synergy matrix updated")

    def get_weight(self, spec: str) -> float:
        """Get current weight for a specialization."""
        return self.current_weights.get(spec.lower(), 1.0)

    def get_weights(self) -> Dict[str, float]:
        """Get all current weights."""
        return self.current_weights.copy()

    def get_synergy(self, spec1: str, spec2: str) -> Optional[float]:
        """Get synergy score between two specs."""
        pair = tuple(sorted([spec1.lower(), spec2.lower()]))
        return self.current_synergies.get(pair)

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get weight adjustment history."""
        return self.history[-limit:]

    def rollback_to_timestamp(self, timestamp: str) -> None:
        """Rollback weights to a specific timestamp."""
        logger.info(f"Rolling back weights to {timestamp}...")

        # Find the entry
        target_entry = None
        for entry in self.history:
            if entry["timestamp"] == timestamp:
                target_entry = entry
                break

        if not target_entry:
            logger.error(f"Timestamp {timestamp} not found in history")
            return

        # Reverse all adjustments after this timestamp
        idx = self.history.index(target_entry)
        for entry in reversed(self.history[idx + 1 :]):
            for adj in entry["adjustments"]:
                spec = adj["spec"]
                old_weight = adj["old_weight"]
                self.current_weights[spec] = old_weight

        # Remove future entries
        self.history = self.history[: idx + 1]

        # Persist
        self._save_weights(self.current_weights)
        self._save_history()

        logger.info(f"Rollback complete. Current history entries: {len(self.history)}")

    def reset_to_defaults(self) -> None:
        """Reset all weights to 1.0."""
        logger.info("Resetting all weights to defaults...")

        from app.core.kb.specs_reference import get_all_elite_specs

        specs = get_all_elite_specs()
        self.current_weights = {spec.lower(): 1.0 for spec in specs}

        # Record in history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "adjustments": [{"action": "reset_all", "value": 1.0}],
            "source": "manual_reset",
        }
        self.history.append(history_entry)

        self._save_weights(self.current_weights)
        self._save_history()

        logger.info("Weights reset to defaults")
