/**
 * Builder Hook
 * React Query hooks for squad builder and optimizer
 */

import { useMutation } from '@tanstack/react-query';
import {
  optimizeSquad,
  calculateSynergy,
  getProfessionRecommendations,
  type OptimizeSquadRequest,
  type CalculateSynergyRequest,
  type BuilderRole,
} from '../api/builder';
import { toast } from 'sonner';

/**
 * Hook to optimize squad composition
 */
export const useOptimizeSquad = () => {
  return useMutation({
    mutationFn: (request: OptimizeSquadRequest) => optimizeSquad(request),
    onSuccess: () => {
      toast.success('Squad optimisé avec succès!');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de l\'optimisation');
    },
  });
};

/**
 * Hook to calculate squad synergies
 */
export const useCalculateSynergy = () => {
  return useMutation({
    mutationFn: (request: CalculateSynergyRequest) => calculateSynergy(request),
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors du calcul des synergies');
    },
  });
};

/**
 * Hook to get profession recommendations
 */
export const useProfessionRecommendations = () => {
  return useMutation({
    mutationFn: ({ currentRoles, targetSize }: { currentRoles: BuilderRole[]; targetSize: number }) =>
      getProfessionRecommendations(currentRoles, targetSize),
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la récupération des recommandations');
    },
  });
};
