/**
 * QuickActions Component - GW2 Themed Action Buttons
 * Animated action buttons with glow effects
 */

import { motion } from 'framer-motion';
import { Plus, Layers, FileText, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface ActionButton {
  title: string;
  description: string;
  icon: React.ElementType;
  gradient: string;
  glow: string;
  path?: string;
  onClick?: () => void;
}

const actions: ActionButton[] = [
  {
    title: 'Create Composition',
    description: 'Build a new squad composition',
    icon: Layers,
    gradient: 'from-emerald-500 to-emerald-600',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.4)]',
    path: '/compositions/new',
  },
  {
    title: 'Create Build',
    description: 'Design a new character build',
    icon: FileText,
    gradient: 'from-blue-500 to-blue-600',
    glow: 'shadow-[0_0_20px_rgba(59,130,246,0.4)]',
    path: '/builder',
  },
  {
    title: 'View Activity',
    description: 'See all your recent actions',
    icon: Activity,
    gradient: 'from-purple-500 to-purple-600',
    glow: 'shadow-[0_0_20px_rgba(168,85,247,0.4)]',
    onClick: () => toast.info('Activity page coming soon!'),
  },
];

export default function QuickActions() {
  const navigate = useNavigate();

  const handleAction = (action: ActionButton) => {
    if (action.path) {
      navigate(action.path);
    } else if (action.onClick) {
      action.onClick();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="space-y-4"
    >
      <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
        <Plus className="w-5 h-5 text-purple-400" />
        Quick Actions
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {actions.map((action, index) => {
          const Icon = action.icon;

          return (
            <motion.button
              key={action.title}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + index * 0.1, duration: 0.3 }}
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleAction(action)}
              className={`
                relative overflow-hidden
                p-6 rounded-2xl
                bg-gradient-to-br from-slate-800/60 to-slate-900/60
                backdrop-blur-sm border border-purple-500/20
                hover:border-purple-400/40
                ${action.glow} hover:shadow-[0_0_30px_rgba(168,85,247,0.5)]
                transition-all duration-500
                group text-left
              `}
            >
              {/* Background Gradient on Hover */}
              <div
                className={`
                  absolute inset-0 opacity-0 group-hover:opacity-10
                  bg-gradient-to-br ${action.gradient}
                  transition-opacity duration-500
                `}
              />

              {/* Animated Border */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.3, 0.6, 0.3] }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: index * 0.2,
                }}
                className="absolute inset-0 border-2 border-purple-500/20 rounded-2xl"
              />

              <div className="relative">
                {/* Icon */}
                <motion.div
                  whileHover={{ rotate: 360, scale: 1.2 }}
                  transition={{ duration: 0.6 }}
                  className={`
                    inline-flex w-14 h-14 rounded-xl
                    bg-gradient-to-br ${action.gradient}
                    items-center justify-center
                    ${action.glow}
                    mb-4
                  `}
                >
                  <Icon className="w-7 h-7 text-white" />
                </motion.div>

                {/* Title */}
                <h4 className="text-base font-bold text-slate-100 group-hover:text-purple-200 transition-colors mb-2">
                  {action.title}
                </h4>

                {/* Description */}
                <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">
                  {action.description}
                </p>

                {/* Arrow Indicator */}
                <motion.div
                  initial={{ x: 0, opacity: 0 }}
                  whileHover={{ x: 5, opacity: 1 }}
                  className="absolute bottom-0 right-0 text-purple-400"
                >
                  →
                </motion.div>
              </div>

              {/* Decorative Particle */}
              <div
                className={`
                  absolute -top-10 -right-10 w-40 h-40
                  bg-gradient-to-br ${action.gradient} opacity-5
                  rounded-full blur-3xl
                  group-hover:scale-150 group-hover:opacity-10
                  transition-all duration-700
                `}
              />
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
