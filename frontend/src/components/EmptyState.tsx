/**
 * EmptyState Component
 * GW2-styled empty state with call-to-action
 */

import { motion } from 'framer-motion';
import { Plus, PackageOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ElementType;
  className?: string;
}

export default function EmptyState({
  title = 'No items found',
  message = 'Get started by creating your first item',
  actionLabel = 'Create New',
  onAction,
  icon: Icon = PackageOpen,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16', className)}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full text-center"
      >
        {/* Icon */}
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
          className="flex justify-center mb-6"
        >
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/20 to-violet-600/20 border border-purple-500/30 flex items-center justify-center backdrop-blur-sm">
            <Icon className="w-12 h-12 text-purple-400" />
          </div>
        </motion.div>

        {/* Title */}
        <motion.h3
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-2xl font-bold text-white mb-3"
        >
          {title}
        </motion.h3>

        {/* Message */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-slate-400 mb-8"
        >
          {message}
        </motion.p>

        {/* Action Button */}
        {onAction && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onAction}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-violet-600 hover:from-purple-600 hover:to-violet-700 rounded-lg text-white font-medium shadow-lg shadow-purple-500/30 transition-all duration-300"
          >
            <Plus className="w-5 h-5" />
            <span>{actionLabel}</span>
          </motion.button>
        )}
      </motion.div>
    </div>
  );
}
