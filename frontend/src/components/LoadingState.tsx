/**
 * LoadingState Component
 * GW2-styled loading indicator with shimmer effect
 */

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface LoadingStateProps {
  message?: string;
  className?: string;
  fullScreen?: boolean;
}

export default function LoadingState({ 
  message = 'Loading...', 
  className,
  fullScreen = false 
}: LoadingStateProps) {
  const content = (
    <div className={cn(
      'flex flex-col items-center justify-center',
      fullScreen ? 'min-h-screen' : 'py-12',
      className
    )}>
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center space-y-4"
      >
        {/* Spinning Loader */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="relative"
        >
          <div className="w-16 h-16 rounded-full border-4 border-purple-500/20 border-t-purple-500 shadow-[0_0_30px_rgba(168,85,247,0.5)]" />
        </motion.div>

        {/* Loading Text */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-slate-300 text-lg font-medium"
        >
          {message}
        </motion.p>

        {/* Shimmer Dots */}
        <div className="flex space-x-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.2,
              }}
              className="w-2 h-2 bg-purple-400 rounded-full"
            />
          ))}
        </div>
      </motion.div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
        {content}
      </div>
    );
  }

  return content;
}
