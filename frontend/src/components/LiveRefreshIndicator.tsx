/**
 * LiveRefreshIndicator Component
 * Shows live refresh status with toggle control
 */

import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Clock, Wifi, WifiOff } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface LiveRefreshIndicatorProps {
  isRefreshing: boolean;
  lastRefresh: Date;
  enabled: boolean;
  onToggle: () => void;
  onManualRefresh: () => void;
}

export default function LiveRefreshIndicator({
  isRefreshing,
  lastRefresh,
  enabled,
  onToggle,
  onManualRefresh,
}: LiveRefreshIndicatorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-800/60 backdrop-blur-sm border border-slate-700/50"
    >
      {/* Live Status Indicator */}
      <div className="flex items-center gap-2">
        <motion.div
          animate={{
            scale: enabled ? [1, 1.2, 1] : 1,
            opacity: enabled ? [0.5, 1, 0.5] : 0.3,
          }}
          transition={{
            duration: 2,
            repeat: enabled ? Infinity : 0,
            ease: 'easeInOut',
          }}
          className={`w-2 h-2 rounded-full ${
            enabled
              ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
              : 'bg-slate-500'
          }`}
        />
        <span className="text-xs font-medium text-slate-300">
          {enabled ? 'Live' : 'Paused'}
        </span>
      </div>

      {/* Last Refresh Time */}
      <div className="flex items-center gap-1.5 text-xs text-slate-400">
        <Clock className="w-3.5 h-3.5" />
        <span>
          {formatDistanceToNow(lastRefresh, { addSuffix: true })}
        </span>
      </div>

      {/* Divider */}
      <div className="w-px h-4 bg-slate-700" />

      {/* Manual Refresh Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={onManualRefresh}
        disabled={isRefreshing}
        className={`
          p-1.5 rounded-lg transition-all duration-200
          ${
            isRefreshing
              ? 'bg-slate-700/50 cursor-not-allowed'
              : 'bg-slate-700/50 hover:bg-purple-500/20 hover:border-purple-500/30'
          }
        `}
        title="Refresh now"
      >
        <RefreshCw
          className={`w-4 h-4 text-slate-300 ${
            isRefreshing ? 'animate-spin' : ''
          }`}
        />
      </motion.button>

      {/* Toggle Live Refresh */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={onToggle}
        className={`
          p-1.5 rounded-lg transition-all duration-200
          ${
            enabled
              ? 'bg-emerald-500/20 border border-emerald-500/30'
              : 'bg-slate-700/50 hover:bg-slate-600/50'
          }
        `}
        title={enabled ? 'Disable live refresh' : 'Enable live refresh'}
      >
        {enabled ? (
          <Wifi className="w-4 h-4 text-emerald-400" />
        ) : (
          <WifiOff className="w-4 h-4 text-slate-400" />
        )}
      </motion.button>

      {/* Refresh Animation Overlay */}
      <AnimatePresence>
        {isRefreshing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-purple-500/5 rounded-xl pointer-events-none"
          >
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="h-full w-1/3 bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
