import { create } from "zustand";

export type Player = {
  id: number;
  name: string;
  buildId: number;
  groupId: number;
};

export type Build = {
  id: number;
  profession: string;
  specialization: string;
  mode: "wvw" | "pve";
};

export type Group = {
  id: number;
  playerIds: number[];
  coverage: {
    quickness: number;
    alacrity: number;
    stability: number;
    resistance: number;
    protection: number;
    might: number;
    fury: number;
  };
};

export type OptimizeState = {
  jobId: string | null;
  status: "idle" | "queued" | "running" | "complete" | "error" | "cancelled";
  bestScore: number;
  elapsedMs: number;
  players: Player[];
  builds: Build[];
  groups: Group[];
  squadSize: number;
  
  // Actions
  setJobId: (jobId: string) => void;
  setStatus: (status: OptimizeState["status"]) => void;
  setBestScore: (score: number) => void;
  setElapsedMs: (ms: number) => void;
  initializePlayers: (count: number, builds: Build[]) => void;
  setBuilds: (builds: Build[]) => void;
  updateFromSSE: (payload: any) => void;
  movePlayer: (playerId: number, targetGroupId: number) => void;
  recalculateCoverage: () => void;
  reset: () => void;
};

// Compute capability vector for a build (simplified client-side heuristic)
function getCapabilities(build: Build): Group["coverage"] {
  const key = `${build.profession.toLowerCase()}:${build.specialization.toLowerCase()}`;
  const heuristics: Record<string, Partial<Group["coverage"]>> = {
    "guardian:firebrand": { quickness: 0.6, stability: 0.9, protection: 0.7, resistance: 0.4, might: 0.6, fury: 0.2, alacrity: 0.1 },
    "engineer:scrapper": { quickness: 0.3, stability: 0.85, protection: 0.5, resistance: 0.6, might: 0.4, fury: 0.2, alacrity: 0.1 },
    "revenant:herald": { quickness: 0.9, alacrity: 0.2, stability: 0.2, resistance: 0.5, protection: 0.8, might: 0.8, fury: 0.7 },
    "elementalist:tempest": { quickness: 0.1, alacrity: 0.1, stability: 0.2, resistance: 0.5, protection: 0.6, might: 0.3, fury: 0.2 },
    "necromancer:scourge": { quickness: 0.0, alacrity: 0.0, stability: 0.0, resistance: 0.6, protection: 0.3, might: 0.2, fury: 0.2 },
    "engineer:mechanist": { quickness: 0.1, alacrity: 0.3, stability: 0.1, resistance: 0.3, protection: 0.3, might: 0.9, fury: 0.3 },
  };
  
  const defaults = { quickness: 0.2, alacrity: 0.2, stability: 0.1, resistance: 0.2, protection: 0.2, might: 0.2, fury: 0.2 };
  return { ...defaults, ...(heuristics[key] || {}) };
}

export const useOptimizeStore = create<OptimizeState>((set, get) => ({
  jobId: null,
  status: "idle",
  bestScore: 0,
  elapsedMs: 0,
  players: [],
  builds: [],
  groups: [],
  squadSize: 15,

  setJobId: (jobId) => set({ jobId }),
  setStatus: (status) => set({ status }),
  setBestScore: (score) => set({ bestScore: score }),
  setElapsedMs: (ms) => set({ elapsedMs: ms }),

  initializePlayers: (count, builds) => {
    const players: Player[] = Array.from({ length: count }, (_, i) => ({
      id: i + 1,
      name: `Player${i + 1}`,
      buildId: builds[0]?.id || 101,
      groupId: Math.floor(i / 5) + 1,
    }));
    
    const groupCount = Math.ceil(count / 5);
    const groups: Group[] = Array.from({ length: groupCount }, (_, i) => ({
      id: i + 1,
      playerIds: players.filter(p => p.groupId === i + 1).map(p => p.id),
      coverage: { quickness: 0, alacrity: 0, stability: 0, resistance: 0, protection: 0, might: 0, fury: 0 },
    }));
    
    set({ players, groups, squadSize: count });
    get().recalculateCoverage();
  },

  setBuilds: (builds) => set({ builds }),

  updateFromSSE: (payload) => {
    const { status, best_score, elapsed_ms, result } = payload;
    
    if (status) set({ status });
    if (best_score !== undefined) set({ bestScore: best_score });
    if (elapsed_ms !== undefined) set({ elapsedMs: elapsed_ms });
    
    if (result?.groups) {
      const { players, builds } = get();
      const newPlayers = [...players];
      
      result.groups.forEach((g: any) => {
        g.players.forEach((pid: number, idx: number) => {
          const player = newPlayers.find(p => p.id === pid);
          if (player) {
            player.groupId = g.group_id;
            player.buildId = g.builds[idx] || player.buildId;
          }
        });
      });
      
      const groupCount = Math.max(...newPlayers.map(p => p.groupId));
      const newGroups: Group[] = Array.from({ length: groupCount }, (_, i) => ({
        id: i + 1,
        playerIds: newPlayers.filter(p => p.groupId === i + 1).map(p => p.id),
        coverage: result.coverage_by_group?.[i] || { quickness: 0, alacrity: 0, stability: 0, resistance: 0, protection: 0, might: 0, fury: 0 },
      }));
      
      set({ players: newPlayers, groups: newGroups });
    }
  },

  movePlayer: (playerId, targetGroupId) => {
    const { players, groups } = get();
    const newPlayers = players.map(p =>
      p.id === playerId ? { ...p, groupId: targetGroupId } : p
    );
    
    const newGroups = groups.map(g => ({
      ...g,
      playerIds: newPlayers.filter(p => p.groupId === g.id).map(p => p.id),
    }));
    
    set({ players: newPlayers, groups: newGroups });
    get().recalculateCoverage();
  },

  recalculateCoverage: () => {
    const { players, builds, groups } = get();
    
    const newGroups = groups.map(group => {
      const groupPlayers = players.filter(p => p.groupId === group.id);
      const coverage = { quickness: 0, alacrity: 0, stability: 0, resistance: 0, protection: 0, might: 0, fury: 0 };
      
      groupPlayers.forEach(player => {
        const build = builds.find(b => b.id === player.buildId);
        if (build) {
          const caps = getCapabilities(build);
          Object.keys(coverage).forEach(key => {
            coverage[key as keyof typeof coverage] = Math.min(1, coverage[key as keyof typeof coverage] + caps[key as keyof typeof caps]);
          });
        }
      });
      
      return { ...group, coverage };
    });
    
    set({ groups: newGroups });
  },

  reset: () => set({
    jobId: null,
    status: "idle",
    bestScore: 0,
    elapsedMs: 0,
    players: [],
    groups: [],
  }),
}));
