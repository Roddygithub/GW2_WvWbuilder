/**
 * Dashboard Page
 * Main user dashboard after login
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { getDashboardStats, getRecentActivities } from '../api/dashboard';
import StatCard from '../components/StatCard';
import ActivityFeed, { Activity } from '../components/ActivityFeed';
import { FileText, Users, Layers, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, loadUser } = useAuthStore();
  const [activities, setActivities] = useState<Activity[]>([]);

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    enabled: isAuthenticated,
    retry: 1,
  });

  // Fetch recent activities
  const { data: recentActivities } = useQuery({
    queryKey: ['recent-activities'],
    queryFn: () => getRecentActivities(10),
    enabled: isAuthenticated,
    retry: 1,
  });

  useEffect(() => {
    if (recentActivities) {
      setActivities(recentActivities);
    }
  }, [recentActivities]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Load user data if not already loaded
    if (!user) {
      loadUser();
    }
  }, [isAuthenticated, user, navigate, loadUser]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-gray-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">GW2 WvW Builder</h1>
              <p className="text-sm text-gray-400">Welcome back, {user.username}!</p>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Statistics Cards */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Overview</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Compositions"
              value={statsLoading ? '...' : stats?.total_compositions || 0}
              icon={Layers}
              iconColor="bg-green-600"
              subtitle="Total created"
            />
            <StatCard
              title="Builds"
              value={statsLoading ? '...' : stats?.total_builds || 0}
              icon={FileText}
              iconColor="bg-blue-600"
              subtitle="Total created"
            />
            <StatCard
              title="Teams"
              value={statsLoading ? '...' : stats?.total_teams || 0}
              icon={Users}
              iconColor="bg-purple-600"
              subtitle="Total managed"
            />
            <StatCard
              title="Recent Activity"
              value={statsLoading ? '...' : stats?.recent_activity_count || 0}
              icon={TrendingUp}
              iconColor="bg-yellow-600"
              subtitle="Last 30 days"
            />
          </div>
        </div>

        {/* User Info Card */}
        <div className="mb-8 rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm">
          <h2 className="text-xl font-semibold text-white mb-4">Account Information</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-gray-400">Username</p>
              <p className="text-white">{user.username}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Email</p>
              <p className="text-white">{user.email}</p>
            </div>
            {user.full_name && (
              <div>
                <p className="text-sm text-gray-400">Full Name</p>
                <p className="text-white">{user.full_name}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-400">Account Status</p>
              <p className="text-white">
                {user.is_active ? (
                  <span className="text-green-400">Active</span>
                ) : (
                  <span className="text-red-400">Inactive</span>
                )}
                {user.is_superuser && (
                  <span className="ml-2 text-purple-400">(Admin)</span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {/* Tags Manager */}
            <Link
              to="/tags"
              className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-purple-600 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Manage Tags</h3>
                  <p className="text-sm text-gray-400">Create and organize tags</p>
                </div>
              </div>
            </Link>

            {/* Squad Builder */}
            <Link
              to="/builder"
              className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-blue-600 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Squad Builder</h3>
                  <p className="text-sm text-gray-400">Build your WvW composition</p>
                </div>
              </div>
            </Link>

            {/* Compositions */}
            <Link
              to="/compositions"
              className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-green-600 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Compositions</h3>
                  <p className="text-sm text-gray-400">View saved compositions</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Two Column Layout for Activity and Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <ActivityFeed activities={activities} maxItems={5} />

          {/* System Status */}
          <div className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm">
            <h2 className="text-xl font-semibold text-white mb-4">System Status</h2>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Backend API</span>
                <span className="text-green-400">● Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Authentication</span>
                <span className="text-green-400">● Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Dashboard API</span>
                <span className="text-green-400">● Available</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Tags API</span>
                <span className="text-green-400">● Available</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Builds API</span>
                <span className="text-yellow-400">● Limited (In Development)</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
