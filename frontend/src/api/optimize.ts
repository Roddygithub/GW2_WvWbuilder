export type OptimizationPlayer = {
  id: number;
  name: string;
  eligible_build_ids: number[];
};

export type OptimizationBuild = {
  id: number;
  profession: string;
  specialization: string;
  mode: "wvw" | "pve";
};

export type OptimizationTargets = {
  quickness_uptime?: number;
  alacrity_uptime?: number;
  resistance_uptime?: number;
  protection_uptime?: number;
  stability_sources?: number;
};

export type OptimizationWeights = {
  quickness?: number;
  alacrity?: number;
  stability?: number;
  resistance?: number;
  protection?: number;
  might?: number;
  fury?: number;
  dps?: number;
  sustain?: number;
  // Soft-only parameters
  dup_penalty_group?: number;
  dup_penalty_global?: number;
  diversity_reward?: number;
  synergy?: number;
};

export type OptimizationRequest = {
  players: OptimizationPlayer[];
  builds: OptimizationBuild[];
  mode: "wvw";
  wvw_mode?: "zerg" | "havoc" | "roaming" | "defense" | "gank";
  squad_size: number;
  time_limit_ms?: number;
  targets?: OptimizationTargets;
  weights?: OptimizationWeights;
};

export type OptimizationGroup = {
  group_id: number;
  players: number[];
  builds: number[];
};

export type OptimizationResultPayload = {
  status: "running" | "complete" | "cancelled" | "timeout" | "error" | "queued";
  elapsed_ms: number;
  best_score: number;
  result?: {
    status: string;
    best_score: number;
    elapsed_ms: number;
    groups: OptimizationGroup[];
    coverage_by_group: Record<string, number>[];
    diagnostics: Record<string, unknown>;
  };
};

const API_BASE = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export async function startOptimize(req: OptimizationRequest): Promise<{ job_id: string }> {
  const res = await fetch(`${API_BASE}/api/v1/optimize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Failed to start optimization: ${res.status}`);
  return res.json();
}

export function streamOptimize(
  jobId: string,
  onMessage: (data: OptimizationResultPayload) => void,
): () => void {
  const es = new EventSource(`${API_BASE}/api/v1/optimize/stream/${jobId}`);
  es.onmessage = (ev) => {
    try {
      const payload = JSON.parse(ev.data) as OptimizationResultPayload;
      onMessage(payload);
    } catch (e) {
      // ignore invalid frames
    }
  };
  es.onerror = () => {
    // Let the UI handle a stopped stream
    es.close();
  };
  return () => es.close();
}
