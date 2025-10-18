from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.optimization import OptimizationRequest, OptimizationResult
from app.core.optimizer.solver_cp_sat import solve_cp_sat

router = APIRouter()

JOB_STORE: Dict[str, Dict] = {}
STREAM_QUEUES: Dict[str, asyncio.Queue] = {}


async def _run_job(job_id: str, req: OptimizationRequest) -> None:
    start = time.time()
    JOB_STORE[job_id]["status"] = "running"
    queue = STREAM_QUEUES.get(job_id)

    def on_intermediate(payload: Dict) -> None:
        """Push intermediate solution to queue."""
        if queue:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    # Apply preset weights/targets from wvw_mode if provided
    if req.wvw_mode:
        from app.services.weights_presets import get_preset_weights, get_preset_targets

        preset_weights = get_preset_weights(req.wvw_mode)
        preset_targets = get_preset_targets(req.wvw_mode)
        # Merge: user-provided weights override presets
        for k, v in preset_weights.items():
            if k not in req.weights:
                req.weights[k] = v
        # Merge targets
        for k, v in preset_targets.items():
            if not hasattr(req.targets, k) or getattr(req.targets, k) is None:
                setattr(req.targets, k, v)

    try:
        from app.core.optimizer.solver_cp_sat_streaming import solve_cp_sat_streaming

        result: OptimizationResult = solve_cp_sat_streaming(req, on_intermediate)
        JOB_STORE[job_id]["result"] = result.model_dump()
        JOB_STORE[job_id]["status"] = result.status
        # Push final result to queue
        if queue:
            queue.put_nowait({"status": result.status, "result": result.model_dump()})
    except Exception as e:
        JOB_STORE[job_id]["status"] = "error"
        JOB_STORE[job_id]["error"] = str(e)
        if queue:
            queue.put_nowait({"status": "error", "error": str(e)})
    finally:
        JOB_STORE[job_id]["elapsed_ms"] = int((time.time() - start) * 1000)
        if queue:
            queue.put_nowait({"status": "done"})


@router.post("/optimize")
async def start_optimization(req: OptimizationRequest) -> Dict[str, str]:
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = {"status": "queued", "result": None, "elapsed_ms": 0}
    STREAM_QUEUES[job_id] = asyncio.Queue(maxsize=100)
    asyncio.create_task(_run_job(job_id, req))
    return {"job_id": job_id}


@router.get("/optimize/status/{job_id}")
async def get_status(job_id: str) -> Dict:
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.get("/optimize/stream/{job_id}")
async def stream(job_id: str):
    queue = STREAM_QUEUES.get(job_id)
    if not queue:

        async def not_found():
            yield f"data: {json.dumps({'status': 'not_found'})}\n\n"

        return StreamingResponse(not_found(), media_type="text/event-stream")

    async def event_gen():
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=5.0)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg.get("status") in (
                    "done",
                    "error",
                    "complete",
                    "timeout",
                    "cancelled",
                ):
                    break
            except asyncio.TimeoutError:
                # Send keepalive
                yield f": keepalive\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.post("/optimize/cancel/{job_id}")
async def cancel(job_id: str) -> Dict[str, str]:
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    job["status"] = "cancelled"
    return {"status": "cancelled"}
