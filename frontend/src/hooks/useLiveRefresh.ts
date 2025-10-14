/**
 * useLiveRefresh Hook
 * Automatically refreshes data at specified intervals
 */

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface UseLiveRefreshOptions {
  /**
   * Refresh interval in milliseconds
   * @default 30000 (30 seconds)
   */
  interval?: number;
  
  /**
   * Query keys to invalidate on refresh
   */
  queryKeys: string[][];
  
  /**
   * Enable/disable live refresh
   * @default true
   */
  enabled?: boolean;
  
  /**
   * Show toast notification on refresh
   * @default false
   */
  showToast?: boolean;
  
  /**
   * Callback when refresh occurs
   */
  onRefresh?: () => void;
}

export function useLiveRefresh({
  interval = 30000,
  queryKeys,
  enabled = true,
  showToast = false,
  onRefresh,
}: UseLiveRefreshOptions) {
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const refresh = async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    
    try {
      // Invalidate all specified query keys
      await Promise.all(
        queryKeys.map((key) =>
          queryClient.invalidateQueries({ queryKey: key })
        )
      );

      setLastRefresh(new Date());
      
      if (showToast) {
        toast.success('Dashboard refreshed', {
          description: 'Latest data loaded successfully',
          duration: 2000,
        });
      }

      onRefresh?.();
    } catch (error) {
      console.error('Failed to refresh data:', error);
      
      if (showToast) {
        toast.error('Refresh failed', {
          description: 'Could not load latest data',
          duration: 3000,
        });
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Set up interval
    intervalRef.current = setInterval(refresh, interval);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, interval, queryKeys]);

  return {
    refresh,
    isRefreshing,
    lastRefresh,
    enabled,
  };
}
