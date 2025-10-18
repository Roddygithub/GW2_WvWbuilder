/**
 * GW2Optimizer - BuildSelector Component
 * Modal pour sélectionner et appliquer des builds
 */

import { FC, useState, useMemo } from 'react';
import { X, Search, Filter } from 'lucide-react';
import { Build, BuildFilter, PROFESSIONS } from '@/types/gw2optimizer';

interface BuildSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (build: Build) => void;
  availableBuilds?: Build[];
}

export const BuildSelector: FC<BuildSelectorProps> = ({
  isOpen,
  onClose,
  onSelect,
  availableBuilds = MOCK_BUILDS,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<BuildFilter>({});

  // Filtrer les builds
  const filteredBuilds = useMemo(() => {
    return availableBuilds.filter((build) => {
      // Search term
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        const matchName = build.specialization.toLowerCase().includes(term);
        const matchProf = build.profession.toLowerCase().includes(term);
        const matchRole = build.role.toLowerCase().includes(term);
        if (!matchName && !matchProf && !matchRole) return false;
      }

      // Profession filter
      if (filters.profession && build.profession !== filters.profession) {
        return false;
      }

      // Role filter
      if (filters.role && build.role !== filters.role) {
        return false;
      }

      // Synergy filter
      if (filters.synergy && build.synergy !== filters.synergy) {
        return false;
      }

      // Min weight filter
      if (filters.minWeight && build.weight < filters.minWeight) {
        return false;
      }

      return true;
    });
  }, [availableBuilds, searchTerm, filters]);

  const handleSelect = (build: Build) => {
    onSelect(build);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-gw2-dark/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[90vh] gw2-card overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-gw2-border">
          <h2 className="text-2xl font-bold text-gw2-gold">
            Build Selector
          </h2>
          <button
            onClick={onClose}
            className="gw2-button-secondary p-2"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="py-4 space-y-3 border-b border-gw2-border">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gw2-textSecondary" />
            <input
              type="text"
              placeholder="Search builds..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="gw2-input w-full pl-10"
            />
          </div>

          {/* Filter Row */}
          <div className="flex gap-3 flex-wrap">
            <select
              className="gw2-input flex-1 min-w-[150px]"
              value={filters.profession || ''}
              onChange={(e) =>
                setFilters({ ...filters, profession: e.target.value || undefined })
              }
            >
              <option value="">All Professions</option>
              {Object.values(PROFESSIONS).map((prof) => (
                <option key={prof.name} value={prof.name}>
                  {prof.icon} {prof.name}
                </option>
              ))}
            </select>

            <select
              className="gw2-input flex-1 min-w-[150px]"
              value={filters.role || ''}
              onChange={(e) =>
                setFilters({ ...filters, role: e.target.value || undefined })
              }
            >
              <option value="">All Roles</option>
              <option value="Support">Support</option>
              <option value="DPS">DPS</option>
              <option value="Healer">Healer</option>
              <option value="Tank">Tank</option>
            </select>

            <select
              className="gw2-input flex-1 min-w-[150px]"
              value={filters.synergy || ''}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  synergy: e.target.value as 'high' | 'medium' | 'low' | undefined,
                })
              }
            >
              <option value="">All Synergies</option>
              <option value="high">High Synergy</option>
              <option value="medium">Medium Synergy</option>
              <option value="low">Low Synergy</option>
            </select>

            <button
              onClick={() => {
                setFilters({});
                setSearchTerm('');
              }}
              className="gw2-button-secondary px-4 flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Clear
            </button>
          </div>
        </div>

        {/* Results Count */}
        <div className="py-2 text-sm text-gw2-textSecondary">
          {filteredBuilds.length} build{filteredBuilds.length !== 1 ? 's' : ''} found
        </div>

        {/* Builds List */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-2">
          {filteredBuilds.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <p className="text-gw2-textSecondary">No builds found</p>
            </div>
          ) : (
            filteredBuilds.map((build) => (
              <BuildCard
                key={build.id}
                build={build}
                onSelect={() => handleSelect(build)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

interface BuildCardProps {
  build: Build;
  onSelect: () => void;
}

const BuildCard: FC<BuildCardProps> = ({ build, onSelect }) => {
  const profession = build.profession.toLowerCase();
  const profMeta = PROFESSIONS[profession];

  const synergyColor =
    build.synergy === 'high'
      ? 'text-success'
      : build.synergy === 'medium'
      ? 'text-warning'
      : 'text-danger';

  return (
    <div className="gw2-card-hover flex items-center gap-4 p-4">
      {/* Icon */}
      <div className="flex-shrink-0 text-4xl">
        {profMeta?.icon || '⚔️'}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3 className="text-lg font-bold text-gw2-text mb-1">
          {build.specialization}
        </h3>
        <div className="flex items-center gap-3 text-sm text-gw2-textSecondary">
          <span>{build.profession}</span>
          <span>•</span>
          <span>{build.role}</span>
          <span>•</span>
          <span className={synergyColor}>
            {build.synergy.toUpperCase()} Synergy
          </span>
        </div>

        {/* Capabilities */}
        {build.capabilities && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {Object.entries(build.capabilities).map(([key, value]) => {
              if (!value || value === 0) return null;
              return (
                <span key={key} className="gw2-badge bg-gw2-dark text-xs">
                  {key}: {Math.round(value * 100)}%
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="flex-shrink-0 text-right">
        <div className="text-sm text-gw2-textSecondary mb-1">Weight</div>
        <div className="text-xl font-bold text-gw2-gold">
          {(build.weight * 100).toFixed(0)}%
        </div>
      </div>

      {/* Select Button */}
      <button
        onClick={onSelect}
        className="gw2-button-primary flex-shrink-0"
      >
        Select
      </button>
    </div>
  );
};

// Mock builds pour démonstration
const MOCK_BUILDS: Build[] = [
  {
    id: '101',
    profession: 'Guardian',
    specialization: 'Firebrand',
    role: 'Support',
    weight: 0.85,
    synergy: 'high',
    capabilities: {
      quickness: 0.6,
      stability: 0.9,
      protection: 0.7,
      resistance: 0.4,
      might: 0.6,
    },
    description: 'Top tier support with quickness and stability',
  },
  {
    id: '102',
    profession: 'Engineer',
    specialization: 'Scrapper',
    role: 'Support',
    weight: 1.1,
    synergy: 'high',
    capabilities: {
      quickness: 0.3,
      stability: 0.85,
      protection: 0.5,
      resistance: 0.6,
      might: 0.4,
    },
  },
  {
    id: '103',
    profession: 'Revenant',
    specialization: 'Herald',
    role: 'Support',
    weight: 0.95,
    synergy: 'medium',
    capabilities: {
      quickness: 0.9,
      alacrity: 0.2,
      stability: 0.2,
      resistance: 0.5,
      protection: 0.8,
      might: 0.8,
      fury: 0.7,
    },
  },
  {
    id: '104',
    profession: 'Necromancer',
    specialization: 'Scourge',
    role: 'DPS',
    weight: 0.92,
    synergy: 'medium',
    capabilities: {
      resistance: 0.6,
      protection: 0.3,
      might: 0.2,
    },
  },
  {
    id: '105',
    profession: 'Elementalist',
    specialization: 'Tempest',
    role: 'Healer',
    weight: 0.88,
    synergy: 'medium',
    capabilities: {
      stability: 0.2,
      resistance: 0.5,
      protection: 0.6,
      might: 0.3,
    },
  },
  {
    id: '106',
    profession: 'Engineer',
    specialization: 'Mechanist',
    role: 'Support',
    weight: 0.90,
    synergy: 'low',
    capabilities: {
      alacrity: 0.3,
      might: 0.9,
      resistance: 0.3,
      protection: 0.3,
    },
  },
];

export default BuildSelector;
