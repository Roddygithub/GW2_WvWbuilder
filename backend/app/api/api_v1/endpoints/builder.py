"""
Builder endpoints for composition optimization.

This module provides endpoints for optimizing squad compositions
based on game mode, squad size, and optimization goals.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.optimizer import optimize_composition
from app.core.cache import cache_response
from app.schemas.composition import (
    CompositionOptimizationRequest,
    CompositionOptimizationResult,
)
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/optimize",
    response_model=CompositionOptimizationResult,
    status_code=status.HTTP_200_OK,
    summary="Optimize a composition",
    description="""
    Generate an optimized squad composition based on the provided constraints.
    
    The optimizer uses a heuristic algorithm (greedy + local search) to find
    a composition that maximizes the weighted score across multiple objectives:
    - Boon uptime (might, quickness, alacrity, stability, etc.)
    - Healing and survivability
    - Damage output
    - Crowd control
    - WvW-specific capabilities (boon rip, cleanses, etc.)
    
    The optimization is time-boxed to ensure fast response times (typically < 5s).
    
    **Game Modes:**
    - `zerg`: Large-scale fights (30-50 players) - emphasis on boon coverage and sustain
    - `roaming`: Small groups (2-10 players) - emphasis on burst and mobility
    - `guild_raid`: Organized guild groups (15-30 players) - emphasis on coordination
    
    **Example Request:**
    ```json
    {
      "squad_size": 15,
      "game_mode": "zerg",
      "preferred_roles": {
        "healer": 3,
        "boon_support": 3,
        "dps": 9
      },
      "optimization_goals": ["boon_uptime", "healing", "damage"],
      "fixed_roles": [
        {
          "profession_id": 1,
          "elite_specialization_id": 3,
          "count": 2,
          "role_type": "healer"
        }
      ]
    }
    ```
    """,
    responses={
        200: {
            "description": "Optimized composition with metrics",
            "content": {
                "application/json": {
                    "example": {
                        "composition": {
                            "id": 0,
                            "name": "Optimized ZERG Composition",
                            "description": "Auto-generated composition for 15 players",
                            "squad_size": 15,
                            "game_mode": "zerg",
                            "is_public": True,
                            "tags": ["zerg", "optimized", "auto-generated"],
                        },
                        "score": 0.87,
                        "metrics": {
                            "boon_uptime": 0.92,
                            "healing": 0.85,
                            "damage": 0.78,
                            "crowd_control": 0.82,
                            "survivability": 0.88,
                        },
                        "role_distribution": {
                            "healer": 3,
                            "boon_support": 3,
                            "dps": 8,
                            "utility": 1,
                        },
                        "boon_coverage": {
                            "might": 0.95,
                            "quickness": 0.90,
                            "alacrity": 0.85,
                            "stability": 0.88,
                        },
                        "notes": [
                            "✓ Excellent might coverage at 95%",
                            "✓ Strong boon coverage for sustained fights",
                            "✓ Good healing and sustain",
                        ],
                    }
                }
            },
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Optimization failed"},
    },
)
async def optimize_composition_endpoint(
    request: CompositionOptimizationRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_async_db),
) -> CompositionOptimizationResult:
    """
    Optimize a squad composition based on the provided constraints.

    This endpoint generates an optimized composition using a heuristic algorithm
    that balances multiple objectives (boons, healing, damage, etc.) based on
    the game mode and squad size.

    The optimization is time-boxed to ensure fast response times.
    """
    try:
        logger.info(
            f"User {current_user.id} requested optimization: "
            f"mode={request.game_mode}, size={request.squad_size}"
        )

        # Validate squad size
        if request.squad_size < 1 or request.squad_size > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Squad size must be between 1 and 50",
            )

        # Validate fixed roles don't exceed squad size
        if request.fixed_roles:
            total_fixed = sum(role.count for role in request.fixed_roles)
            if total_fixed > request.squad_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Fixed roles count ({total_fixed}) exceeds squad size ({request.squad_size})",
                )

        # Run optimization
        result = optimize_composition(request)

        logger.info(
            f"Optimization completed: score={result.score:.3f}, "
            f"roles={result.role_distribution}"
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error in optimization: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Optimization failed. Please try again or contact support.",
        )


@router.get(
    "/modes",
    response_model=Dict[str, Any],
    summary="Get available game modes",
)
@cache_response(ttl=3600)  # Cache for 1 hour (game modes rarely change)
async def get_game_modes(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_user),
) -> Dict[str, Any]:
    """
    Get list of available game types and modes for composition optimization.
    """
    game_types = {
        "wvw": {
            "name": "World vs World (McM)",
            "modes": [
                {
                    "id": "zerg",
                    "name": "Zerg (30-50 players)",
                    "description": "Large-scale fights with emphasis on boon coverage and coordination",
                    "squad_size_range": [30, 50],
                    "emphasis": ["boon_uptime", "healing", "survivability"],
                },
                {
                    "id": "roaming",
                    "name": "Roaming (2-10 players)",
                    "description": "Small group combat with emphasis on burst and mobility",
                    "squad_size_range": [2, 10],
                    "emphasis": ["burst_damage", "mobility", "self_sustain"],
                },
                {
                    "id": "guild_raid",
                    "name": "Guild Raid (15-30 players)",
                    "description": "Organized guild groups with emphasis on coordination",
                    "squad_size_range": [15, 30],
                    "emphasis": ["coordination", "boon_uptime", "damage"],
                },
            ],
        },
        "pve": {
            "name": "Player vs Environment (PvE)",
            "modes": [
                {
                    "id": "openworld",
                    "name": "Open World (1-5 players)",
                    "description": "Solo or small group open world content",
                    "squad_size_range": [1, 5],
                    "emphasis": ["damage", "survivability", "mobility"],
                },
                {
                    "id": "fractale",
                    "name": "Fractales (5 players)",
                    "description": "5-player instanced content with mechanics",
                    "squad_size_range": [5, 5],
                    "emphasis": ["damage", "boon_uptime", "crowd_control"],
                },
                {
                    "id": "raid",
                    "name": "Raids/Strikes (10 players)",
                    "description": "10-player endgame content with strict requirements",
                    "squad_size_range": [10, 10],
                    "emphasis": ["damage", "boon_uptime", "healing"],
                },
            ],
        },
    }

    return {"game_types": game_types}


@router.get(
    "/professions",
    summary="Get available professions",
    description="Returns a list of available professions for fixed profession selection.",
)
@cache_response(ttl=3600)  # Cache for 1 hour
async def get_available_professions(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Get list of available professions.
    """
    professions = [
        {"id": 1, "name": "Guardian", "color": "blue"},
        {"id": 2, "name": "Revenant", "color": "red"},
        {"id": 3, "name": "Necromancer", "color": "green"},
        {"id": 4, "name": "Warrior", "color": "yellow"},
        {"id": 5, "name": "Elementalist", "color": "red"},
        {"id": 6, "name": "Engineer", "color": "amber"},
        {"id": 7, "name": "Ranger", "color": "green"},
        {"id": 8, "name": "Thief", "color": "gray"},
        {"id": 9, "name": "Mesmer", "color": "purple"},
    ]

    return {"professions": professions}


@router.get(
    "/roles",
    summary="Get available roles",
    description="Returns a list of available roles for composition optimization.",
)
@cache_response(ttl=3600)  # Cache for 1 hour
async def get_available_roles(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """Get available roles for composition optimization."""
    return {
        "roles": [
            {
                "id": "healer",
                "name": "Healer",
                "description": "Provides healing and sustain to the group",
            },
            {
                "id": "boon_support",
                "name": "Boon Support",
                "description": "Provides critical boons (might, quickness, alacrity, etc.)",
            },
            {
                "id": "dps",
                "name": "DPS",
                "description": "Deals damage to enemies",
            },
            {
                "id": "support",
                "name": "Support",
                "description": "Provides utility and support (barrier, cleanses, etc.)",
            },
            {
                "id": "utility",
                "name": "Utility",
                "description": "Provides special utilities (portals, stealth, etc.)",
            },
            {
                "id": "power_damage",
                "name": "Power DPS",
                "description": "Deals power-based damage",
            },
            {
                "id": "condition_damage",
                "name": "Condition DPS",
                "description": "Deals condition-based damage",
            },
        ]
    }
