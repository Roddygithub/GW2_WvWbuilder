/**
 * Activity Feed Component
 * Displays recent user activities
 */

import { Clock, FileText, Users, Tag } from 'lucide-react';

export interface Activity {
  id: string;
  type: 'composition' | 'build' | 'team' | 'tag';
  title: string;
  description: string;
  timestamp: string;
}

interface ActivityFeedProps {
  activities: Activity[];
  maxItems?: number;
}

const activityIcons = {
  composition: FileText,
  build: FileText,
  team: Users,
  tag: Tag,
};

const activityColors = {
  composition: 'bg-green-600',
  build: 'bg-blue-600',
  team: 'bg-purple-600',
  tag: 'bg-yellow-600',
};

export default function ActivityFeed({ activities, maxItems = 5 }: ActivityFeedProps) {
  const displayActivities = activities.slice(0, maxItems);

  if (displayActivities.length === 0) {
    return (
      <div className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
        <div className="text-center py-8">
          <Clock className="mx-auto h-12 w-12 text-gray-600" />
          <p className="mt-2 text-sm text-gray-400">No recent activity</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm">
      <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {displayActivities.map((activity) => {
          const Icon = activityIcons[activity.type];
          const colorClass = activityColors[activity.type];

          return (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className={`rounded-full ${colorClass} p-2 flex-shrink-0`}>
                <Icon className="h-4 w-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {activity.title}
                </p>
                <p className="text-sm text-gray-400 truncate">
                  {activity.description}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatTimestamp(activity.timestamp)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  
  return date.toLocaleDateString();
}
