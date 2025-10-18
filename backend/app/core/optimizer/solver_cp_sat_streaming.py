from __future__ import annotations

import math
import time
from typing import Callable, Dict, List, Tuple, Set

import numpy as np
from ortools.sat.python import cp_model

from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResult,
    GroupAssignment,
)
from app.core.optimizer.capabilities import compute_capability_vector
from app.core.optimizer.solver_cp_sat_callback import StreamingSolutionCallback


def solve_cp_sat_streaming(
    req: OptimizationRequest,
    on_intermediate: Callable[[Dict], None],
) -> OptimizationResult:
    """
    CP-SAT solver with streaming callback for intermediate best solutions.
    """
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

    # Build capability matrix
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
    caps = np.zeros((len(builds), len(keys)), dtype=float)
    for j, b in enumerate(builds):
        vec = compute_capability_vector(b, req.mode)
        caps[j, :] = [vec.get(k, 0.0) for k in keys]

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

    dps_sum = {}
    sustain_sum = {}
    for k in range(group_count):
        dps_sum[k] = model.NewIntVar(0, 5000, f"dps_{k}")
        sustain_sum[k] = model.NewIntVar(0, 5000, f"sustain_{k}")
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
                if dps_coef > 0:
                    dps_terms.append((dps_coef, z[(i, j, k)]))
                if sus_coef > 0:
                    sus_terms.append((sus_coef, z[(i, j, k)]))
        if dps_terms:
            model.Add(dps_sum[k] == sum(coef * var for coef, var in dps_terms))
        else:
            model.Add(dps_sum[k] == 0)
        if sus_terms:
            model.Add(sustain_sum[k] == sum(coef * var for coef, var in sus_terms))
        else:
            model.Add(sustain_sum[k] == 0)

    # Auto mode (Soft-Only): saturation, duplicate penalties, diversity rewards
    t = req.targets
    w = req.weights

    def iw(v: float) -> int:
        return int(round(v * 1000))

    # 1) Saturation caps per boon per group
    boon_caps = {
        "quickness": int(round(t.quickness_uptime * 1000)),
        "alacrity": int(round(t.alacrity_uptime * 1000)),
        "stability": int(round(0.5 * 1000)),  # approx one reliable source
        "resistance": int(round(t.resistance_uptime * 1000)),
        "protection": int(round(t.protection_uptime * 1000)),
        "fury": int(round(t.fury_uptime * 1000)),
    }

    c = {}
    for k in range(group_count):
        for boon, cap in boon_caps.items():
            # c[k,boon] <= u[k,boon] and <= cap; objective will push it to min(u, cap)
            c[(k, boon)] = model.NewIntVar(0, cap, f"c_{k}_{boon}")
            model.Add(c[(k, boon)] <= u[(k, boon)])
            model.Add(c[(k, boon)] <= cap)

    # 2) Group-level duplicate penalties and diversity rewards
    # Threshold: allow 1 of the same build per group before penalties
    group_dup_threshold = 1
    dup_penalty_group_w = iw(w.get("dup_penalty_group", 0.2))  # default mild penalty
    diversity_reward_w = iw(
        w.get("diversity_reward", 0.03)
    )  # small reward per unique spec

    # We need per-group per-build counts: s_kj in [0,5]
    s_kj = {}
    present = {}
    extra_group = {}

    for k in range(group_count):
        for j in range(len(builds)):
            # Count of build j in group k
            s_kj[(k, j)] = model.NewIntVar(0, 5, f"s_{k}_{j}")
            terms = []
            for i in range(n):
                if (i, j, k) in z:
                    terms.append(z[(i, j, k)])
            if terms:
                model.Add(s_kj[(k, j)] == sum(terms))
            else:
                model.Add(s_kj[(k, j)] == 0)

            # present[k,j] boolean if any of build j in group k
            present[(k, j)] = model.NewBoolVar(f"present_{k}_{j}")
            # Linking: s_kj >= present and s_kj <= 5*present
            model.Add(s_kj[(k, j)] >= present[(k, j)])
            model.Add(s_kj[(k, j)] <= 5 * present[(k, j)])

            # Extra duplicates beyond threshold (soft penalty)
            extra_group[(k, j)] = model.NewIntVar(0, 5, f"extra_{k}_{j}")
            # extra >= s_kj - threshold and >= 0
            model.Add(extra_group[(k, j)] >= s_kj[(k, j)] - group_dup_threshold)
            model.Add(extra_group[(k, j)] >= 0)

    # 3) Global duplicate penalties (soft)
    dup_penalty_global_w = iw(w.get("dup_penalty_global", 0.05))
    global_dup_threshold_per_build = max(1, group_count)  # ~one per group allowed
    extra_global = {}
    S_j = {}
    for j in range(len(builds)):
        # Total count of build j across squad
        S_j[j] = model.NewIntVar(0, n, f"S_{j}")
        x_terms = [x[(i, j)] for i in range(n) if (i, j) in x]
        if x_terms:
            model.Add(S_j[j] == sum(x_terms))
        else:
            model.Add(S_j[j] == 0)
        extra_global[j] = model.NewIntVar(0, n, f"extra_global_{j}")
        model.Add(extra_global[j] >= S_j[j] - global_dup_threshold_per_build)
        model.Add(extra_global[j] >= 0)

    # 4) Synergy pairs (soft bonus)
    # Map specialization names per build index
    spec_by_j = {j: builds[j].specialization.lower() for j in range(len(builds))}
    # Define synergy pairs by specialization (lowercase) with a multiplier
    spec_synergies = [
        ("firebrand", "scrapper", 1.0),
        ("firebrand", "herald", 0.6),
        ("scrapper", "tempest", 0.6),
        ("herald", "tempest", 0.4),
        ("scourge", "tempest", 0.4),
    ]
    # Build actual (j1,j2,mult) list from current builds
    synergy_pairs_j = []
    for a, b, mult in spec_synergies:
        js_a = [j for j, name in spec_by_j.items() if name == a]
        js_b = [j for j, name in spec_by_j.items() if name == b]
        for j1 in js_a:
            for j2 in js_b:
                if j1 != j2:
                    # keep (min,max) to avoid duplicates
                    jj = tuple(sorted((j1, j2)))
                    if all(jj != tuple(sorted((p[0], p[1]))) for p in synergy_pairs_j):
                        synergy_pairs_j.append((jj[0], jj[1], mult))

    synergy_w = iw(w.get("synergy", 0.05))
    pair_present = {}
    for k in range(group_count):
        for j1, j2, mult in synergy_pairs_j:
            var = model.NewBoolVar(f"syn_{k}_{j1}_{j2}")
            # var == 1 iff both present in group k
            model.Add(var <= present[(k, j1)])
            model.Add(var <= present[(k, j2)])
            model.Add(var >= present[(k, j1)] + present[(k, j2)] - 1)
            pair_present[(k, j1, j2)] = (var, mult)

    # 5) Build objective
    obj_terms = []

    for k in range(group_count):
        obj_terms.append(iw(w.get("quickness", 0.0)) * c[(k, "quickness")])
        obj_terms.append(iw(w.get("alacrity", 0.0)) * c[(k, "alacrity")])
        obj_terms.append(iw(w.get("stability", 0.0)) * c[(k, "stability")])
        obj_terms.append(iw(w.get("protection", 0.0)) * c[(k, "protection")])
        obj_terms.append(iw(w.get("fury", 0.0)) * c[(k, "fury")])
        obj_terms.append(iw(w.get("might", 0.0)) * might_sum[k])
        obj_terms.append(iw(w.get("dps", 0.0)) * dps_sum[k])
        obj_terms.append(iw(w.get("sustain", 0.0)) * sustain_sum[k])

        # Diversity reward: sum of present builds in the group
        obj_terms.append(
            diversity_reward_w * sum(present[(k, j)] for j in range(len(builds)))
        )

        # Group duplicate penalties
        obj_terms.append(
            -dup_penalty_group_w * sum(extra_group[(k, j)] for j in range(len(builds)))
        )

        # Synergy rewards
        if synergy_pairs_j:
            obj_terms.append(
                sum(
                    int(mult * synergy_w) * pair_present[(k, j1, j2)][0]
                    for (j1, j2, mult) in synergy_pairs_j
                )
            )

    # Global duplicate penalties
    obj_terms.append(
        -dup_penalty_global_w * sum(extra_global[j] for j in range(len(builds)))
    )

    model.Maximize(sum(obj_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(0.1, req.time_limit_ms / 1000.0)
    solver.parameters.num_search_workers = 8

    # Add streaming callback
    start_time = time.time()
    callback = StreamingSolutionCallback(
        on_solution=on_intermediate,
        x_vars=x,
        g_vars=g,
        players=players,
        builds=builds,
        group_count=group_count,
        start_time=start_time,
    )

    status = solver.Solve(model, callback)
    is_feasible = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    # Extract final solution
    groups: List[GroupAssignment] = []
    assign_build_index: List[int] = [-1] * n
    assign_group_index: List[int] = [-1] * n

    for i, p in enumerate(players):
        elig = [bid for bid in p.eligible_build_ids if bid in build_index]
        if not elig:
            elig = [builds[0].id]
        if is_feasible:
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
        else:
            # Fallback: first eligible build + round-robin groups respecting ≤5
            assign_build_index[i] = build_index[elig[0]]
            assign_group_index[i] = i % group_count

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
    if is_feasible:
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
                if (k, boon) in c:
                    cap = boon_caps.get(boon, 1000)
                    denom = float(cap) if cap > 0 else 1.0
                    val = solver.Value(c[(k, boon)]) / denom
                else:
                    # fallback to raw u if c not defined
                    val = solver.Value(u[(k, boon)]) / 1000.0 if (k, boon) in u else 0.0
                cov[boon] = max(0.0, min(1.0, val))
            coverage_by_group.append(cov)
    else:
        # Compute approximate coverage from assigned builds and caps matrix
        for k in range(group_count):
            cov = {}
            members = [idx for idx in range(n) if assign_group_index[idx] == k]
            for boon in [
                "quickness",
                "alacrity",
                "stability",
                "resistance",
                "protection",
                "fury",
            ]:
                idx_b = key_idx[boon]
                s = 0.0
                for i in members:
                    j = assign_build_index[i]
                    if 0 <= j < len(builds):
                        s += float(caps[j, idx_b])
                cap = boon_caps.get(boon, 1000) / 1000.0
                denom = cap if cap > 0 else 1.0
                cov[boon] = max(0.0, min(1.0, s / denom))
            coverage_by_group.append(cov)

    best_score = 0.0
    if is_feasible:
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
        diagnostics={"status": int(status), "solution_count": callback.solution_count},
    )
