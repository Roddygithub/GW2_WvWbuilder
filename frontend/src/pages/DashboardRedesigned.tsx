/**
 * Dashboard Redesigned - GW2 Immersive Experience
 * Complete dashboard with sidebar, header, stats, charts, and activity feed
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast, Toaster } from 'sonner';
import { useAuthStore } from '../store/authStore';
import { getDashboardStats, getRecentActivities } from '../api/dashboard';
import { Activity } from '../components/ActivityFeedRedesigned';
import { useLiveRefresh } from '../hooks/useLiveRefresh';
import { isAuthenticated as tokenAuthenticated } from '../api/auth';

// Components
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import StatCardRedesigned from '../components/StatCardRedesigned';
import ActivityChart from '../components/ActivityChart';
import ActivityFeedRedesigned from '../components/ActivityFeedRedesigned';
import QuickActions from '../components/QuickActions';
import LiveRefreshIndicator from '../components/LiveRefreshIndicator';

// Icons
import { Layers, FileText, Users, TrendingUp } from 'lucide-react';

export default function DashboardRedesigned() {
  const navigate = useNavigate();
  const { user, isAuthenticated, loadUser } = useAuthStore();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [liveRefreshEnabled, setLiveRefreshEnabled] = useState(true);
  const isAuthed = isAuthenticated || tokenAuthenticated();

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    enabled: isAuthed,
    retry: 1,
  });

  // Fetch recent activities
  const { data: recentActivities } = useQuery({
    queryKey: ['recent-activities'],
    queryFn: () => getRecentActivities(10),
    enabled: isAuthed,
    retry: 1,
  });

  // Live refresh hook
  const { refresh, isRefreshing, lastRefresh } = useLiveRefresh({
    interval: 30000, // 30 seconds
    queryKeys: [['dashboard-stats'], ['recent-activities']],
    enabled: liveRefreshEnabled && isAuthed,
    showToast: false,
    onRefresh: () => {
      console.log('Dashboard data refreshed');
    },
  });

  useEffect(() => {
    if (!isAuthed) {
      navigate('/login');
      return;
    }

    if (!user) {
      loadUser();
    }
  }, [isAuthed, user, navigate, loadUser]);

  useEffect(() => {
    if (recentActivities) {
      setActivities(recentActivities);
    }
  }, [recentActivities]);

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-white text-center"
        >
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Loading your command center...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            color: '#e2e8f0',
          },
        }}
      />

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="ml-[280px] transition-all duration-300" data-testid="main-content">
        {/* Header with Live Refresh */}
        <div className="sticky top-0 z-10 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-md border-b border-slate-700/50">
          <div className="flex items-center justify-between px-8 py-4">
            <Header />
            <LiveRefreshIndicator
              isRefreshing={isRefreshing}
              lastRefresh={lastRefresh}
              enabled={liveRefreshEnabled}
              onToggle={() => {
                setLiveRefreshEnabled(!liveRefreshEnabled);
                toast.success(
                  liveRefreshEnabled ? 'Live refresh disabled' : 'Live refresh enabled',
                  { duration: 2000 }
                );
              }}
              onManualRefresh={() => {
                refresh();
                toast.info('Refreshing dashboard...', { duration: 1000 });
              }}
            />
          </div>
        </div>

        {/* Main Dashboard Content */}
        <main className="p-8 space-y-8" data-testid="dashboard-loaded">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCardRedesigned
              title="Compositions"
              value={statsLoading ? '...' : stats?.total_compositions || 0}
              icon={Layers}
              color="emerald"
              subtitle="Total created"
              delay={0}
            />
            <StatCardRedesigned
              title="Builds"
              value={statsLoading ? '...' : stats?.total_builds || 0}
              icon={FileText}
              color="blue"
              subtitle="Total created"
              delay={0.1}
            />
            <StatCardRedesigned
              title="Teams"
              value={statsLoading ? '...' : stats?.total_teams || 0}
              icon={Users}
              color="purple"
              subtitle="Total managed"
              delay={0.2}
            />
            <StatCardRedesigned
              title="Recent Activity"
              value={statsLoading ? '...' : stats?.recent_activity_count || 0}
              icon={TrendingUp}
              color="amber"
              subtitle="Last 30 days"
              delay={0.3}
            />
          </div>

          {/* Quick Actions */}
          <QuickActions />

          {/* Activity Chart */}
          <ActivityChart />

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Activity Feed */}
            <ActivityFeedRedesigned activities={activities} maxItems={5} />

            {/* System Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-sm border border-purple-500/20 p-6 shadow-[0_0_20px_rgba(168,85,247,0.2)]"
            >
              <h3 className="text-lg font-bold text-slate-100 mb-6">
                System Status
              </h3>
              <div className="space-y-4">
                {[
                  { label: 'Backend API', status: 'operational', color: 'emerald' },
                  { label: 'Authentication', status: 'operational', color: 'emerald' },
                  { label: 'Dashboard API', status: 'operational', color: 'emerald' },
                  { label: 'Tags API', status: 'operational', color: 'emerald' },
                  { label: 'Builds API', status: 'development', color: 'amber' },
                ].map((item, index) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + index * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300"
                  >
                    <span className="text-slate-300 text-sm">{item.label}</span>
                    <div className="flex items-center gap-2">
                      <motion.div
                        animate={{
                          scale: [1, 1.2, 1],
                          opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: 'easeInOut',
                        }}
                        className={`w-2 h-2 rounded-full ${
                          item.color === 'emerald'
                            ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                            : 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]'
                        }`}
                      />
                      <span
                        className={`text-xs font-medium ${
                          item.color === 'emerald'
                            ? 'text-emerald-400'
                            : 'text-amber-400'
                        }`}
                      >
                        {item.status === 'operational' ? 'Operational' : 'In Development'}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Stats Summary */}
              <div className="mt-6 pt-6 border-t border-slate-700/50">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-purple-400">99.9%</p>
                    <p className="text-xs text-slate-400 mt-1">Uptime</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-400">
                      {activities.length}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">Active Sessions</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="text-center text-sm text-slate-500 py-8"
          >
            <p>
              Powered by{' '}
              <span className="text-purple-400 font-semibold">GW2 WvW Builder</span>
            </p>
            <p className="mt-1">© 2025 All rights reserved</p>
          </motion.div>
        </main>
      </div>
    </div>
  );
}
