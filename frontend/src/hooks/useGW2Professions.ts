/**
 * Hook for fetching GW2 professions from API
 */

import { useQuery } from "@tanstack/react-query";
import { getAllProfessionsDetails, checkGW2APIAvailability } from "../api/gw2";
import type { GW2Profession } from "../api/gw2";

/**
 * Hook to fetch all GW2 professions with details
 */
export const useGW2Professions = () => {
  return useQuery<GW2Profession[], Error>({
    queryKey: ["gw2-professions"],
    queryFn: getAllProfessionsDetails,
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60 * 24, // 24 hours (renamed from cacheTime in newer versions)
    retry: 2,
  });
};

/**
 * Hook to check if GW2 API is available
 */
export const useGW2APIStatus = () => {
  return useQuery<boolean, Error>({
    queryKey: ["gw2-api-status"],
    queryFn: checkGW2APIAvailability,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  });
};
