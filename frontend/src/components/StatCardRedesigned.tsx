/**
 * StatCard Redesigned - GW2 Themed with Animations
 * Immersive stat cards with glow effects and animations
 */

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatCardRedesignedProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color: 'emerald' | 'blue' | 'purple' | 'amber';
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  delay?: number;
}

const colorConfig = {
  emerald: {
    gradient: 'from-emerald-500 to-emerald-600',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.4)]',
    glowHover: 'shadow-[0_0_30px_rgba(16,185,129,0.6)]',
    border: 'border-emerald-500/30',
    text: 'text-emerald-400',
  },
  blue: {
    gradient: 'from-blue-500 to-blue-600',
    glow: 'shadow-[0_0_20px_rgba(59,130,246,0.4)]',
    glowHover: 'shadow-[0_0_30px_rgba(59,130,246,0.6)]',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
  },
  purple: {
    gradient: 'from-purple-500 to-purple-600',
    glow: 'shadow-[0_0_20px_rgba(168,85,247,0.4)]',
    glowHover: 'shadow-[0_0_30px_rgba(168,85,247,0.6)]',
    border: 'border-purple-500/30',
    text: 'text-purple-400',
  },
  amber: {
    gradient: 'from-amber-500 to-amber-600',
    glow: 'shadow-[0_0_20px_rgba(245,158,11,0.4)]',
    glowHover: 'shadow-[0_0_30px_rgba(245,158,11,0.6)]',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
  },
};

export default function StatCardRedesigned({
  title,
  value,
  icon: Icon,
  color,
  subtitle,
  trend,
  delay = 0,
}: StatCardRedesignedProps) {
  const config = colorConfig[color];

  return (
    <motion.div
      data-testid="stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5, ease: 'easeOut' }}
      whileHover={{ scale: 1.05, y: -5 }}
      className={`
        relative overflow-hidden rounded-2xl
        bg-gradient-to-br from-slate-800/60 to-slate-900/60
        backdrop-blur-sm border ${config.border}
        ${config.glow} hover:${config.glowHover}
        transition-all duration-500 cursor-pointer
        group
      `}
    >
      {/* Background Glow Effect */}
      <div
        className={`
        absolute inset-0 opacity-0 group-hover:opacity-100
        bg-gradient-to-br ${config.gradient} opacity-5
        transition-opacity duration-500
      `}
      />

      {/* Animated Border Glow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        className={`absolute inset-0 border-2 ${config.border} rounded-2xl`}
      />

      <div className="relative p-6">
        <div className="flex items-start justify-between">
          {/* Icon */}
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
            className={`
              w-14 h-14 rounded-xl
              bg-gradient-to-br ${config.gradient}
              flex items-center justify-center
              ${config.glow}
              group-hover:scale-110 transition-transform duration-300
            `}
          >
            <Icon className="w-7 h-7 text-white" />
          </motion.div>

          {/* Trend Indicator */}
          {trend && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.3 }}
              className={`
                px-2 py-1 rounded-lg text-xs font-bold
                ${
                  trend.isPositive
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/20 text-red-400'
                }
              `}
            >
              {trend.isPositive ? '+' : ''}
              {trend.value}%
            </motion.div>
          )}
        </div>

        {/* Title */}
        <h3 className="mt-4 text-sm font-medium text-slate-400 uppercase tracking-wide">
          {title}
        </h3>

        {/* Value */}
        <motion.p
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: delay + 0.2, duration: 0.5 }}
          className={`mt-2 text-4xl font-bold ${config.text} group-hover:text-white transition-colors duration-300`}
        >
          {value}
        </motion.p>

        {/* Subtitle */}
        {subtitle && (
          <p className="mt-2 text-xs text-slate-500">{subtitle}</p>
        )}

        {/* Decorative Line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: delay + 0.4, duration: 0.6 }}
          className={`mt-4 h-1 rounded-full bg-gradient-to-r ${config.gradient} opacity-50 group-hover:opacity-100 transition-opacity duration-300`}
        />
      </div>

      {/* Particle Effect (optional decorative element) */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-gradient-to-br from-purple-500/10 to-transparent rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />
    </motion.div>
  );
}
