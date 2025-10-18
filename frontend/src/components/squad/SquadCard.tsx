/**
 * GW2Optimizer - SquadCard Component
 * Affiche une composition d'escouade avec builds, poids, synergies et badges
 * Version avancée avec animations, hover details et timeline
 */

import { FC, useState } from 'react';
import { Squad, PROFESSIONS } from '@/types/gw2optimizer';
import { Users, TrendingUp, TrendingDown, Clock, Zap, ChevronDown, ChevronUp, Info } from 'lucide-react';

interface SquadCardProps {
  squad: Squad;
  onSelect?: (squadId: string) => void;
  showTimeline?: boolean;
}

export const SquadCard: FC<SquadCardProps> = ({ squad, onSelect, showTimeline = false }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const handleCardClick = () => {
    onSelect?.(squad.id);
  };

  const handleExpandToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <div
      className="gw2-card-hover cursor-pointer transition-all duration-300"
      onClick={handleCardClick}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => setShowDetails(false)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5 text-gw2-gold" />
          <h3 className="text-lg font-bold text-gw2-text">{squad.name}</h3>
        </div>
        <div className="flex items-center gap-2 text-xs text-gw2-textSecondary">
          <Clock className="h-3 w-3" />
          {new Date(squad.timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="gw2-card bg-gw2-dark p-2 text-center">
          <div className="text-xs text-gw2-textSecondary mb-1">Weight</div>
          <div className="text-lg font-bold text-gw2-gold">
            {(squad.weight * 100).toFixed(0)}%
          </div>
        </div>
        <div className="gw2-card bg-gw2-dark p-2 text-center">
          <div className="text-xs text-gw2-textSecondary mb-1">Synergy</div>
          <div className="text-lg font-bold text-gw2-gold">
            {(squad.synergy * 100).toFixed(0)}%
          </div>
        </div>
        <div className="gw2-card bg-gw2-dark p-2 text-center">
          <div className="text-xs text-gw2-textSecondary mb-1">Players</div>
          <div className="text-lg font-bold text-gw2-text">
            {squad.squad_size}
          </div>
        </div>
      </div>

      {/* Builds */}
      <div className="mb-4">
        <div className="text-xs text-gw2-textSecondary mb-2 font-semibold">
          Squad Composition
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {squad.builds.map((build, idx) => {
            const profession = build.profession.toLowerCase();
            const profMeta = PROFESSIONS[profession];
            
            return (
              <div
                key={idx}
                className="flex items-center gap-2 bg-gw2-dark p-2 rounded-md border border-gw2-border"
              >
                <span className="text-xl">{profMeta?.icon || '⚔️'}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-gw2-text truncate">
                    {build.specialization}
                  </div>
                  <div className="text-xs text-gw2-textSecondary">
                    x{build.count}
                  </div>
                </div>
                <div className="flex items-center">
                  <Zap className="h-3 w-3 text-gw2-gold" />
                  <span className="text-xs text-gw2-gold ml-1">
                    {(build.weight * 100).toFixed(0)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Buffs & Nerfs */}
      {(squad.buffs.length > 0 || squad.nerfs.length > 0) && (
        <div className="space-y-2">
          {squad.buffs.length > 0 && (
            <div>
              <div className="text-xs text-gw2-textSecondary mb-1 font-semibold flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-success" />
                Buffs
              </div>
              <div className="flex flex-wrap gap-1">
                {squad.buffs.map((buff, idx) => (
                  <span key={idx} className="gw2-badge-buff text-xs">
                    {buff}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {squad.nerfs.length > 0 && (
            <div>
              <div className="text-xs text-gw2-textSecondary mb-1 font-semibold flex items-center gap-1">
                <TrendingDown className="h-3 w-3 text-danger" />
                Nerfs
              </div>
              <div className="flex flex-wrap gap-1">
                {squad.nerfs.map((nerf, idx) => (
                  <span key={idx} className="gw2-badge-nerf text-xs">
                    {nerf}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Mode Badge & Expand Button */}
      <div className="mt-3 pt-3 border-t border-gw2-border flex items-center justify-between">
        {squad.mode && (
          <span className="gw2-badge bg-gw2-red/20 text-gw2-red border border-gw2-red/50 text-xs">
            Mode: {squad.mode.toUpperCase()}
          </span>
        )}
        
        <button
          onClick={handleExpandToggle}
          className="gw2-button-secondary px-3 py-1 text-xs flex items-center gap-1"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-3 w-3" />
              Less
            </>
          ) : (
            <>
              <ChevronDown className="h-3 w-3" />
              Details
            </>
          )}
        </button>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gw2-border space-y-3 animate-accordion-down">
          {/* Detailed Stats */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-4 w-4 text-gw2-gold" />
              <span className="text-sm font-semibold text-gw2-text">Detailed Analysis</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="gw2-card bg-gw2-dark p-2">
                <div className="text-gw2-textSecondary mb-1">Avg Build Weight</div>
                <div className="text-gw2-gold font-bold">
                  {squad.builds.length > 0
                    ? ((squad.builds.reduce((sum, b) => sum + b.weight, 0) / squad.builds.length) * 100).toFixed(0)
                    : 0}%
                </div>
              </div>
              <div className="gw2-card bg-gw2-dark p-2">
                <div className="text-gw2-textSecondary mb-1">Build Diversity</div>
                <div className="text-gw2-gold font-bold">
                  {squad.builds.length} types
                </div>
              </div>
            </div>
          </div>

          {/* Timeline (if enabled) */}
          {showTimeline && (
            <div>
              <div className="text-xs font-semibold text-gw2-textSecondary mb-2">Recent Changes</div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs text-gw2-text">
                  <Clock className="h-3 w-3 text-gw2-gold" />
                  <span>Created {new Date(squad.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Hover Tooltip */}
      {showDetails && !isExpanded && (
        <div className="absolute top-0 left-0 right-0 bg-gw2-dark/95 backdrop-blur-sm p-2 rounded-t-card border-t-2 border-gw2-gold text-xs text-gw2-textSecondary z-10">
          Click to select • Hover for quick stats • Details for full analysis
        </div>
      )}
    </div>
  );
};

export default SquadCard;
