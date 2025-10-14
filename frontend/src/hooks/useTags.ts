/**
 * Tags Hook
 * React Query hooks for tags CRUD (admin functionality)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getTags,
  getTag,
  createTag,
  updateTag,
  deleteTag,
  type Tag,
  type CreateTagRequest,
  type UpdateTagRequest,
} from '../api/tags';
import { toast } from 'sonner';

/**
 * Hook to fetch all tags
 */
export const useTags = () => {
  return useQuery<Tag[], Error>({
    queryKey: ['tags'],
    queryFn: getTags,
    staleTime: 1000 * 60 * 10, // 10 minutes (tags don't change often)
  });
};

/**
 * Hook to fetch single tag by ID
 */
export const useTag = (id: number | undefined) => {
  return useQuery<Tag, Error>({
    queryKey: ['tag', id],
    queryFn: () => getTag(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 10,
  });
};

/**
 * Hook to create a new tag (admin only)
 */
export const useCreateTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateTagRequest) => createTag(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag créé avec succès!');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la création du tag');
    },
  });
};

/**
 * Hook to update an existing tag (admin only)
 */
export const useUpdateTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTagRequest }) =>
      updateTag(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      queryClient.invalidateQueries({ queryKey: ['tag', variables.id] });
      toast.success('Tag mis à jour!');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la mise à jour du tag');
    },
  });
};

/**
 * Hook to delete a tag (admin only)
 */
export const useDeleteTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteTag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag supprimé');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Erreur lors de la suppression du tag');
    },
  });
};
