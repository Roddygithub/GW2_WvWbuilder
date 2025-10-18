/**
 * GW2Optimizer - Header Component
 * Header principal avec logo et mention Mistral 7B
 */

import { FC } from 'react';
import { Flame } from 'lucide-react';

export const Header: FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-gw2-border bg-gw2-dark/95 backdrop-blur supports-[backdrop-filter]:bg-gw2-dark/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Flame className="h-8 w-8 text-gw2-red" />
            <h1 className="text-2xl font-bold gw2-gradient-text">
              GW2Optimizer
            </h1>
          </div>
        </div>

        {/* Powered By Mistral */}
        <div className="flex items-center gap-2 text-sm text-gw2-textSecondary">
          <span className="hidden sm:inline">Empowered by</span>
          <span className="font-semibold text-gw2-gold">Ollama</span>
          <span className="hidden sm:inline">with</span>
          <span className="font-semibold text-gw2-text">Mistral 7B</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
