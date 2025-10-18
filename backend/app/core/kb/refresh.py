#!/usr/bin/env python3
"""
KB Refresh Script — Auto-learning cycle for GW2_WvWbuilder

This script:
1. Ingests data from GW2 API (official)
2. Ingests data from GW2 Wiki (official)
3. Crawls community sources (MetaBattle, Hardstuck, etc.)
4. Enriches synergies via LLM (Mistral/Ollama) if --with-llm
5. Saves updated KB to app/var/kb.json
6. Optionally triggers backend restart if --auto

Usage:
  python app/core/kb/refresh.py [--with-llm] [--auto]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.kb.ingest_gw2 import ingest_all as ingest_gw2
from app.core.kb.ingest_wiki import ingest_wiki_data
from app.core.kb.web_crawler import crawl_all_sources, extract_synergies_from_crawl
from app.core.kb.builder import build_kb_from_gw2_data
from app.core.kb.store import save_kb

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def refresh_kb(with_llm: bool = False, auto: bool = False) -> None:
    """Refresh KB with latest data from all sources."""
    logger.info("=" * 60)
    logger.info("KB Refresh Cycle Started")
    logger.info("=" * 60)

    # Step 1: Ingest GW2 API
    logger.info("Step 1/5: Ingesting GW2 API data...")
    gw2_data = ingest_gw2()
    logger.info(f"  → {len(gw2_data.get('skills', []))} skills")
    logger.info(f"  → {len(gw2_data.get('traits', []))} traits")
    logger.info(f"  → {len(gw2_data.get('specializations', []))} specializations")

    # Step 2: Ingest Wiki data
    logger.info("Step 2/5: Ingesting GW2 Wiki data...")
    wiki_data = ingest_wiki_data()
    logger.info(f"  → {len(wiki_data.get('boon_priorities', {}))} mode priorities")
    logger.info(f"  → {len(wiki_data.get('spec_notes', {}))} spec notes")

    # Step 3: Crawl community sources
    logger.info("Step 3/5: Crawling community sources...")
    web_sources_enabled = os.getenv("LLM_WEB_SOURCES", "0") == "1"

    if web_sources_enabled:
        crawl_data = crawl_all_sources()
        web_synergies = extract_synergies_from_crawl(crawl_data)
        logger.info(f"  → {sum(len(v) for v in crawl_data.values())} pages crawled")
        logger.info(f"  → {len(web_synergies)} synergy pairs extracted")
    else:
        logger.info("  → Web sources disabled (set LLM_WEB_SOURCES=1 to enable)")
        web_synergies = []

    # Step 4: Build KB from all data
    logger.info("Step 4/5: Building KB from aggregated data...")
    kb = build_kb_from_gw2_data(mode="wvw")

    # Add web synergies to KB metadata
    if web_synergies:
        kb.meta["web_synergies"] = [
            {"pair": pair, "source": "web_crawl"} for pair in web_synergies
        ]

    logger.info(f"  → {len(kb.builds)} build templates in KB")

    # Step 5: Enrich with LLM if requested
    if with_llm and os.getenv("LLM_ENGINE") == "ollama":
        logger.info("Step 5/5: Enriching synergies with LLM (Mistral)...")
        try:
            from app.core.llm.ollama_engine import OllamaEngine

            engine = OllamaEngine()

            # Get all specs in KB
            specs = list(set(b.specialization for b in kb.builds))

            # Ask LLM for synergy matrix
            llm_synergies = engine.get_synergy_pairs(specs, "wvw")
            logger.info(f"  → {len(llm_synergies)} LLM-enriched synergy pairs")

            # Add to KB metadata
            kb.meta["llm_synergies"] = [
                {"pair": pair, "score": score, "source": "llm"}
                for pair, score in llm_synergies.items()
            ]
        except Exception as e:
            logger.warning(f"LLM enrichment failed: {e}")
    else:
        logger.info(
            "Step 5/5: Skipping LLM enrichment (--with-llm not set or LLM_ENGINE != ollama)"
        )

    # Save KB
    logger.info("Saving KB to disk...")
    save_kb(kb)
    logger.info(f"  → KB saved to app/var/kb.json")

    logger.info("=" * 60)
    logger.info("KB Refresh Cycle Complete")
    logger.info("=" * 60)

    # Auto-restart backend if requested
    if auto:
        logger.info(
            "Auto-restart requested, but not implemented (manual restart required)"
        )
        logger.info("  → Run: ./stop_all.sh && ./start_all.sh")


def main():
    parser = argparse.ArgumentParser(
        description="Refresh GW2_WvWbuilder Knowledge Base"
    )
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="Enrich synergies with LLM (Mistral/Ollama)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-restart backend after refresh (for cron)",
    )

    args = parser.parse_args()

    try:
        refresh_kb(with_llm=args.with_llm, auto=args.auto)
        sys.exit(0)
    except Exception as e:
        logger.error(f"KB refresh failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
