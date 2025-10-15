/**
 * Builds API Module
 * CRUD operations for character builds
 */

import { apiGet, apiPost, apiPut, apiDelete } from "./client";

export interface Build {
  id: number;
  name: string;
  profession: string;
  specialization?: string;
  role: string;
  description?: string;
  skills?: number[];
  traits?: number[];
  equipment?: any;
  user_id: number;
  is_public: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateBuildPayload {
  name: string;
  profession: string;
  specialization?: string;
  role: string;
  description?: string;
  skills?: number[];
  traits?: number[];
  equipment?: any;
  is_public?: boolean;
}

export interface UpdateBuildPayload extends Partial<CreateBuildPayload> {}

export const getBuilds = async (): Promise<Build[]> => {
  return apiGet<Build[]>("/builds");
};

export const getBuildById = async (id: string | number): Promise<Build> => {
  return apiGet<Build>(`/builds/${id}`);
};

export const createBuild = async (
  payload: CreateBuildPayload,
): Promise<Build> => {
  return apiPost<Build, CreateBuildPayload>("/builds", payload);
};

export const updateBuild = async (
  id: number | string,
  payload: UpdateBuildPayload,
): Promise<Build> => {
  return apiPut<Build, UpdateBuildPayload>(`/builds/${id}`, payload);
};

export const deleteBuild = async (id: number | string): Promise<void> => {
  return apiDelete<void>(`/builds/${id}`);
};
