/**
 * GW2 Themed Card Component
 * Enhanced card with GW2 styling and animations
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GW2CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  glowing?: boolean;
}

export const GW2Card = ({ 
  children, 
  className, 
  onClick, 
  hoverable = true,
  glowing = false 
}: GW2CardProps) => {
  const hoverVariants = hoverable ? {
    scale: 1.02,
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 0 20px rgba(255, 193, 7, 0.3)',
  } : undefined;

  return (
    <motion.div
      className={cn(
        'relative rounded-lg border backdrop-blur-sm',
        'bg-gradient-to-br from-slate-900/90 to-slate-800/80',
        'border-purple-500/20',
        glowing && 'shadow-[0_0_20px_rgba(168,85,247,0.3)]',
        onClick && 'cursor-pointer',
        className
      )}
      whileHover={hoverVariants}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      onClick={onClick}
    >
      {/* Purple accent line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50" />
      
      {/* Content */}
      <div className="relative z-10 p-6">
        {children}
      </div>
      
      {/* Bottom accent */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />
    </motion.div>
  );
};

export default GW2Card;
