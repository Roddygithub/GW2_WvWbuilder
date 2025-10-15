/**
 * Dashboard Hook
 * React Query hooks for dashboard data
 */

import { useQuery } from '@tanstack/react-query';
import { getDashboardStats, getRecentActivities, type DashboardStats, type RecentActivity } from '../api/dashboard';
import { getAuthToken } from '../api/client';

/**
 * Hook to fetch dashboard statistics
 */
export const useDashboardStats = () => {
  const isAuthenticated = !!getAuthToken();
  
  return useQuery<DashboardStats, Error>({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  });
};

/**
 * Hook to fetch recent activities
 */
export const useRecentActivities = (limit: number = 10) => {
  const isAuthenticated = !!getAuthToken();
  
  return useQuery<RecentActivity[], Error>({
    queryKey: ['recent-activities', limit],
    queryFn: () => getRecentActivities(limit),
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: 2,
  });
};
