/**
 * Main Layout Component
 * Wraps protected pages with Header, Sidebar and consistent styling
 */

import { ReactNode } from "react";
import { motion } from "framer-motion";
import Header from "../Header";
import Sidebar from "../Sidebar";
import { Toaster } from "sonner";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="ml-[280px] transition-all duration-300">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="p-8"
        >
          {children}
        </motion.main>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "rgba(15, 23, 42, 0.95)",
            border: "1px solid rgba(168, 85, 247, 0.3)",
            color: "#e2e8f0",
          },
        }}
      />
    </div>
  );
}
