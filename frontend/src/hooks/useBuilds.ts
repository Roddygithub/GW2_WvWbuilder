/**
 * Builds Hook
 * React Query hooks for character builds CRUD
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getBuilds,
  getBuildById,
  createBuild,
  updateBuild,
  deleteBuild,
  type Build,
  type CreateBuildPayload,
  type UpdateBuildPayload,
} from "../api/builds";
import { toast } from "sonner";

/**
 * Hook to fetch all builds
 */
export const useBuilds = () => {
  return useQuery<Build[], Error>({
    queryKey: ["builds"],
    queryFn: getBuilds,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Hook to fetch single build by ID
 */
export const useBuild = (id: string | number | undefined) => {
  return useQuery<Build, Error>({
    queryKey: ["build", id],
    queryFn: () => getBuildById(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Hook to create a new build
 */
export const useCreateBuild = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateBuildPayload) => createBuild(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["builds"] });
      toast.success("Build créé avec succès!");
    },
    onError: (error: any) => {
      toast.error(error.detail || "Erreur lors de la création");
    },
  });
};

/**
 * Hook to update an existing build
 */
export const useUpdateBuild = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number | string;
      data: UpdateBuildPayload;
    }) => updateBuild(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["builds"] });
      queryClient.invalidateQueries({ queryKey: ["build", variables.id] });
      toast.success("Build mis à jour!");
    },
    onError: (error: any) => {
      toast.error(error.detail || "Erreur lors de la mise à jour");
    },
  });
};

/**
 * Hook to delete a build
 */
export const useDeleteBuild = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number | string) => deleteBuild(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["builds"] });
      toast.success("Build supprimé");
    },
    onError: (error: any) => {
      toast.error(error.detail || "Erreur lors de la suppression");
    },
  });
};
