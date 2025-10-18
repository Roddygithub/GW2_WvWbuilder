from __future__ import annotations

import time
from typing import Any, Callable, Dict, List

from ortools.sat.python import cp_model


class StreamingSolutionCallback(cp_model.CpSolverSolutionCallback):
    """
    Callback to stream intermediate best solutions during CP-SAT search.

    Invoked by OR-Tools whenever a better feasible solution is found.
    """

    def __init__(
        self,
        on_solution: Callable[[Dict[str, Any]], None],
        x_vars: Dict,
        g_vars: Dict,
        players: List,
        builds: List,
        group_count: int,
        start_time: float,
    ):
        super().__init__()
        self.on_solution = on_solution
        self.x_vars = x_vars
        self.g_vars = g_vars
        self.players = players
        self.builds = builds
        self.group_count = group_count
        self.start_time = start_time
        self.solution_count = 0

    def on_solution_callback(self) -> None:
        """Called by OR-Tools when a new best solution is found."""
        self.solution_count += 1
        elapsed_ms = int((time.time() - self.start_time) * 1000)
        obj_val = self.ObjectiveValue()

        # Extract assignments
        n = len(self.players)
        assign_build = [-1] * n
        assign_group = [-1] * n

        for i in range(n):
            for (ii, j), var in self.x_vars.items():
                if ii == i and self.Value(var) == 1:
                    assign_build[i] = j
                    break
            for (ii, k), var in self.g_vars.items():
                if ii == i and self.Value(var) == 1:
                    assign_group[i] = k
                    break

        # Build groups
        groups_data = []
        for k in range(self.group_count):
            player_ids = [self.players[i].id for i in range(n) if assign_group[i] == k]
            build_ids = [
                self.builds[assign_build[i]].id
                for i in range(n)
                if assign_group[i] == k
            ]
            groups_data.append(
                {"group_id": k + 1, "players": player_ids, "builds": build_ids}
            )

        # Normalize score (heuristic)
        denom = 1000.0 * self.group_count if self.group_count > 0 else 1.0
        best_score = max(0.0, min(1.0, obj_val / (denom * 10.0)))

        payload = {
            "status": "running",
            "elapsed_ms": elapsed_ms,
            "best_score": best_score,
            "solution_count": self.solution_count,
            "groups": groups_data,
        }
        self.on_solution(payload)
