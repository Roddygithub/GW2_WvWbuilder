/**
 * BackupStatusBar Component
 * Visual indicator for backup status with manual trigger
 */

import { motion } from 'framer-motion';
import { Database, RefreshCw, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface BackupStatusBarProps {
  lastBackupTime?: Date;
  isBackingUp?: boolean;
  hasError?: boolean;
  onManualBackup?: () => void;
  className?: string;
}

export default function BackupStatusBar({
  lastBackupTime,
  isBackingUp = false,
  hasError = false,
  onManualBackup,
  className,
}: BackupStatusBarProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getTimeAgo = (date?: Date) => {
    if (!date) return 'Never';
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const handleManualBackup = () => {
    if (onManualBackup && !isBackingUp) {
      onManualBackup();
      toast.info('Backup started...');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'flex items-center justify-between px-4 py-3 rounded-lg backdrop-blur-sm border transition-all duration-300',
        hasError
          ? 'bg-red-500/10 border-red-500/30'
          : isBackingUp
          ? 'bg-blue-500/10 border-blue-500/30'
          : 'bg-slate-800/40 border-purple-500/20 hover:border-purple-500/40',
        className
      )}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      {/* Status Icon & Info */}
      <div className="flex items-center space-x-3">
        <motion.div
          animate={isBackingUp ? { rotate: 360 } : {}}
          transition={{ duration: 1, repeat: isBackingUp ? Infinity : 0, ease: 'linear' }}
          className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center',
            hasError
              ? 'bg-red-500/20 border border-red-500/40'
              : isBackingUp
              ? 'bg-blue-500/20 border border-blue-500/40'
              : 'bg-purple-500/20 border border-purple-500/40'
          )}
        >
          {hasError ? (
            <AlertCircle className="w-5 h-5 text-red-400" />
          ) : isBackingUp ? (
            <RefreshCw className="w-5 h-5 text-blue-400" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-purple-400" />
          )}
        </motion.div>

        <div>
          <p className="text-sm font-medium text-slate-200">
            {hasError ? 'Backup Failed' : isBackingUp ? 'Backup in Progress' : 'Backup Status'}
          </p>
          <div className="flex items-center space-x-2 mt-0.5">
            <Clock className="w-3 h-3 text-slate-400" />
            <p className="text-xs text-slate-400">
              Last backup: {getTimeAgo(lastBackupTime)}
            </p>
          </div>
        </div>
      </div>

      {/* Manual Backup Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleManualBackup}
        disabled={isBackingUp}
        className={cn(
          'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300',
          isBackingUp
            ? 'bg-slate-700/50 text-slate-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-500/20 to-violet-500/20 hover:from-purple-500/30 hover:to-violet-500/30 text-purple-300 border border-purple-500/30'
        )}
      >
        <Database className="w-4 h-4" />
        <span>{isBackingUp ? 'Backing up...' : 'Backup Now'}</span>
      </motion.button>

      {/* Progress Bar */}
      {isBackingUp && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-b-lg"
          style={{ transformOrigin: 'left' }}
        />
      )}

      {/* Glow Effect on Hover */}
      {isHovered && !isBackingUp && !hasError && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.3 }}
          className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500/20 to-violet-500/20 blur-xl"
        />
      )}
    </motion.div>
  );
}
