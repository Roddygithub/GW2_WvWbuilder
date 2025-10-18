"""
Meta Evolution API Endpoints — GW2_WvWBuilder v4.3

Provides access to adaptive meta system data and controls.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.ai.meta_weights_updater import MetaWeightsUpdater
from app.ai.patch_monitor import monitor_all_sources, filter_recent_changes
from app.ai.meta_analyzer import analyze_all_changes
from app.core.llm.ollama_engine import OllamaEngine
import os

router = APIRouter()


# Schemas
class WeightInfo(BaseModel):
    spec: str
    weight: float
    last_updated: Optional[str] = None


class SynergyInfo(BaseModel):
    spec1: str
    spec2: str
    score: float


class HistoryEntry(BaseModel):
    timestamp: str
    adjustments: List[Dict]
    source: str


class PatchChange(BaseModel):
    date: str
    spec: str
    change_type: str
    impact: str
    magnitude: Optional[str]
    source: str


class MetaStats(BaseModel):
    total_specs: int
    total_synergies: int
    history_entries: int
    last_update: Optional[str]
    avg_weight: float
    top_specs: List[WeightInfo]
    bottom_specs: List[WeightInfo]


# Endpoints
@router.get("/weights", response_model=List[WeightInfo])
def get_current_weights():
    """Get current specialization weights."""
    updater = MetaWeightsUpdater()
    weights = updater.get_weights()
    
    return [
        WeightInfo(spec=spec, weight=weight)
        for spec, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True)
    ]


@router.get("/weights/{spec}", response_model=WeightInfo)
def get_spec_weight(spec: str):
    """Get weight for a specific specialization."""
    updater = MetaWeightsUpdater()
    weight = updater.get_weight(spec)
    
    if weight is None:
        raise HTTPException(status_code=404, detail=f"Spec '{spec}' not found")
    
    return WeightInfo(spec=spec, weight=weight)


@router.get("/synergies", response_model=List[SynergyInfo])
def get_synergies(
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get synergy matrix (filtered by min score)."""
    updater = MetaWeightsUpdater()
    synergies = updater.current_synergies
    
    filtered = [
        SynergyInfo(spec1=pair[0], spec2=pair[1], score=score)
        for pair, score in synergies.items()
        if score >= min_score
    ]
    
    # Sort by score descending
    filtered.sort(key=lambda x: x.score, reverse=True)
    
    return filtered[:limit]


@router.get("/history", response_model=List[HistoryEntry])
def get_history(limit: int = Query(50, ge=1, le=200)):
    """Get weight adjustment history."""
    updater = MetaWeightsUpdater()
    history = updater.get_history(limit=limit)
    
    return [
        HistoryEntry(
            timestamp=entry["timestamp"],
            adjustments=entry["adjustments"],
            source=entry.get("source", "unknown")
        )
        for entry in history
    ]


@router.get("/stats", response_model=MetaStats)
def get_meta_stats():
    """Get meta evolution statistics."""
    updater = MetaWeightsUpdater()
    weights = updater.get_weights()
    synergies = updater.current_synergies
    history = updater.get_history(limit=1000)
    
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    avg_weight = sum(weights.values()) / len(weights) if weights else 1.0
    
    top_specs = [
        WeightInfo(spec=spec, weight=weight)
        for spec, weight in sorted_weights[:5]
    ]
    
    bottom_specs = [
        WeightInfo(spec=spec, weight=weight)
        for spec, weight in sorted_weights[-5:]
    ]
    
    last_update = history[-1]["timestamp"] if history else None
    
    return MetaStats(
        total_specs=len(weights),
        total_synergies=len(synergies),
        history_entries=len(history),
        last_update=last_update,
        avg_weight=avg_weight,
        top_specs=top_specs,
        bottom_specs=bottom_specs,
    )


@router.get("/changes/recent", response_model=List[PatchChange])
def get_recent_changes(days: int = Query(30, ge=1, le=365)):
    """Get recent patch changes (cached from last scan)."""
    # This would ideally be cached, but for now we'll do a quick scan
    all_changes = monitor_all_sources()
    recent = filter_recent_changes(all_changes, days=days)
    
    return [
        PatchChange(
            date=change["date"],
            spec=change["spec"],
            change_type=change["change_type"],
            impact=change["impact"],
            magnitude=change.get("magnitude"),
            source=change["source"],
        )
        for change in recent
    ]


@router.post("/scan")
async def trigger_scan(with_llm: bool = False):
    """Manually trigger a patch scan and analysis.
    
    This is typically run via cron, but can be triggered manually.
    """
    from app.ai.adaptive_meta_runner import run_adaptive_meta
    
    try:
        # Run in background (simplified, should use BackgroundTasks in production)
        run_adaptive_meta(with_llm=with_llm, dry_run=False)
        return {"status": "success", "message": "Adaptive meta scan completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/reset")
def reset_weights():
    """Reset all weights to defaults (1.0)."""
    updater = MetaWeightsUpdater()
    updater.reset_to_defaults()
    
    return {"status": "success", "message": "Weights reset to defaults"}


@router.post("/rollback/{timestamp}")
def rollback_to_timestamp(timestamp: str):
    """Rollback weights to a specific timestamp."""
    updater = MetaWeightsUpdater()
    
    try:
        updater.rollback_to_timestamp(timestamp)
        return {"status": "success", "message": f"Rolled back to {timestamp}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rollback failed: {str(e)}")
