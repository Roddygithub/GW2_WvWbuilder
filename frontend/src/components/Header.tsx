/**
 * Header Component - GW2 Themed Welcome Section
 * Animated header with user info and logout
 */

import { motion } from 'framer-motion';
import { LogOut, Bell, User } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export default function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="sticky top-0 z-40 bg-gradient-to-r from-slate-950/95 via-purple-950/95 to-slate-950/95 backdrop-blur-md border-b border-purple-500/20"
    >
      <div className="px-8 py-6">
        <div className="flex items-center justify-between">
          {/* Welcome Section */}
          <div className="flex-1">
            <motion.h2
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-violet-300 to-purple-400"
            >
              {getGreeting()}, {user?.username || 'Commander'}!
            </motion.h2>
            <motion.p
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-slate-400 mt-1"
            >
              Ready to lead your squad to victory
            </motion.p>
          </div>

          {/* Actions */}
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="flex items-center space-x-4"
          >
            {/* Notifications */}
            <motion.button
              whileHover={{ scale: 1.1, rotate: 15 }}
              whileTap={{ scale: 0.9 }}
              className="relative p-3 rounded-xl bg-slate-800/60 border border-purple-500/20 hover:border-purple-400/40 hover:bg-slate-800/80 transition-all duration-300 group"
            >
              <Bell className="w-5 h-5 text-purple-300 group-hover:text-purple-200" />
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-br from-purple-500 to-violet-600 rounded-full flex items-center justify-center text-xs text-white font-bold shadow-[0_0_10px_rgba(168,85,247,0.6)]"
              >
                0
              </motion.span>
            </motion.button>

            {/* User Profile */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-slate-800/60 border border-purple-500/20 hover:border-purple-400/40 hover:bg-slate-800/80 transition-all duration-300 group"
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-slate-200 group-hover:text-purple-200">
                  {user?.username || 'Commander'}
                </p>
                <p className="text-xs text-slate-400">
                  {user?.is_superuser ? 'Admin' : 'Player'}
                </p>
              </div>
            </motion.button>

            {/* Logout */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleLogout}
              className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 hover:border-red-400/40 hover:bg-red-500/20 transition-all duration-300 group"
            >
              <LogOut className="w-5 h-5 text-red-400 group-hover:text-red-300" />
            </motion.button>
          </motion.div>
        </div>

        {/* Decorative Line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="mt-6 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent"
        />
      </div>
    </motion.header>
  );
}
