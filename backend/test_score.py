#!/usr/bin/env python3
"""Debug script for score calculation"""

import logging
logging.basicConfig(level=logging.DEBUG)

from app.core.optimizer.engine import OptimizerEngine
from app.schemas.composition import CompositionOptimizationRequest

# Create request
request = CompositionOptimizationRequest(
    squad_size=10,
    game_type="wvw",
    game_mode="zerg",
)

# Create engine
engine = OptimizerEngine(game_type="wvw", game_mode="zerg")

# Generate solution
solution = engine._generate_initial_solution(request)

print(f"\n{'='*60}")
print(f"Solution has {len(solution)} builds")
for i, build in enumerate(solution, 1):
    print(f"  {i}. {build.role_type.value}")
    
# Evaluate
score, metrics, boon_coverage, role_dist = engine.evaluate_solution(solution, request)

print(f"\n{'='*60}")
print(f"FINAL SCORE: {score:.3f} ({score*100:.1f}%)")
print(f"\nMetrics:")
for k, v in metrics.items():
    print(f"  {k}: {v:.3f}")
    
print(f"\nRole Distribution:")
for k, v in role_dist.items():
    print(f"  {k}: {v}")
