/**
 * Squad Builder API Module
 * Operations for squad optimization and building
 */

import { apiPost, apiGet } from "./client";

export interface BuilderRole {
  profession: string;
  role: string;
  count: number;
  specialization?: string;
}

export interface FixedRole {
  profession_id: number;
  elite_specialization_id?: number;
  count: number;
  role_type: string;
}

export interface CompositionOptimizationRequest {
  squad_size: number;
  game_type: string;
  game_mode: string;
  fixed_professions?: number[];
  preferred_roles?: Record<string, number>;
  min_boon_uptime?: Record<string, number>;
  min_healing?: number;
  min_damage?: number;
  min_cc?: number;
  min_cleanses?: number;
  excluded_elite_specializations?: number[];
  optimization_goals?: string[];
}

export interface CompositionMember {
  id: number;
  profession_name: string;
  elite_specialization_name?: string;
  role_type: string;
  is_commander: boolean;
  username: string;
  notes?: string;
  profession_id?: number;
  elite_specialization_id?: number;
}

export interface Composition {
  id: number;
  name: string;
  description?: string;
  squad_size: number;
  game_mode: string;
  is_public: boolean;
  tags?: any[];
  members?: CompositionMember[];
  created_by: number;
  created_at?: string;
  updated_at?: string;
}

export interface CompositionOptimizationResult {
  composition: Composition;
  score: number;
  metrics: Record<string, number>;
  role_distribution: Record<string, number>;
  boon_coverage: Record<string, number>;
  notes?: string[];
  subgroups?: Array<{
    group_number: number;
    size: number;
    members: number[];
    boon_coverage: Record<string, number>;
    avg_boon_coverage: number;
  }>;
}

export interface GameMode {
  id: string;
  name: string;
  description: string;
  squad_size_range: [number, number];
  emphasis: string[];
}

export interface Role {
  id: string;
  name: string;
  description: string;
}

/**
 * Optimize squad composition based on criteria
 */
export const optimizeComposition = async (
  request: CompositionOptimizationRequest,
): Promise<CompositionOptimizationResult> => {
  return apiPost<CompositionOptimizationResult, CompositionOptimizationRequest>(
    "/builder/optimize",
    request,
  );
};

/**
 * Get available game modes
 */
export const getGameModes = async (): Promise<{ modes: GameMode[] }> => {
  return apiGet<{ modes: GameMode[] }>("/builder/modes");
};

/**
 * Get available roles
 */
export const getAvailableRoles = async (): Promise<{ roles: Role[] }> => {
  return apiGet<{ roles: Role[] }>("/builder/roles");
};

// Legacy exports for backward compatibility
export type OptimizeSquadRequest = CompositionOptimizationRequest;
export type OptimizeSquadResponse = CompositionOptimizationResult;

export const optimizeSquad = optimizeComposition;
