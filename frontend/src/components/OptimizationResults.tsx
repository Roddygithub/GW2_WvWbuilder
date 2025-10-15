/**
 * OptimizationResults Component
 * Displays synergies, suggestions, and squad analysis
 */

import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, CheckCircle2, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SynergyData {
  boons: Record<string, number>;
  healing: number;
  damage: number;
  survivability: number;
  crowdControl: number;
}

interface OptimizationResultsProps {
  synergy?: SynergyData;
  suggestions?: string[];
  warnings?: string[];
  score?: number;
  className?: string;
}

const boonColors: Record<string, string> = {
  might: '#FF6F00',
  fury: '#D32F2F',
  quickness: '#FFC107',
  alacrity: '#9C27B0',
  protection: '#2196F3',
  stability: '#607D8B',
  resolution: '#FFEB3B',
  resistance: '#FF5722',
};

export default function OptimizationResults({
  synergy,
  suggestions = [],
  warnings = [],
  score = 0,
  className,
}: OptimizationResultsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-yellow-500 to-amber-600';
    return 'from-red-500 to-orange-600';
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Score Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative rounded-xl p-6 bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-purple-500/30 overflow-hidden"
      >
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-slate-200 flex items-center space-x-2">
              <TrendingUp className="w-6 h-6 text-purple-400" />
              <span>Optimization Score</span>
            </h3>
            <div className={cn('text-4xl font-bold', getScoreColor(score))}>
              {score}/100
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="relative w-full h-3 bg-slate-700/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${score}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={cn(
                'h-full bg-gradient-to-r rounded-full shadow-lg',
                getScoreGradient(score)
              )}
            />
          </div>
        </div>

        {/* Background Glow */}
        <div 
          className="absolute inset-0 opacity-20 blur-3xl"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444'}, transparent 70%)`,
          }}
        />
      </motion.div>

      {/* Boons Coverage */}
      {synergy?.boons && Object.keys(synergy.boons).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-xl p-6 bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-purple-500/30"
        >
          <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center space-x-2">
            <Zap className="w-5 h-5 text-purple-400" />
            <span>Boon Coverage</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(synergy.boons).map(([boon, value]) => (
              <div key={boon} className="flex flex-col">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-300 capitalize">{boon}</span>
                  <span className="text-xs text-slate-400">{value}%</span>
                </div>
                <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="h-full rounded-full"
                    style={{ 
                      background: boonColors[boon] || '#A855F7',
                      boxShadow: `0 0 10px ${boonColors[boon] || '#A855F7'}40`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Stats */}
      {synergy && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {[
            { label: 'Damage', value: synergy.damage, color: 'text-red-400', bg: 'from-red-500/20 to-red-600/20' },
            { label: 'Healing', value: synergy.healing, color: 'text-green-400', bg: 'from-green-500/20 to-green-600/20' },
            { label: 'Survivability', value: synergy.survivability, color: 'text-blue-400', bg: 'from-blue-500/20 to-blue-600/20' },
            { label: 'Crowd Control', value: synergy.crowdControl, color: 'text-purple-400', bg: 'from-purple-500/20 to-purple-600/20' },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              className={cn(
                'rounded-xl p-4 bg-gradient-to-br border border-slate-700',
                stat.bg
              )}
            >
              <p className="text-xs text-slate-400 mb-1">{stat.label}</p>
              <p className={cn('text-2xl font-bold', stat.color)}>{stat.value}</p>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-xl p-6 bg-gradient-to-br from-green-500/10 to-emerald-600/10 border border-green-500/30"
        >
          <h3 className="text-lg font-bold text-green-300 mb-4 flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5" />
            <span>Suggestions</span>
          </h3>
          <ul className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.05 }}
                className="flex items-start space-x-3 text-sm text-slate-300"
              >
                <span className="text-green-400 mt-0.5">•</span>
                <span>{suggestion}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Warnings */}
      {warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl p-6 bg-gradient-to-br from-yellow-500/10 to-amber-600/10 border border-yellow-500/30"
        >
          <h3 className="text-lg font-bold text-yellow-300 mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5" />
            <span>Warnings</span>
          </h3>
          <ul className="space-y-2">
            {warnings.map((warning, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
                className="flex items-start space-x-3 text-sm text-slate-300"
              >
                <span className="text-yellow-400 mt-0.5">⚠</span>
                <span>{warning}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
}
