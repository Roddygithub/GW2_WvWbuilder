/**
 * Page Container with GW2 Theme
 * Animated container for all pages
 */

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { pageVariants } from "@/lib/animations";
import { cn } from "@lib/utils";

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}

export const PageContainer = ({
  children,
  className,
  title,
  subtitle,
}: PageContainerProps) => {
  return (
    <motion.div
      className={cn(
        "min-h-screen bg-gradient-to-br from-gw2-fractal-dark via-gw2-fractal to-gw2-fractal-dark",
        "text-gw2-offwhite",
        className,
      )}
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="container mx-auto px-4 py-8">
        {(title || subtitle) && (
          <div className="mb-8">
            {title && (
              <h1 className="text-4xl font-bold text-gw2-gold mb-2">{title}</h1>
            )}
            {subtitle && (
              <p className="text-gw2-offwhite/70 text-lg">{subtitle}</p>
            )}
            <div className="mt-4 h-[2px] w-24 bg-gradient-to-r from-gw2-gold to-transparent" />
          </div>
        )}
        {children}
      </div>
    </motion.div>
  );
};

export default PageContainer;
