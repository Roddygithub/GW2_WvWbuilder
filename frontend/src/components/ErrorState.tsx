/**
 * ErrorState Component
 * GW2-styled error display with retry option
 */

import { motion } from "framer-motion";
import { AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
  fullScreen?: boolean;
}

export default function ErrorState({
  message = "Something went wrong",
  onRetry,
  className,
  fullScreen = false,
}: ErrorStateProps) {
  const content = (
    <div
      className={cn(
        "flex flex-col items-center justify-center",
        fullScreen ? "min-h-screen" : "py-12",
        className,
      )}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="max-w-md w-full"
      >
        {/* Error Card */}
        <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-xl p-8 border border-red-500/30 backdrop-blur-sm">
          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-red-500/20 border border-red-500/40 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-white text-center mb-2">
            Error
          </h3>

          {/* Message */}
          <p className="text-red-200 text-center mb-6">{message}</p>

          {/* Retry Button */}
          {onRetry && (
            <div className="flex justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onRetry}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-red-500/20 to-orange-500/20 hover:from-red-500/30 hover:to-orange-500/30 border border-red-500/40 rounded-lg text-white font-medium transition-all duration-300"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Retry</span>
              </motion.button>
            </div>
          )}

          {/* Help Text */}
          <p className="text-slate-400 text-xs text-center mt-4">
            If the problem persists, please check your connection or contact
            support.
          </p>
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
