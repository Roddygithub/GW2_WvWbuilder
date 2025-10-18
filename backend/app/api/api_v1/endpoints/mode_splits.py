from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.optimizer.mode_effects import SPLIT_BALANCE_DATA
from app.schemas.mode_splits import ModeSplits

router = APIRouter()


@router.get("/", response_model=Dict[str, Any], summary="Get WvW/PvE mode split data (read-only)")
async def get_mode_splits() -> Dict[str, Any]:
    """Return validated mode-split data (versioned JSON)."""
    try:
        data = ModeSplits.model_validate(SPLIT_BALANCE_DATA)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid mode-splits data: {e}")

    counts = data.counts()
    return {
        "version": data.version,
        "last_updated": data.last_updated,
        "coverage": data.coverage,
        "counts": counts,
        "traits": data.traits,
        "skills": data.skills,
    }
