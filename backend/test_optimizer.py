#!/usr/bin/env python3
"""
Test script to debug optimizer issues
"""

import sys
import traceback
from app.core.optimizer import optimize_composition
from app.schemas.composition import CompositionOptimizationRequest

def test_optimization():
    """Test the optimization engine directly"""
    
    request = CompositionOptimizationRequest(
        squad_size=5,
        game_type="wvw",
        game_mode="roaming",
        optimization_goals=["boon_uptime", "healing", "damage"]
    )
    
    print(f"Testing optimization with:")
    print(f"  - squad_size: {request.squad_size}")
    print(f"  - game_type: {request.game_type}")
    print(f"  - game_mode: {request.game_mode}")
    print()
    
    try:
        result = optimize_composition(request)
        print("✅ SUCCESS!")
        print(f"Score: {result.score:.3f}")
        print(f"Roles: {result.role_distribution}")
        return True
    except Exception as e:
        print("❌ ERROR!")
        print(f"Exception: {type(e).__name__}: {e}")
        print()
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimization()
    sys.exit(0 if success else 1)
