/**
 * GW2 Themed Card Component
 * Enhanced card with GW2 styling and animations
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { cardHover } from '@/lib/animations';

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
  return (
    <motion.div
      className={cn(
        'relative rounded-lg border backdrop-blur-sm',
        'bg-gradient-to-br from-gw2-fractal-dark/90 to-gw2-fractal/80',
        'border-gw2-gold/20',
        glowing && 'shadow-[0_0_20px_rgba(255,193,7,0.3)]',
        onClick && 'cursor-pointer',
        className
      )}
      variants={hoverable ? cardHover : undefined}
      initial="rest"
      whileHover="hover"
      whileTap={onClick ? "tap" : undefined}
      onClick={onClick}
    >
      {/* Gold accent line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-gw2-gold to-transparent opacity-50" />
      
      {/* Content */}
      <div className="relative z-10 p-6">
        {children}
      </div>
      
      {/* Bottom accent */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-gw2-gold/30 to-transparent" />
    </motion.div>
  );
};

export default GW2Card;
