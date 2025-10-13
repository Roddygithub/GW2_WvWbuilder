/**
 * Sidebar Component - GW2 Themed Navigation
 * Animated sidebar with navigation links
 */

import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Layers,
  FileText,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sword,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Compositions', path: '/compositions', icon: Layers },
  { name: 'Builds', path: '/builder', icon: FileText },
  { name: 'Teams', path: '/teams', icon: Users },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();

  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0, width: isCollapsed ? '80px' : '280px' }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen bg-gradient-to-b from-slate-950 via-purple-950 to-slate-950 border-r border-purple-500/20 backdrop-blur-md z-50"
    >
      {/* Logo Section */}
      <div className="flex items-center justify-between p-6 border-b border-purple-500/20">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-3"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-violet-600 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.5)]">
                <Sword className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-100 leading-tight">
                  GW2 WvW
                </h1>
                <p className="text-xs text-purple-300">Builder</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Collapse Button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 border border-purple-500/20 hover:border-purple-400/40 transition-all duration-300"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-purple-300" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-purple-300" />
          )}
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, x: 5 }}
                whileTap={{ scale: 0.98 }}
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-xl
                  transition-all duration-300 cursor-pointer
                  ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-500/20 to-violet-500/20 border border-purple-400/40 shadow-[0_0_15px_rgba(168,85,247,0.3)]'
                      : 'bg-slate-800/40 border border-transparent hover:border-purple-500/20 hover:bg-slate-800/60'
                  }
                `}
              >
                <div
                  className={`
                  flex items-center justify-center w-10 h-10 rounded-lg
                  ${
                    isActive
                      ? 'bg-gradient-to-br from-purple-500 to-violet-600 shadow-lg'
                      : 'bg-slate-700/50'
                  }
                `}
                >
                  <Icon
                    className={`w-5 h-5 ${
                      isActive ? 'text-white' : 'text-purple-300'
                    }`}
                  />
                </div>

                <AnimatePresence mode="wait">
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 0.2 }}
                      className={`font-medium ${
                        isActive ? 'text-purple-200' : 'text-slate-300'
                      }`}
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Active Indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-1.5 h-6 bg-gradient-to-b from-purple-400 to-violet-500 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.8)]"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-purple-500/20">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs text-slate-400 text-center"
            >
              <p>© 2025 GW2 WvW Builder</p>
              <p className="text-purple-400 mt-1">v0.1.0</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
}
