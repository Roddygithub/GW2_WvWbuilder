/**
 * Meta Evolution API Client — GW2_WvWBuilder v4.3
 * 
 * Client for accessing adaptive meta system data.
 */

import { apiClient } from './client';

export interface WeightInfo {
  spec: string;
  weight: number;
  last_updated?: string;
}

export interface SynergyInfo {
  spec1: string;
  spec2: string;
  score: number;
}

export interface Adjustment {
  spec: string;
  old_weight: number;
  new_weight: number;
  delta: number;
  change_type: string;
  reasoning: string;
}

export interface HistoryEntry {
  timestamp: string;
  adjustments: Adjustment[];
  source: string;
}

export interface PatchChange {
  date: string;
  spec: string;
  change_type: string;
  impact: string;
  magnitude?: string;
  source: string;
}

export interface MetaStats {
  total_specs: number;
  total_synergies: number;
  history_entries: number;
  last_update?: string;
  avg_weight: number;
  top_specs: WeightInfo[];
  bottom_specs: WeightInfo[];
}

/**
 * Get all current specialization weights
 */
export async function getWeights(): Promise<WeightInfo[]> {
  const response = await apiClient.get('/meta/weights');
  return response.data;
}

/**
 * Get weight for a specific specialization
 */
export async function getSpecWeight(spec: string): Promise<WeightInfo> {
  const response = await apiClient.get(`/meta/weights/${spec}`);
  return response.data;
}

/**
 * Get synergy matrix
 */
export async function getSynergies(minScore = 0.0, limit = 50): Promise<SynergyInfo[]> {
  const response = await apiClient.get('/meta/synergies', {
    params: { min_score: minScore, limit }
  });
  return response.data;
}

/**
 * Get weight adjustment history
 */
export async function getHistory(limit = 50): Promise<HistoryEntry[]> {
  const response = await apiClient.get('/meta/history', {
    params: { limit }
  });
  return response.data;
}

/**
 * Get meta evolution statistics
 */
export async function getStats(): Promise<MetaStats> {
  const response = await apiClient.get('/meta/stats');
  return response.data;
}

/**
 * Get recent patch changes
 */
export async function getRecentChanges(days = 30): Promise<PatchChange[]> {
  const response = await apiClient.get('/meta/changes/recent', {
    params: { days }
  });
  return response.data;
}

/**
 * Trigger manual patch scan (admin)
 */
export async function triggerScan(withLlm = false): Promise<{ status: string; message: string }> {
  const response = await apiClient.post('/meta/scan', { with_llm: withLlm });
  return response.data;
}

/**
 * Reset all weights to defaults (admin)
 */
export async function resetWeights(): Promise<{ status: string; message: string }> {
  const response = await apiClient.post('/meta/reset');
  return response.data;
}

/**
 * Rollback to a specific timestamp (admin)
 */
export async function rollbackToTimestamp(timestamp: string): Promise<{ status: string; message: string }> {
  const response = await apiClient.post(`/meta/rollback/${timestamp}`);
  return response.data;
}
