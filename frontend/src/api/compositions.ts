/**
 * Compositions API Module
 * CRUD operations for squad compositions
 */

import { apiGet, apiPost, apiPut, apiDelete } from './client';
import type { Composition } from "@/types/squad";

export interface CreateCompositionPayload {
  name: string;
  squad_size: number;
  playstyle: string;
  description?: string | null;
  professions: string[];
  tags?: string[];
}

export interface UpdateCompositionPayload extends Partial<CreateCompositionPayload> {}

export const getCompositions = async (): Promise<Composition[]> => {
  return apiGet<Composition[]>('/compositions');
};

export const getCompositionById = async (id: string | number): Promise<Composition> => {
  return apiGet<Composition>(`/compositions/${id}`);
};

export const createComposition = async (payload: CreateCompositionPayload): Promise<Composition> => {
  return apiPost<Composition, CreateCompositionPayload>('/compositions', payload);
};

export const updateComposition = async (
  id: number | string, 
  payload: UpdateCompositionPayload
): Promise<Composition> => {
  return apiPut<Composition, UpdateCompositionPayload>(`/compositions/${id}`, payload);
};

export const deleteComposition = async (id: number | string): Promise<void> => {
  return apiDelete<void>(`/compositions/${id}`);
};