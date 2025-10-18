/**
 * GW2Optimizer - API Client
 * Client pour interagir avec le backend via Mistral 7B
 */

import { apiClient } from './client';
import {
  ChatMessage,
  CompositionRequest,
  SquadCompositionResponse,
  Squad,
} from '@/types/gw2optimizer';

/**
 * Génère une composition via chat avec Mistral 7B
 */
export async function generateComposition(
  prompt: string,
  squadSize: number = 15,
  mode?: 'zerg' | 'havoc' | 'roaming' | 'defense' | 'gank'
): Promise<SquadCompositionResponse> {
  const request: CompositionRequest = {
    prompt,
    squad_size: squadSize,
    mode,
  };

  const response = await apiClient.post<SquadCompositionResponse>(
    '/api/v1/compositions/generate',
    request
  );

  return response.data;
}

/**
 * Chat conversationnel avec Mistral (alternative)
 * Note: Endpoint à créer dans le backend si besoin
 */
export async function chatWithAI(
  message: string,
  conversationId?: string
): Promise<ChatMessage> {
  const response = await apiClient.post<ChatMessage>('/api/v1/chat', {
    message,
    conversation_id: conversationId,
  });

  return response.data;
}

/**
 * Récupère les compositions sauvegardées
 */
export async function getSavedCompositions(): Promise<Squad[]> {
  const response = await apiClient.get<Squad[]>('/api/v1/compositions');
  return response.data;
}

/**
 * Sauvegarde une composition
 */
export async function saveComposition(squad: Squad): Promise<Squad> {
  const response = await apiClient.post<Squad>('/api/v1/compositions', squad);
  return response.data;
}

/**
 * Supprime une composition
 */
export async function deleteComposition(squadId: string): Promise<void> {
  await apiClient.delete(`/api/v1/compositions/${squadId}`);
}

/**
 * Obtient des suggestions de builds basées sur le contexte
 */
export async function getBuildSuggestions(
  mode: string,
  currentBuilds: string[]
): Promise<Array<{ spec: string; reason: string; weight: number }>> {
  const response = await apiClient.post('/api/v1/builds/suggestions', {
    mode,
    current_builds: currentBuilds,
  });

  return response.data;
}

export default {
  generateComposition,
  chatWithAI,
  getSavedCompositions,
  saveComposition,
  deleteComposition,
  getBuildSuggestions,
};
