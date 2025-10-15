/**
 * Builder Hook
 * React Query hooks for squad builder and optimizer
 */

import { useMutation, useQuery } from "@tanstack/react-query";
import {
  optimizeComposition,
  getGameModes,
  getAvailableRoles,
  type CompositionOptimizationRequest,
  type CompositionOptimizationResult,
} from "../api/builder";
import { toast } from "sonner";

/**
 * Hook to optimize squad composition
 */
export const useOptimizeComposition = () => {
  return useMutation({
    mutationFn: (request: CompositionOptimizationRequest) =>
      optimizeComposition(request),
    onSuccess: (data: CompositionOptimizationResult) => {
      toast.success(
        `Composition optimisée avec un score de ${(data.score * 100).toFixed(0)}%!`,
      );
    },
    onError: (error: any) => {
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Erreur lors de l'optimisation";
      toast.error(message);
    },
  });
};

/**
 * Hook to get available game modes
 */
export const useGameModes = () => {
  return useQuery({
    queryKey: ["builder", "modes"],
    queryFn: getGameModes,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get available roles
 */
export const useAvailableRoles = () => {
  return useQuery({
    queryKey: ["builder", "roles"],
    queryFn: getAvailableRoles,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Legacy export for backward compatibility
export const useOptimizeSquad = useOptimizeComposition;
