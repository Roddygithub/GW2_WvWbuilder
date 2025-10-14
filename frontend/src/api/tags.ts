/**
 * Tags API
 * Handles tag management (CRUD operations)
 * Status: Production-ready (78% tested)
 */

import { apiDelete, apiGet, apiPost, apiPut } from './client';

export interface Tag {
  id: number;
  name: string;
  description?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateTagRequest {
  name: string;
  description?: string;
  category?: string;
}

export interface UpdateTagRequest {
  name?: string;
  description?: string;
  category?: string;
}

/**
 * Get all tags
 */
export async function getTags(): Promise<Tag[]> {
  return apiGet<Tag[]>('/tags/');
}

/**
 * Get tag by ID
 */
export async function getTag(id: number): Promise<Tag> {
  return apiGet<Tag>(`/tags/${id}`);
}

/**
 * Create new tag (admin only)
 */
export async function createTag(data: CreateTagRequest): Promise<Tag> {
  return apiPost<Tag, CreateTagRequest>('/tags/', data);
}

/**
 * Update tag (admin only)
 */
export async function updateTag(id: number, data: UpdateTagRequest): Promise<Tag> {
  return apiPut<Tag, UpdateTagRequest>(`/tags/${id}`, data);
}

/**
 * Delete tag (admin only)
 * Note: Backend returns {msg} instead of {detail}
 */
export async function deleteTag(id: number): Promise<{ msg?: string; detail?: string }> {
  return apiDelete<{ msg?: string; detail?: string }>(`/tags/${id}`);
}

export default {
  getTags,
  getTag,
  createTag,
  updateTag,
  deleteTag,
};
