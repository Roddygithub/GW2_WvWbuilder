import axios from "axios";
import type { Composition } from "@/types/squad"; // Corrected import

const apiClient = axios.create({
  baseURL: "/api", // Use relative path to leverage Vite proxy
});

export const getCompositions = async (): Promise<Composition[]> => {
  const response = await apiClient.get("/compositions/");
  return response.data;
};

export const getCompositionById = async (id: string): Promise<Composition> => {
  const response = await apiClient.get(`/compositions/${id}`);
  return response.data;
};

export interface CreateCompositionPayload {
  name: string;
  squad_size: number;
  playstyle: string;
  description?: string | null;
  professions: string[];
}

export const createComposition = async (payload: CreateCompositionPayload): Promise<Composition> => {
  const response = await apiClient.post("/compositions/", payload);
  return response.data;
};

export const updateComposition = async (id: number, payload: CreateCompositionPayload): Promise<Composition> => {
  const response = await apiClient.put(`/compositions/${id}`, payload);
  return response.data;
};

export const deleteComposition = async (id: number): Promise<void> => {
  await apiClient.delete(`/compositions/${id}`);
};