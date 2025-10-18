/**
 * GW2Optimizer - Types TypeScript
 * Types pour le nouveau frontend GW2Optimizer
 */

// ============================================================================
// CHAT TYPES
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// SQUAD & BUILD TYPES
// ============================================================================

export interface BuildInfo {
  id: string;
  profession: string;
  specialization: string;
  role: string;
  count: number;
  weight: number;
}

export interface Squad {
  id: string;
  name: string;
  builds: BuildInfo[];
  weight: number;
  synergy: number;
  buffs: string[];
  nerfs: string[];
  timestamp: string;
  mode?: 'zerg' | 'havoc' | 'roaming' | 'defense' | 'gank';
  squad_size: number;
}

export interface SquadCompositionResponse {
  squads: Squad[];
  meta: {
    total_players: number;
    avg_weight: number;
    avg_synergy: number;
  };
}

// ============================================================================
// META EVOLUTION TYPES
// ============================================================================

export interface MetaDataPoint {
  timestamp: string;
  weights: Record<string, number>; // { "firebrand": 0.85, ... }
}

export interface MetaWeight {
  spec: string;
  weight: number;
  change?: number; // delta depuis dernier update
  trend?: 'up' | 'down' | 'stable';
}

export interface SynergyPair {
  spec1: string;
  spec2: string;
  score: number;
  category?: 'high' | 'medium' | 'low';
}

export interface PatchNote {
  date: string;
  spec: string;
  change_type: 'nerf' | 'buff' | 'rework';
  impact: string;
  magnitude?: string;
  source: 'gw2wiki' | 'forum' | 'reddit';
}

export interface MetaStats {
  total_specs: number;
  avg_weight: number;
  top_specs: MetaWeight[];
  bottom_specs: MetaWeight[];
  last_updated: string;
}

export interface HistoryEntry {
  timestamp: string;
  adjustments: Array<{
    spec: string;
    old_weight: number;
    new_weight: number;
    delta: number;
    change_type: 'nerf' | 'buff' | 'rework';
    reasoning: string;
  }>;
  source: 'patch_analysis' | 'manual_reset' | 'rollback';
}

// ============================================================================
// BUILD SELECTOR TYPES
// ============================================================================

export interface Build {
  id: string;
  profession: string;
  specialization: string;
  role: string;
  weight: number;
  synergy: 'high' | 'medium' | 'low';
  capabilities: {
    quickness?: number;
    alacrity?: number;
    stability?: number;
    resistance?: number;
    protection?: number;
    might?: number;
    fury?: number;
  };
  description?: string;
}

export interface BuildFilter {
  profession?: string;
  role?: string;
  minWeight?: number;
  synergy?: 'high' | 'medium' | 'low';
}

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

export interface CompositionRequest {
  prompt: string;
  squad_size: number;
  mode?: 'zerg' | 'havoc' | 'roaming' | 'defense' | 'gank';
  weights?: {
    quickness?: number;
    alacrity?: number;
    stability?: number;
    resistance?: number;
    protection?: number;
    might?: number;
    fury?: number;
    dps?: number;
    sustain?: number;
  };
}

export interface MetaEvolutionQuery {
  days?: number;
  specs?: string[];
  min_score?: number;
  limit?: number;
}

// ============================================================================
// UI STATE TYPES
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  progress?: number;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message: string;
  code?: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
}

// ============================================================================
// GRAPH/CHART TYPES
// ============================================================================

export interface ChartDataPoint {
  name: string;
  value: number;
  timestamp?: string;
}

export interface LineChartData {
  timestamp: string;
  [key: string]: number | string; // dynamic spec weights
}

export interface HeatmapCell {
  x: string;
  y: string;
  value: number;
  color?: string;
}

// ============================================================================
// PROFESSION/SPEC METADATA
// ============================================================================

export interface ProfessionMeta {
  name: string;
  icon: string;
  color: string;
  specializations: string[];
}

export const PROFESSIONS: Record<string, ProfessionMeta> = {
  guardian: {
    name: 'Guardian',
    icon: '🛡️',
    color: '#72C1D9',
    specializations: ['Dragonhunter', 'Firebrand', 'Willbender'],
  },
  warrior: {
    name: 'Warrior',
    icon: '⚔️',
    color: '#FFD166',
    specializations: ['Berserker', 'Spellbreaker', 'Bladesworn'],
  },
  engineer: {
    name: 'Engineer',
    icon: '🔧',
    color: '#D09C59',
    specializations: ['Scrapper', 'Holosmith', 'Mechanist'],
  },
  ranger: {
    name: 'Ranger',
    icon: '🏹',
    color: '#8CDC82',
    specializations: ['Druid', 'Soulbeast', 'Untamed'],
  },
  thief: {
    name: 'Thief',
    icon: '🗡️',
    color: '#C08F95',
    specializations: ['Daredevil', 'Deadeye', 'Specter'],
  },
  elementalist: {
    name: 'Elementalist',
    icon: '🔥',
    color: '#F68A87',
    specializations: ['Tempest', 'Weaver', 'Catalyst'],
  },
  mesmer: {
    name: 'Mesmer',
    icon: '🔮',
    color: '#B679D5',
    specializations: ['Chronomancer', 'Mirage', 'Virtuoso'],
  },
  necromancer: {
    name: 'Necromancer',
    icon: '💀',
    color: '#52A76F',
    specializations: ['Reaper', 'Scourge', 'Harbinger'],
  },
  revenant: {
    name: 'Revenant',
    icon: '⚡',
    color: '#D16E5A',
    specializations: ['Herald', 'Renegade', 'Vindicator'],
  },
};

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type WvWMode = 'zerg' | 'havoc' | 'roaming' | 'defense' | 'gank';

export type ChangeType = 'nerf' | 'buff' | 'rework';

export type SynergyLevel = 'high' | 'medium' | 'low';

export type MessageRole = 'user' | 'assistant';

// ============================================================================
// CONSTANTS
// ============================================================================

export const WVW_MODES = [
  { value: 'zerg', label: 'Zerg (25-50 players)', icon: '🏰' },
  { value: 'havoc', label: 'Havoc (10-20 players)', icon: '⚔️' },
  { value: 'roaming', label: 'Roaming (1-5 players)', icon: '🏃' },
  { value: 'defense', label: 'Defense', icon: '🛡️' },
  { value: 'gank', label: 'Gank', icon: '💥' },
] as const;

export const BADGE_COLORS = {
  nerf: '#f44336',
  buff: '#4caf50',
  rework: '#ff9800',
  high: '#4caf50',
  medium: '#ff9800',
  low: '#f44336',
} as const;
