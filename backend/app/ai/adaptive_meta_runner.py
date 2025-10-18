#!/usr/bin/env python3
"""
Adaptive Meta Runner — GW2_WvWBuilder v4.3

Orchestrates the complete adaptive meta system:
1. Monitors patch notes
2. Analyzes changes with LLM
3. Updates weights and synergies
4. Records history

Can be run manually or via cron (every 12h recommended).

Usage:
    python app/ai/adaptive_meta_runner.py [--with-llm] [--dry-run]
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env
from dotenv import load_dotenv
# Load from project root (3 levels up: app/ai/adaptive_meta_runner.py -> backend)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.ai.patch_monitor import monitor_all_sources, filter_recent_changes
from app.ai.meta_analyzer import analyze_all_changes, recalculate_synergies
from app.ai.meta_weights_updater import MetaWeightsUpdater

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def run_adaptive_meta(with_llm: bool = False, dry_run: bool = False):
    """Run the complete adaptive meta cycle."""
    logger.info("=" * 70)
    logger.info("Adaptive Meta System v4.3")
    logger.info("=" * 70)
    
    # Step 1: Monitor patch notes
    logger.info("Step 1/4: Monitoring patch notes from all sources...")
    all_changes = monitor_all_sources()
    
    if not all_changes:
        logger.info("No changes detected. Exiting.")
        return
    
    # Filter to recent changes only
    recent_changes = filter_recent_changes(all_changes, days=30)
    logger.info(f"  → {len(all_changes)} total changes, {len(recent_changes)} in last 30 days")
    
    if not recent_changes:
        logger.info("No recent changes. Exiting.")
        return
    
    # Step 2: Analyze changes with LLM (if available)
    logger.info("Step 2/4: Analyzing balance changes...")
    llm_engine = None
    
    if with_llm and os.getenv("LLM_ENGINE") == "ollama":
        try:
            from app.core.llm.ollama_engine import OllamaEngine
            llm_engine = OllamaEngine()
            logger.info("  → LLM engine (Mistral) activated")
        except Exception as e:
            logger.warning(f"LLM engine unavailable: {e}")
    else:
        logger.info("  → Using heuristic analysis (no LLM)")
    
    analyses = analyze_all_changes(recent_changes, llm_engine)
    
    if not analyses:
        logger.info("No analyses generated. Exiting.")
        return
    
    # Step 3: Update weights
    logger.info("Step 3/4: Updating specialization weights...")
    updater = MetaWeightsUpdater()
    
    if dry_run:
        logger.info("  → DRY RUN: No changes will be saved")
        for analysis in analyses:
            spec = analysis["spec"]
            delta = analysis["weight_delta"]
            current = updater.get_weight(spec)
            new_weight = max(0.1, min(2.0, current + delta))
            logger.info(f"    Would adjust {spec}: {current:.2f} → {new_weight:.2f}")
    else:
        updated_weights = updater.apply_weight_adjustments(analyses)
        logger.info(f"  → Weights updated: {len(updated_weights)} specs")
    
    # Step 4: Recalculate synergies
    logger.info("Step 4/4: Recalculating synergy matrix...")
    current_synergies = updater.current_synergies
    
    if llm_engine:
        updated_synergies = recalculate_synergies(analyses, current_synergies, llm_engine)
    else:
        updated_synergies = recalculate_synergies(analyses, current_synergies, None)
    
    if dry_run:
        logger.info("  → DRY RUN: Synergies not saved")
        logger.info(f"    Would update {len(updated_synergies)} synergy pairs")
    else:
        updater.apply_synergy_updates(updated_synergies)
        logger.info(f"  → Synergies updated: {len(updated_synergies)} pairs")
    
    # Summary
    logger.info("=" * 70)
    logger.info("Adaptive Meta System Complete")
    logger.info("=" * 70)
    logger.info(f"Changes detected: {len(recent_changes)}")
    logger.info(f"Analyses generated: {len(analyses)}")
    logger.info(f"Weights adjusted: {len([a for a in analyses if a['weight_delta'] != 0.0])}")
    logger.info(f"Synergies updated: {len(updated_synergies)}")
    
    if not dry_run:
        logger.info("")
        logger.info("Data files updated:")
        logger.info(f"  - {updater.weights_file}")
        logger.info(f"  - {updater.history_file}")
        logger.info(f"  - {updater.synergies_file}")
    
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Run Adaptive Meta System")
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="Use LLM (Mistral) for intelligent analysis"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving changes (test mode)"
    )
    
    args = parser.parse_args()
    
    try:
        run_adaptive_meta(with_llm=args.with_llm, dry_run=args.dry_run)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Adaptive meta system failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
