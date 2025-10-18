from __future__ import annotations

import math
import time
import uuid
from typing import Dict, List, Tuple

import numpy as np
from ortools.sat.python import cp_model

from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResult,
    GroupAssignment,
    BuildTemplateInput,
)
from app.core.optimizer.capabilities import compute_capability_vector


def _capabilities_for_build(b: BuildTemplateInput, mode: str) -> Dict[str, float]:
    return compute_capability_vector(b, mode)


def _build_caps_matrix(builds: List[BuildTemplateInput], mode: str) -> np.ndarray:
    keys = [
        "quickness",
        "alacrity",
        "stability",
        "resistance",
        "protection",
        "might",
        "fury",
        "dps",
        "sustain",
    ]
    m = np.zeros((len(builds), len(keys)), dtype=float)
    for j, b in enumerate(builds):
        caps = _capabilities_for_build(b, mode)
        m[j, :] = [caps[k] for k in keys]
    return m


def solve_cp_sat(req: OptimizationRequest) -> OptimizationResult:
    players = req.players
    builds = req.builds
    n = len(players)
    if n == 0:
        return OptimizationResult(
            status="complete",
            best_score=0.0,
            elapsed_ms=0,
            groups=[],
            coverage_by_group=[],
            diagnostics={},
        )
    group_count = max(1, math.ceil(n / 5))
    build_index: Dict[int, int] = {b.id: idx for idx, b in enumerate(builds)}
    caps = _build_caps_matrix(builds, req.mode)
    keys = [
        "quickness",
        "alacrity",
        "stability",
        "resistance",
        "protection",
        "might",
        "fury",
        "dps",
        "sustain",
    ]
    key_idx = {k: i for i, k in enumerate(keys)}
    model = cp_model.CpModel()
    x = {}
    g = {}
    for i, p in enumerate(players):
        elig = [bid for bid in p.eligible_build_ids if bid in build_index]
        if not elig:
            elig = [builds[0].id]
        for bid in elig:
            j = build_index[bid]
            x[(i, j)] = model.NewBoolVar(f"x_{i}_{j}")
        for k in range(group_count):
            g[(i, k)] = model.NewBoolVar(f"g_{i}_{k}")
        model.Add(sum(x[(i, build_index[bid])] for bid in elig) == 1)
        model.Add(sum(g[(i, k)] for k in range(group_count)) == 1)
    for k in range(group_count):
        model.Add(sum(g[(i, k)] for i in range(n)) <= 5)
    z = {}
    for i, p in enumerate(players):
        elig = [bid for bid in p.eligible_build_ids if bid in build_index]
        if not elig:
            elig = [builds[0].id]
        for bid in elig:
            j = build_index[bid]
            for k in range(group_count):
                z[(i, j, k)] = model.NewBoolVar(f"z_{i}_{j}_{k}")
                model.Add(z[(i, j, k)] <= x[(i, j)])
                model.Add(z[(i, j, k)] <= g[(i, k)])
                model.Add(z[(i, j, k)] >= x[(i, j)] + g[(i, k)] - 1)
    u = {}
    for k in range(group_count):
        for boon in [
            "quickness",
            "alacrity",
            "stability",
            "resistance",
            "protection",
            "fury",
        ]:
            u[(k, boon)] = model.NewIntVar(0, 1000, f"u_{k}_{boon}")
            terms = []
            idx = key_idx[boon]
            for i in range(n):
                elig = [
                    bid for bid in players[i].eligible_build_ids if bid in build_index
                ]
                if not elig:
                    elig = [builds[0].id]
                for bid in elig:
                    j = build_index[bid]
                    coef = int(round(caps[j, idx] * 1000))
                    if coef > 0:
                        terms.append((coef, z[(i, j, k)]))
            if terms:
                model.Add(u[(k, boon)] == sum(coef * var for coef, var in terms))
            else:
                model.Add(u[(k, boon)] == 0)
    might_sum = {}
    for k in range(group_count):
        might_sum[k] = model.NewIntVar(0, 25000, f"might_{k}")
        terms = []
        idx = key_idx["might"]
        for i in range(n):
            elig = [bid for bid in players[i].eligible_build_ids if bid in build_index]
            if not elig:
                elig = [builds[0].id]
            for bid in elig:
                j = build_index[bid]
                coef = int(round(caps[j, idx] * 1000))
                if coef > 0:
                    terms.append((coef, z[(i, j, k)]))
        if terms:
            model.Add(might_sum[k] == sum(coef * var for coef, var in terms))
        else:
            model.Add(might_sum[k] == 0)
    dps_avg = {}
    sustain_avg = {}
    for k in range(group_count):
        dps_avg[k] = model.NewIntVar(0, 1000, f"dps_{k}")
        sustain_avg[k] = model.NewIntVar(0, 1000, f"sustain_{k}")
        dps_terms = []
        sus_terms = []
        for i in range(n):
            elig = [bid for bid in players[i].eligible_build_ids if bid in build_index]
            if not elig:
                elig = [builds[0].id]
            for bid in elig:
                j = build_index[bid]
                dps_coef = int(round(caps[j, key_idx["dps"]] * 1000))
                sus_coef = int(round(caps[j, key_idx["sustain"]] * 1000))
                for gg in range(group_count):
                    dps_terms.append((dps_coef, z[(i, j, gg)]))
                    sus_terms.append((sus_coef, z[(i, j, gg)]))
        if dps_terms:
            model.Add(
                dps_avg[k] == sum(coef * var for coef, var in dps_terms) // max(1, 5)
            )
        else:
            model.Add(dps_avg[k] == 0)
        if sus_terms:
            model.Add(
                sustain_avg[k]
                == sum(coef * var for coef, var in sus_terms) // max(1, 5)
            )
        else:
            model.Add(sustain_avg[k] == 0)
    # High-priority constraints (hard) per group based on req.targets
    t = req.targets
    for k in range(group_count):
        # Quickness uptime ≥ target (e.g., 0.9)
        model.Add(u[(k, "quickness")] >= int(round(t.quickness_uptime * 1000)))
        # Resistance uptime ≥ target (e.g., 0.8)
        model.Add(u[(k, "resistance")] >= int(round(t.resistance_uptime * 1000)))
        # Protection uptime ≥ target (e.g., 0.6)
        model.Add(u[(k, "protection")] >= int(round(t.protection_uptime * 1000)))
        # Stability: approximate "1 source" as a minimum uptime threshold (heuristic)
        if t.stability_sources >= 1:
            model.Add(u[(k, "stability")] >= int(round(0.5 * 1000)))

    w = req.weights
    obj_terms = []

    def iw(v: float) -> int:
        return int(round(v * 1000))

    for k in range(group_count):
        obj_terms.append(iw(w.get("quickness", 0.0)) * u[(k, "quickness")])
        obj_terms.append(iw(w.get("alacrity", 0.0)) * u[(k, "alacrity")])
        obj_terms.append(iw(w.get("stability", 0.0)) * u[(k, "stability")])
        obj_terms.append(iw(w.get("protection", 0.0)) * u[(k, "protection")])
        obj_terms.append(iw(w.get("fury", 0.0)) * u[(k, "fury")])
        obj_terms.append(iw(w.get("might", 0.0)) * might_sum[k])
        obj_terms.append(iw(w.get("dps", 0.0)) * dps_avg[k])
        obj_terms.append(iw(w.get("sustain", 0.0)) * sustain_avg[k])
    model.Maximize(sum(obj_terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(0.1, req.time_limit_ms / 1000.0)
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    groups: List[GroupAssignment] = []
    assign_build_index: List[int] = [-1] * n
    assign_group_index: List[int] = [-1] * n
    for i, p in enumerate(players):
        elig = [bid for bid in p.eligible_build_ids if bid in build_index]
        if not elig:
            elig = [builds[0].id]
        best_j = None
        for bid in elig:
            j = build_index[bid]
            if (i, j) in x and solver.Value(x[(i, j)]) == 1:
                best_j = j
                break
        if best_j is None:
            best_j = build_index[elig[0]]
        assign_build_index[i] = best_j
        best_k = 0
        for k in range(group_count):
            if solver.Value(g[(i, k)]) == 1:
                best_k = k
                break
        assign_group_index[i] = best_k
    group_members: Dict[int, List[int]] = {k: [] for k in range(group_count)}
    group_builds: Dict[int, List[int]] = {k: [] for k in range(group_count)}
    for i, p in enumerate(players):
        k = assign_group_index[i]
        j = assign_build_index[i]
        group_members[k].append(p.id)
        build_id = builds[j].id
        group_builds[k].append(build_id)
    for k in range(group_count):
        groups.append(
            GroupAssignment(
                group_id=k + 1, players=group_members[k], builds=group_builds[k]
            )
        )
    coverage_by_group: List[Dict[str, float]] = []
    for k in range(group_count):
        cov = {}
        for boon in [
            "quickness",
            "alacrity",
            "stability",
            "resistance",
            "protection",
            "fury",
        ]:
            val = solver.Value(u[(k, boon)]) / 1000.0 if (k, boon) in u else 0.0
            if boon == "might":
                pass
            cov[boon] = min(1.0, val)
        coverage_by_group.append(cov)
    best_score = 0.0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        obj_val = solver.ObjectiveValue()
        denom = 1000.0 * group_count if group_count > 0 else 1.0
        best_score = max(0.0, min(1.0, obj_val / (denom * 10.0)))
    elapsed_ms = int(1000 * solver.WallTime())
    return OptimizationResult(
        status="complete",
        best_score=best_score,
        elapsed_ms=elapsed_ms,
        groups=groups,
        coverage_by_group=coverage_by_group,
        diagnostics={"status": int(status)},
    )
