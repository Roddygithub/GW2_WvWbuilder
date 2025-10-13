/**
 * Dashboard API
 * Endpoints for dashboard statistics and data
 */

import { apiGet } from './client';

export interface DashboardStats {
  total_compositions: number;
  total_builds: number;
  total_teams: number;
  recent_activity_count: number;
}

export interface RecentActivity {
  id: string;
  type: 'composition' | 'build' | 'team' | 'tag';
  title: string;
  description: string;
  timestamp: string;
}

/**
 * Get dashboard statistics
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  return apiGet<DashboardStats>('/dashboard/stats');
}

/**
 * Get recent user activities
 */
export async function getRecentActivities(limit = 10): Promise<RecentActivity[]> {
  return apiGet<RecentActivity[]>(`/dashboard/activities?limit=${limit}`);
}

export default {
  getDashboardStats,
  getRecentActivities,
};
