/**
 * GW2 API Module
 * Handles communication with Guild Wars 2 API via backend proxy
 */

import { apiGet } from "./client";

// Types
export interface GW2Profession {
  id: string;
  name: string;
  icon: string;
  icon_big?: string;
  specializations: number[];
  weapons: Record<string, string>;
  training: any[];
  flags: string[];
  skills?: any[];
}

export interface GW2Specialization {
  id: number;
  name: string;
  profession: string;
  elite: boolean;
  minor_traits: number[];
  major_traits: number[];
  icon?: string;
  background?: string;
}

export interface GW2Skill {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  type?: string;
  weapon_type?: string;
  professions?: string[];
  slot?: string;
  facts?: any[];
  traited_facts?: any[];
}

export interface GW2Character {
  name: string;
  race: string;
  gender: string;
  profession: string;
  level: number;
  guild?: string;
  age: number;
  created: string;
  deaths: number;
  crafting: any[];
}

export interface GW2AccountInfo {
  id: string;
  age: number;
  name: string;
  world: number;
  guilds: string[];
  guild_leader: string[];
  created: string;
  access: string[];
  commander: boolean;
  fractal_level: number;
  daily_ap: number;
  monthly_ap: number;
  wvw_rank: number;
}

/**
 * Get list of all professions
 */
export const getProfessions = async (): Promise<string[]> => {
  return apiGet<string[]>("/gw2/professions");
};

/**
 * Get detailed information about a specific profession
 */
export const getProfessionDetails = async (
  professionId: string,
): Promise<GW2Profession> => {
  return apiGet<GW2Profession>(`/gw2/professions/${professionId}`);
};

/**
 * Get all professions with details
 */
export const getAllProfessionsDetails = async (): Promise<GW2Profession[]> => {
  const professionIds = await getProfessions();
  const professions = await Promise.all(
    professionIds.map((id) => getProfessionDetails(id)),
  );
  return professions;
};

/**
 * Get account information (requires GW2 API key)
 */
export const getAccountInfo = async (): Promise<GW2AccountInfo> => {
  return apiGet<GW2AccountInfo>("/gw2/account");
};

/**
 * Get list of characters (requires GW2 API key)
 */
export const getCharacters = async (): Promise<string[]> => {
  return apiGet<string[]>("/gw2/characters");
};

/**
 * Get detailed information about a character (requires GW2 API key)
 */
export const getCharacterDetails = async (
  characterName: string,
): Promise<GW2Character> => {
  return apiGet<GW2Character>(`/gw2/characters/${characterName}`);
};

/**
 * Get item information
 */
export const getItem = async (itemId: number): Promise<any> => {
  return apiGet<any>(`/gw2/items/${itemId}`);
};

/**
 * Check if GW2 API is available
 */
export const checkGW2APIAvailability = async (): Promise<boolean> => {
  try {
    await getProfessions();
    return true;
  } catch (error) {
    console.error("GW2 API not available:", error);
    return false;
  }
};

export default {
  getProfessions,
  getProfessionDetails,
  getAllProfessionsDetails,
  getAccountInfo,
  getCharacters,
  getCharacterDetails,
  getItem,
  checkGW2APIAvailability,
};
