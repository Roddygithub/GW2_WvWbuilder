/**
 * ActivityFeed Redesigned - GW2 Themed with Advanced Animations
 * Immersive activity feed with smooth Framer Motion animations
 */

import { motion, AnimatePresence } from 'framer-motion';
import { Clock, FileText, Users, Tag, Layers } from 'lucide-react';

export interface Activity {
  id: string;
  type: 'composition' | 'build' | 'team' | 'tag';
  title: string;
  description: string;
  timestamp: string;
}

interface ActivityFeedRedesignedProps {
  activities: Activity[];
  maxItems?: number;
}

const activityConfig = {
  composition: {
    icon: Layers,
    gradient: 'from-emerald-500 to-emerald-600',
    glow: 'shadow-[0_0_10px_rgba(16,185,129,0.4)]',
    border: 'border-emerald-500/30',
  },
  build: {
    icon: FileText,
    gradient: 'from-blue-500 to-blue-600',
    glow: 'shadow-[0_0_10px_rgba(59,130,246,0.4)]',
    border: 'border-blue-500/30',
  },
  team: {
    icon: Users,
    gradient: 'from-purple-500 to-purple-600',
    glow: 'shadow-[0_0_10px_rgba(168,85,247,0.4)]',
    border: 'border-purple-500/30',
  },
  tag: {
    icon: Tag,
    gradient: 'from-amber-500 to-amber-600',
    glow: 'shadow-[0_0_10px_rgba(245,158,11,0.4)]',
    border: 'border-amber-500/30',
  },
};

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return date.toLocaleDateString();
}

export default function ActivityFeedRedesigned({
  activities,
  maxItems = 5,
}: ActivityFeedRedesignedProps) {
  const displayActivities = activities.slice(0, maxItems);

  return (
    <motion.div
      data-testid="activity-feed"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7, duration: 0.5 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-sm border border-purple-500/20 p-6 shadow-[0_0_20px_rgba(168,85,247,0.2)]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Clock className="w-5 h-5 text-purple-400" />
          Recent Activity
        </h3>
        <span className="text-xs text-slate-400 bg-slate-700/50 px-3 py-1 rounded-full">
          {displayActivities.length} events
        </span>
      </div>

      {/* Activity List */}
      {displayActivities.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Clock className="mx-auto h-16 w-16 text-slate-600 mb-4" />
          <p className="text-slate-400">No recent activity</p>
          <p className="text-sm text-slate-500 mt-2">
            Start creating compositions to see your activity here
          </p>
        </motion.div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {displayActivities.map((activity, index) => {
              const config = activityConfig[activity.type];
              const Icon = config.icon;

              return (
                <motion.div
                  data-testid="activity-item"
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1, duration: 0.3 }}
                  whileHover={{ scale: 1.02, x: 5 }}
                  className={`
                    flex items-start gap-4 p-4 rounded-xl
                    bg-slate-800/40 border ${config.border}
                    hover:bg-slate-800/60 hover:${config.glow}
                    transition-all duration-300 cursor-pointer
                    group
                  `}
                >
                  {/* Icon */}
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className={`
                      flex-shrink-0 w-12 h-12 rounded-lg
                      bg-gradient-to-br ${config.gradient}
                      flex items-center justify-center
                      ${config.glow}
                    `}
                  >
                    <Icon className="w-6 h-6 text-white" />
                  </motion.div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-200 group-hover:text-purple-200 transition-colors truncate">
                      {activity.title}
                    </p>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                      {activity.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Clock className="w-3 h-3 text-slate-500" />
                      <p className="text-xs text-slate-500">
                        {formatTimestamp(activity.timestamp)}
                      </p>
                    </div>
                  </div>

                  {/* Type Badge */}
                  <span className="flex-shrink-0 text-xs px-2 py-1 rounded-full bg-slate-700/50 text-slate-400 capitalize">
                    {activity.type}
                  </span>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      {/* View All Link */}
      {displayActivities.length > 0 && activities.length > maxItems && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-4 text-center"
        >
          <button className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors">
            View all {activities.length} activities →
          </button>
        </motion.div>
      )}
    </motion.div>
  );
}
