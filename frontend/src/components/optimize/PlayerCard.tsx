import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, User } from "lucide-react";
import { Player, Build } from "../../store/optimizeStore";

type PlayerCardProps = {
  player: Player;
  build?: Build;
};

export default function PlayerCard({ player, build }: PlayerCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `player-${player.id}`,
    data: { playerId: player.id, currentGroupId: player.groupId },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-2 p-2 bg-muted/30 border border-border rounded cursor-move hover:bg-muted/50 transition-all ${
        isDragging ? "shadow-lg ring-2 ring-primary" : ""
      }`}
      {...listeners}
      {...attributes}
    >
      <GripVertical className="w-4 h-4 text-muted-foreground flex-shrink-0" />
      <User className="w-4 h-4 text-primary flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{player.name}</div>
        {build && (
          <div className="text-xs text-muted-foreground truncate">
            {build.profession} - {build.specialization}
          </div>
        )}
      </div>
    </div>
  );
}
