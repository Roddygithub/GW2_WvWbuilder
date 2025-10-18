import { useDroppable } from "@dnd-kit/core";
import { AlertCircle, CheckCircle2, Shield } from "lucide-react";
import { Group, Player, Build } from "../../store/optimizeStore";
import PlayerCard from "./PlayerCard";

type GroupCardProps = {
  group: Group;
  players: Player[];
  builds: Build[];
};

function CoverageBadge({ label, value, target }: { label: string; value: number; target?: number }) {
  const pct = Math.round(value * 100);
  const isWarning = target !== undefined && value < target;
  
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`capitalize ${isWarning ? "text-destructive" : "text-muted-foreground"}`}>
        {label}
      </span>
      <div className="w-20 h-2 bg-muted rounded overflow-hidden">
        <div
          className={`h-full transition-all ${isWarning ? "bg-destructive" : "bg-primary"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`font-semibold ${isWarning ? "text-destructive" : "text-primary"}`}>
        {pct}%
      </span>
    </div>
  );
}

export default function GroupCard({ group, players, builds }: GroupCardProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: `group-${group.id}`,
    data: { groupId: group.id },
  });

  const groupPlayers = players.filter(p => group.playerIds.includes(p.id));
  const isFull = groupPlayers.length >= 5;
  
  // Check constraints
  const warnings: string[] = [];
  if (group.coverage.quickness < 0.9) warnings.push("Quickness < 90%");
  if (group.coverage.resistance < 0.8) warnings.push("Resistance < 80%");
  if (group.coverage.protection < 0.6) warnings.push("Protection < 60%");
  if (group.coverage.stability < 0.5) warnings.push("Stability < 50%");

  return (
    <div
      ref={setNodeRef}
      className={`border-2 rounded-lg p-4 transition-all ${
        isOver && !isFull
          ? "border-primary bg-primary/10 scale-105"
          : isFull
          ? "border-muted bg-muted/20"
          : "border-border bg-card"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary" />
          <h3 className="font-semibold">Groupe {group.id}</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${isFull ? "text-muted-foreground" : "text-primary"}`}>
            {groupPlayers.length} / 5
          </span>
          {warnings.length === 0 ? (
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          ) : (
            <AlertCircle className="w-4 h-4 text-destructive" />
          )}
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="mb-3 p-2 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive">
          <div className="font-semibold mb-1">⚠️ Contraintes non satisfaites:</div>
          <ul className="list-disc list-inside space-y-0.5">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Coverage */}
      <div className="space-y-1.5 mb-3">
        <CoverageBadge label="quickness" value={group.coverage.quickness} target={0.9} />
        <CoverageBadge label="resistance" value={group.coverage.resistance} target={0.8} />
        <CoverageBadge label="protection" value={group.coverage.protection} target={0.6} />
        <CoverageBadge label="stability" value={group.coverage.stability} target={0.5} />
        <CoverageBadge label="might" value={group.coverage.might} />
        <CoverageBadge label="fury" value={group.coverage.fury} />
      </div>

      {/* Players */}
      <div className="space-y-2 min-h-[100px]">
        {groupPlayers.length === 0 ? (
          <div className="text-center text-sm text-muted-foreground py-8 border-2 border-dashed border-muted rounded">
            Glissez des joueurs ici
          </div>
        ) : (
          groupPlayers.map(player => {
            const build = builds.find(b => b.id === player.buildId);
            return (
              <PlayerCard
                key={player.id}
                player={player}
                build={build}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
