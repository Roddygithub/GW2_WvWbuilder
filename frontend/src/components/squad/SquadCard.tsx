/**
 * GW2Optimizer - SquadCard Component
 * Affiche une composition d'escouade avec builds, poids, synergies et badges
 */

import { FC } from 'react';
import { Squad, PROFESSIONS } from '@/types/gw2optimizer';
import { Users, TrendingUp, TrendingDown, Clock, Zap } from 'lucide-react';

interface SquadCardProps {
  squad: Squad;
  onSelect?: (squadId: string) => void;
}

export const SquadCard: FC<SquadCardProps> = ({ squad, onSelect }) => {
  return (
    <div
      className="gw2-card-hover cursor-pointer"
      onClick={() => onSelect?.(squad.id)}
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

      {/* Mode Badge */}
      {squad.mode && (
        <div className="mt-3 pt-3 border-t border-gw2-border">
          <span className="gw2-badge bg-gw2-red/20 text-gw2-red border border-gw2-red/50 text-xs">
            Mode: {squad.mode.toUpperCase()}
          </span>
        </div>
      )}
    </div>
  );
};

export default SquadCard;
