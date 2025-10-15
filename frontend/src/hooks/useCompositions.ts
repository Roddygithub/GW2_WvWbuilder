/**
 * Compositions Hook
 * React Query hooks for squad compositions CRUD
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCompositions,
  getCompositionById,
  createComposition,
  updateComposition,
  deleteComposition,
  type CreateCompositionPayload,
  type UpdateCompositionPayload,
} from '../api/compositions';
import type { Composition } from '../types/squad';
import { toast } from 'sonner';
import { getAuthToken } from '../api/client';

/**
 * Hook to fetch all compositions
 */
export const useCompositions = () => {
  const isAuthenticated = !!getAuthToken();
  
  return useQuery<Composition[], Error>({
    queryKey: ['compositions'],
    queryFn: getCompositions,
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to fetch single composition by ID
 */
export const useComposition = (id: string | number | undefined) => {
  return useQuery<Composition, Error>({
    queryKey: ['composition', id],
    queryFn: () => getCompositionById(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Hook to create a new composition
 */
export const useCreateComposition = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateCompositionPayload) => createComposition(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compositions'] });
      toast.success('Composition créée avec succès!');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la création');
    },
  });
};

/**
 * Hook to update an existing composition
 */
export const useUpdateComposition = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: UpdateCompositionPayload }) =>
      updateComposition(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['compositions'] });
      queryClient.invalidateQueries({ queryKey: ['composition', variables.id] });
      toast.success('Composition mise à jour!');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la mise à jour');
    },
  });
};

/**
 * Hook to delete a composition
 */
export const useDeleteComposition = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number | string) => deleteComposition(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compositions'] });
      toast.success('Composition supprimée');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la suppression');
    },
  });
};
