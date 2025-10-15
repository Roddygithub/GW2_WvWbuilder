#!/usr/bin/env python3
"""
Test script for the composition optimizer.

This script tests the optimizer engine directly without requiring
the full API server to be running.
"""

import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.optimizer import optimize_composition
from app.schemas.composition import CompositionOptimizationRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_zerg_optimization():
    """Test optimization for zerg mode."""
    logger.info("=" * 80)
    logger.info("Testing ZERG optimization (15 players)")
    logger.info("=" * 80)
    
    request = CompositionOptimizationRequest(
        squad_size=15,
        game_mode="zerg",
        preferred_roles={
            "healer": 3,
            "boon_support": 3,
            "dps": 9,
        },
        optimization_goals=["boon_uptime", "healing", "damage"],
        fixed_roles=[
            {
                "profession_id": 1,
                "elite_specialization_id": 3,
                "count": 2,
                "role_type": "healer",
            }
        ],
    )
    
    result = optimize_composition(request)
    
    logger.info(f"\n✓ Optimization completed!")
    logger.info(f"  Score: {result.score:.3f} ({result.score * 100:.1f}%)")
    logger.info(f"  Composition: {result.composition.name}")
    logger.info(f"\n  Role Distribution:")
    for role, count in result.role_distribution.items():
        logger.info(f"    - {role}: {count}")
    
    logger.info(f"\n  Metrics:")
    for metric, value in result.metrics.items():
        logger.info(f"    - {metric}: {value:.2%}")
    
    logger.info(f"\n  Boon Coverage:")
    for boon, coverage in result.boon_coverage.items():
        logger.info(f"    - {boon}: {coverage:.2%}")
    
    if result.notes:
        logger.info(f"\n  Notes:")
        for note in result.notes:
            logger.info(f"    {note}")
    
    return result


def test_roaming_optimization():
    """Test optimization for roaming mode."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing ROAMING optimization (5 players)")
    logger.info("=" * 80)
    
    request = CompositionOptimizationRequest(
        squad_size=5,
        game_mode="roaming",
        optimization_goals=["burst_damage", "mobility", "self_sustain"],
    )
    
    result = optimize_composition(request)
    
    logger.info(f"\n✓ Optimization completed!")
    logger.info(f"  Score: {result.score:.3f} ({result.score * 100:.1f}%)")
    logger.info(f"  Composition: {result.composition.name}")
    logger.info(f"\n  Role Distribution:")
    for role, count in result.role_distribution.items():
        logger.info(f"    - {role}: {count}")
    
    logger.info(f"\n  Metrics:")
    for metric, value in result.metrics.items():
        logger.info(f"    - {metric}: {value:.2%}")
    
    if result.notes:
        logger.info(f"\n  Notes:")
        for note in result.notes:
            logger.info(f"    {note}")
    
    return result


def test_guild_raid_optimization():
    """Test optimization for guild raid mode."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing GUILD RAID optimization (25 players)")
    logger.info("=" * 80)
    
    request = CompositionOptimizationRequest(
        squad_size=25,
        game_mode="guild_raid",
        preferred_roles={
            "healer": 5,
            "boon_support": 5,
            "dps": 15,
        },
        optimization_goals=["boon_uptime", "coordination", "damage"],
    )
    
    result = optimize_composition(request)
    
    logger.info(f"\n✓ Optimization completed!")
    logger.info(f"  Score: {result.score:.3f} ({result.score * 100:.1f}%)")
    logger.info(f"  Composition: {result.composition.name}")
    logger.info(f"\n  Role Distribution:")
    for role, count in result.role_distribution.items():
        logger.info(f"    - {role}: {count}")
    
    logger.info(f"\n  Metrics:")
    for metric, value in result.metrics.items():
        logger.info(f"    - {metric}: {value:.2%}")
    
    if result.notes:
        logger.info(f"\n  Notes:")
        for note in result.notes:
            logger.info(f"    {note}")
    
    return result


def generate_example_payloads():
    """Generate example request/response payloads for documentation."""
    logger.info("\n" + "=" * 80)
    logger.info("Generating example payloads")
    logger.info("=" * 80)
    
    # Example request
    request = CompositionOptimizationRequest(
        squad_size=15,
        game_mode="zerg",
        preferred_roles={
            "healer": 3,
            "boon_support": 3,
            "dps": 9,
        },
        optimization_goals=["boon_uptime", "healing", "damage"],
        fixed_roles=[
            {
                "profession_id": 1,
                "elite_specialization_id": 3,
                "count": 2,
                "role_type": "healer",
            }
        ],
    )
    
    result = optimize_composition(request)
    
    # Save example request
    request_json = request.model_dump(mode='json')
    with open('example_request.json', 'w') as f:
        json.dump(request_json, f, indent=2)
    logger.info("✓ Saved example_request.json")
    
    # Save example response
    response_json = result.model_dump(mode='json')
    with open('example_response.json', 'w') as f:
        json.dump(response_json, f, indent=2)
    logger.info("✓ Saved example_response.json")
    
    logger.info("\nExample Request:")
    print(json.dumps(request_json, indent=2))
    
    logger.info("\nExample Response (truncated):")
    truncated = {
        "score": result.score,
        "metrics": result.metrics,
        "role_distribution": result.role_distribution,
        "boon_coverage": result.boon_coverage,
        "notes": result.notes,
    }
    print(json.dumps(truncated, indent=2))


def main():
    """Run all tests."""
    try:
        # Test different modes
        test_zerg_optimization()
        test_roaming_optimization()
        test_guild_raid_optimization()
        
        # Generate example payloads
        generate_example_payloads()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ All tests passed!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
