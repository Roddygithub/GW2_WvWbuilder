/**
 * GW2Optimizer - BuildCard Component
 * Affiche un build individuel avec icône GW2, stats et capabilities
 */

import { FC } from 'react';
import { Build } from '@/types/gw2optimizer';
import { Zap, Shield, Swords, Heart } from 'lucide-react';
import { getProfessionIcon, getSpecializationIcon } from '@/utils/gw2icons';

interface BuildCardProps {
  build: Build;
  onSelect?: () => void;
  isSelected?: boolean;
  showCapabilities?: boolean;
}

export const BuildCard: FC<BuildCardProps> = ({
  build,
  onSelect,
  isSelected = false,
  showCapabilities = true,
}) => {
  const specIcon = getSpecializationIcon(build.specialization);
  const profIcon = getProfessionIcon(build.profession);
  const iconUrl = specIcon || profIcon;

  const synergyColor =
    build.synergy === 'high'
      ? 'text-success border-success/50 bg-success/10'
      : build.synergy === 'medium'
      ? 'text-warning border-warning/50 bg-warning/10'
      : 'text-danger border-danger/50 bg-danger/10';

  const getRoleIcon = () => {
    switch (build.role.toLowerCase()) {
      case 'support':
        return <Shield className="h-4 w-4" />;
      case 'dps':
        return <Swords className="h-4 w-4" />;
      case 'healer':
        return <Heart className="h-4 w-4" />;
      default:
        return <Zap className="h-4 w-4" />;
    }
  };

  return (
    <div
      className={`gw2-card transition-all duration-200 ${
        isSelected ? 'border-gw2-gold shadow-lg shadow-gw2-gold/20' : 'hover:border-gw2-gold/50'
      } ${onSelect ? 'cursor-pointer' : ''}`}
      onClick={onSelect}
    >
      <div className="flex items-center gap-4">
        {/* Icon */}
        <div className="flex-shrink-0">
          {iconUrl ? (
            <img
              src={iconUrl}
              alt={build.specialization}
              className="w-12 h-12 rounded-md border border-gw2-border"
              loading="lazy"
            />
          ) : (
            <div className="w-12 h-12 rounded-md border border-gw2-border bg-gw2-dark flex items-center justify-center text-2xl">
              ⚔️
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-bold text-gw2-text truncate">
            {build.specialization}
          </h3>
          <div className="flex items-center gap-2 text-xs text-gw2-textSecondary mt-1">
            <span>{build.profession}</span>
            <span>•</span>
            <div className="flex items-center gap-1">
              {getRoleIcon()}
              <span>{build.role}</span>
            </div>
          </div>

          {/* Synergy Badge */}
          <div className="mt-2">
            <span className={`gw2-badge text-xs ${synergyColor}`}>
              {build.synergy.toUpperCase()} Synergy
            </span>
          </div>
        </div>

        {/* Weight */}
        <div className="flex-shrink-0 text-right">
          <div className="text-xs text-gw2-textSecondary mb-1">Weight</div>
          <div className="text-xl font-bold text-gw2-gold">
            {(build.weight * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Capabilities */}
      {showCapabilities && build.capabilities && (
        <div className="mt-3 pt-3 border-t border-gw2-border">
          <div className="text-xs text-gw2-textSecondary mb-2 font-semibold">
            Capabilities
          </div>
          <div className="grid grid-cols-3 gap-1">
            {Object.entries(build.capabilities).map(([key, value]) => {
              if (!value || value === 0) return null;
              return (
                <div
                  key={key}
                  className="flex items-center justify-between bg-gw2-dark px-2 py-1 rounded text-xs"
                >
                  <span className="text-gw2-textSecondary capitalize">
                    {key}:
                  </span>
                  <span className="text-gw2-gold font-semibold ml-1">
                    {Math.round(value * 100)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Description */}
      {build.description && (
        <div className="mt-3 pt-3 border-t border-gw2-border">
          <p className="text-xs text-gw2-textSecondary italic">
            {build.description}
          </p>
        </div>
      )}
    </div>
  );
};

export default BuildCard;
