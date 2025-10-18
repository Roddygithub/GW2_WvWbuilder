/**
 * BuildCard Component
 * Displays a single build with profession icon, spec, role, and link to GW2Skills
 */

import { ExternalLink } from "lucide-react";
import { getProfessionIcon, getProfessionColor, getGW2SkillsLink } from "../utils/gw2Icons";

interface BuildCardProps {
  professionName: string;
  eliteSpecializationName?: string | null;
  roleType: string;
  isCommander: boolean;
  playerNumber: number;
}

export default function BuildCard({
  professionName,
  eliteSpecializationName,
  roleType,
  isCommander,
  playerNumber,
}: BuildCardProps) {
  const professionColor = getProfessionColor(professionName);
  const professionIcon = getProfessionIcon(professionName);
  const gw2SkillsLink = getGW2SkillsLink(professionName, eliteSpecializationName);

  return (
    <div
      className="gw2-card p-3 hover:gw2-gold-glow transition-all group"
      style={{ borderLeft: `4px solid ${professionColor}` }}
    >
      <div className="flex items-center gap-3">
        {/* Profession Icon */}
        <div className="relative flex-shrink-0">
          <img
            src={professionIcon}
            alt={professionName}
            className="w-12 h-12 rounded"
            style={{ backgroundColor: `${professionColor}20` }}
          />
          {isCommander && (
            <div className="absolute -top-1 -right-1 text-lg">👑</div>
          )}
        </div>

        {/* Build Info */}
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm flex items-center gap-2">
            <span className="text-foreground">{professionName}</span>
            {eliteSpecializationName && (
              <span className="text-primary">- {eliteSpecializationName}</span>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            Player {playerNumber} • {roleType.replace("_", " ")}
          </div>
        </div>

        {/* GW2Skills Link */}
        <a
          href={gw2SkillsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 p-2 rounded hover:bg-primary/20 transition-colors"
          title="Ouvrir dans GW2Skills"
        >
          <ExternalLink className="w-4 h-4 text-primary" />
        </a>
      </div>

      {/* TODO v4: Add weapons, skills, traits preview */}
      {/* <div className="mt-2 pt-2 border-t border-border text-xs">
        <div>Weapons: Staff, Scepter/Focus</div>
        <div>Skills: Healing Signet, Shelter, etc.</div>
      </div> */}
    </div>
  );
}
