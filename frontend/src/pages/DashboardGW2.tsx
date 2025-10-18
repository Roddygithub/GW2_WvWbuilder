/**
 * Dashboard Page - GW2 Theme
 * Main user dashboard with Guild Wars 2 aesthetic
 */

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "../store/authStore";
import { getDashboardStats, getRecentActivities } from "../api/dashboard";
import StatCard from "../components/StatCard";
import ActivityFeed, { Activity } from "../components/ActivityFeed";
import { FileText, Users, Layers, TrendingUp, LogOut, Shield, Sword } from "lucide-react";

export default function DashboardGW2() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, loadUser } = useAuthStore();
  const [activities, setActivities] = useState<Activity[]>([]);

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: getDashboardStats,
    enabled: isAuthenticated,
    retry: 1,
  });

  // Fetch recent activities
  const { data: recentActivities } = useQuery({
    queryKey: ["recent-activities"],
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
      navigate("/login");
      return;
    }

    if (!user) {
      loadUser();
    }
  }, [isAuthenticated, user, navigate, loadUser]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="gw2-card p-8">
          <div className="text-primary text-xl font-semibold">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gw2-fractal-bg gw2-tyria-pattern">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm shadow-lg">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Sword className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold">GW2 WvW Builder</h1>
                <p className="text-sm text-muted-foreground mt-1">
                  Welcome back, <span className="text-primary font-semibold">{user.username}</span>!
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="gw2-button-secondary flex items-center space-x-2 px-4 py-2"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Welcome Banner */}
        <div className="gw2-card gw2-gold-glow p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">
                Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}, {user.username}!
              </h2>
              <p className="text-muted-foreground">Ready to lead your squad to victory in the Mists</p>
            </div>
            <Shield className="h-16 w-16 text-primary opacity-30" />
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Overview</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="gw2-card p-6 hover:gw2-gold-glow transition-all">
              <div className="flex items-center justify-between mb-4">
                <Layers className="h-8 w-8 text-primary" />
                <div className="text-right">
                  <p className="text-3xl font-bold text-primary">
                    {statsLoading ? "..." : stats?.total_compositions || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Compositions</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">Total created</p>
            </div>

            <div className="gw2-card p-6 hover:gw2-gold-glow transition-all">
              <div className="flex items-center justify-between mb-4">
                <FileText className="h-8 w-8 text-primary" />
                <div className="text-right">
                  <p className="text-3xl font-bold text-primary">
                    {statsLoading ? "..." : stats?.total_builds || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Builds</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">Total created</p>
            </div>

            <div className="gw2-card p-6 hover:gw2-gold-glow transition-all">
              <div className="flex items-center justify-between mb-4">
                <Users className="h-8 w-8 text-primary" />
                <div className="text-right">
                  <p className="text-3xl font-bold text-primary">
                    {statsLoading ? "..." : stats?.total_teams || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Teams</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">Total managed</p>
            </div>

            <div className="gw2-card p-6 hover:gw2-gold-glow transition-all">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="h-8 w-8 text-primary" />
                <div className="text-right">
                  <p className="text-3xl font-bold text-primary">
                    {statsLoading ? "..." : stats?.recent_activity_count || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Activity</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">Last 30 days</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              to="/compositions/new"
              className="gw2-card p-6 hover:gw2-gold-glow transition-all group"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-primary/20 p-4 group-hover:bg-primary/30 transition-colors">
                  <Layers className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">Create Composition</h3>
                  <p className="text-sm text-muted-foreground">
                    Build a new squad composition
                  </p>
                </div>
              </div>
            </Link>

            <Link
              to="/optimizer"
              className="gw2-card p-6 hover:gw2-gold-glow transition-all group"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-primary/20 p-4 group-hover:bg-primary/30 transition-colors">
                  <Sword className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">Squad Optimizer</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-powered composition builder
                  </p>
                </div>
              </div>
            </Link>

            <Link
              to="/activity"
              className="gw2-card p-6 hover:gw2-gold-glow transition-all group"
            >
              <div className="flex items-center space-x-4">
                <div className="rounded-full bg-primary/20 p-4 group-hover:bg-primary/30 transition-colors">
                  <TrendingUp className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">View Activity</h3>
                  <p className="text-sm text-muted-foreground">
                    See all your recent actions
                  </p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Activity Chart Section */}
          <div className="gw2-card p-6">
            <h2 className="text-xl font-bold mb-4">Activity Overview</h2>
            <p className="text-sm text-muted-foreground mb-4">Last 7 days</p>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Compositions</span>
                <div className="flex-1 mx-4 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-2/3"></div>
                </div>
                <span className="text-sm font-semibold text-primary">66%</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Builds</span>
                <div className="flex-1 mx-4 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-1/2"></div>
                </div>
                <span className="text-sm font-semibold text-primary">50%</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Teams</span>
                <div className="flex-1 mx-4 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-1/3"></div>
                </div>
                <span className="text-sm font-semibold text-primary">33%</span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <h3 className="text-lg font-bold mb-2">Recent Activity</h3>
              {activities.length > 0 ? (
                <ActivityFeed activities={activities} maxItems={3} />
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground text-sm">No recent activity</p>
                  <p className="text-muted-foreground text-xs mt-1">
                    Start creating compositions to see your activity here
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* System Status */}
          <div className="gw2-card p-6">
            <h2 className="text-xl font-bold mb-6">System Status</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-medium">Backend API</span>
                <span className="text-sm text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-400 mr-2"></span>
                  Operational
                </span>
              </div>
              
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-medium">Authentication</span>
                <span className="text-sm text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-400 mr-2"></span>
                  Operational
                </span>
              </div>
              
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-medium">Dashboard API</span>
                <span className="text-sm text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-400 mr-2"></span>
                  Operational
                </span>
              </div>
              
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-medium">Tags API</span>
                <span className="text-sm text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-400 mr-2"></span>
                  Operational
                </span>
              </div>
              
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-medium">Builds API</span>
                <span className="text-sm text-yellow-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-yellow-400 mr-2"></span>
                  In Development
                </span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-primary">99.9%</p>
                  <p className="text-xs text-muted-foreground mt-1">Uptime</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-primary">{user ? "1" : "0"}</p>
                  <p className="text-xs text-muted-foreground mt-1">Active Sessions</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-muted-foreground">
          <p>Powered by GW2 WvW Builder</p>
          <p className="mt-1">© 2025 All rights reserved</p>
        </div>
      </main>
    </div>
  );
}
