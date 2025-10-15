/**
 * SettingsModal Component
 * Modal for theme, language, and notification settings
 */

import { motion, AnimatePresence } from "framer-motion";
import { X, Moon, Sun, Globe, Bell, Check } from "lucide-react";
import { useState } from "react";
import { cn } from '../lib/utils';
import { toast } from "sonner";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [language, setLanguage] = useState<"en" | "fr">("en");
  const [notifications, setNotifications] = useState({
    builds: true,
    teams: true,
    updates: false,
  });

  const handleSave = () => {
    toast.success("Settings saved successfully!");
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="w-full max-w-2xl bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl border border-purple-500/30 shadow-[0_0_50px_rgba(168,85,247,0.3)] overflow-hidden">
              {/* Header */}
              <div className="px-6 py-4 border-b border-purple-500/20 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-violet-400">
                  Settings
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-slate-800/60 transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                {/* Theme Section */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                    <Moon className="w-5 h-5 text-purple-400" />
                    <span>Theme</span>
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {["dark", "light"].map((t) => (
                      <motion.button
                        key={t}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setTheme(t as "light" | "dark")}
                        className={cn(
                          "flex items-center justify-between p-4 rounded-lg border-2 transition-all duration-300",
                          theme === t
                            ? "bg-purple-500/20 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                            : "bg-slate-800/40 border-slate-700 hover:border-slate-600",
                        )}
                      >
                        <div className="flex items-center space-x-3">
                          {t === "dark" ? (
                            <Moon className="w-5 h-5 text-purple-400" />
                          ) : (
                            <Sun className="w-5 h-5 text-amber-400" />
                          )}
                          <span className="text-slate-200 font-medium capitalize">
                            {t}
                          </span>
                        </div>
                        {theme === t && (
                          <Check className="w-5 h-5 text-purple-400" />
                        )}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Language Section */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                    <Globe className="w-5 h-5 text-purple-400" />
                    <span>Language</span>
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { code: "en", name: "English" },
                      { code: "fr", name: "Français" },
                    ].map((lang) => (
                      <motion.button
                        key={lang.code}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setLanguage(lang.code as "en" | "fr")}
                        className={cn(
                          "flex items-center justify-between p-4 rounded-lg border-2 transition-all duration-300",
                          language === lang.code
                            ? "bg-purple-500/20 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                            : "bg-slate-800/40 border-slate-700 hover:border-slate-600",
                        )}
                      >
                        <span className="text-slate-200 font-medium">
                          {lang.name}
                        </span>
                        {language === lang.code && (
                          <Check className="w-5 h-5 text-purple-400" />
                        )}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Notifications Section */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                    <Bell className="w-5 h-5 text-purple-400" />
                    <span>Notifications</span>
                  </h3>
                  <div className="space-y-3">
                    {[
                      {
                        key: "builds",
                        label: "New builds shared",
                        description: "Get notified when new builds are shared",
                      },
                      {
                        key: "teams",
                        label: "Team updates",
                        description: "Get notified about team changes",
                      },
                      {
                        key: "updates",
                        label: "System updates",
                        description: "Get notified about app updates",
                      },
                    ].map((notif) => (
                      <div
                        key={notif.key}
                        className="flex items-center justify-between p-4 rounded-lg bg-slate-800/40 border border-slate-700 hover:border-slate-600 transition-colors"
                      >
                        <div>
                          <p className="text-slate-200 font-medium">
                            {notif.label}
                          </p>
                          <p className="text-xs text-slate-400 mt-1">
                            {notif.description}
                          </p>
                        </div>
                        <button
                          onClick={() =>
                            setNotifications((prev) => ({
                              ...prev,
                              [notif.key]:
                                !prev[notif.key as keyof typeof prev],
                            }))
                          }
                          className={cn(
                            "relative w-12 h-6 rounded-full transition-colors duration-300",
                            notifications[
                              notif.key as keyof typeof notifications
                            ]
                              ? "bg-purple-500"
                              : "bg-slate-600",
                          )}
                        >
                          <motion.div
                            layout
                            transition={{ duration: 0.2 }}
                            className={cn(
                              "absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-lg",
                              notifications[
                                notif.key as keyof typeof notifications
                              ]
                                ? "left-6"
                                : "left-0.5",
                            )}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="px-6 py-4 border-t border-purple-500/20 flex justify-end space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 transition-colors"
                >
                  Cancel
                </button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSave}
                  className="px-6 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-violet-600 hover:from-purple-600 hover:to-violet-700 text-white font-medium shadow-lg shadow-purple-500/30 transition-all duration-300"
                >
                  Save Changes
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
