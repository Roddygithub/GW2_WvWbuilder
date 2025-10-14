/**
 * Squad Builder API Module
 * Operations for squad optimization and building
 */

import { apiPost } from './client';

export interface BuilderRole {
  profession: string;
  role: string;
  count: number;
  specialization?: string;
}

export interface OptimizeSquadRequest {
  squad_size: number;
  playstyle: string;
  roles?: BuilderRole[];
  priorities?: {
    boons?: string[];
    damage?: number;
    support?: number;
    survivability?: number;
  };
}

export interface OptimizeSquadResponse {
  optimized_composition: {
    roles: BuilderRole[];
    synergies: {
      boon_coverage: Record<string, number>;
      cleanses: number;
      cc: number;
    };
    score: number;
  };
  suggestions: string[];
  warnings?: string[];
}

export interface SquadSynergy {
  boons: Record<string, number>;
  healing: number;
  damage: number;
  survivability: number;
  crowd_control: number;
}

export interface CalculateSynergyRequest {
  roles: BuilderRole[];
}

/**
 * Optimize squad composition based on criteria
 */
export const optimizeSquad = async (request: OptimizeSquadRequest): Promise<OptimizeSquadResponse> => {
  return apiPost<OptimizeSquadResponse, OptimizeSquadRequest>('/builder/optimize', request);
};

/**
 * Calculate synergies for current squad composition
 */
export const calculateSynergy = async (request: CalculateSynergyRequest): Promise<SquadSynergy> => {
  return apiPost<SquadSynergy, CalculateSynergyRequest>('/builder/synergy', request);
};

/**
 * Get profession recommendations for squad
 */
export const getProfessionRecommendations = async (
  currentRoles: BuilderRole[],
  targetSize: number
): Promise<{ recommendations: BuilderRole[]; reasoning: string[] }> => {
  return apiPost('/builder/recommendations', {
    current_roles: currentRoles,
    target_size: targetSize,
  });
};
