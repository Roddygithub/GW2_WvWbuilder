import { useEffect, useRef, useState } from "react";
import { DndContext, DragEndEvent, DragOverlay, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { startOptimize, streamOptimize, type OptimizationRequest as ApiOptimizationRequest } from "../api/optimize";
import { Users, Zap, Gauge, Sparkles, RefreshCw } from "lucide-react";
import { useOptimizeStore, type Build as StoreBuild } from "../store/optimizeStore";
import GroupCard from "../components/optimize/GroupCard";
import PlayerCard from "../components/optimize/PlayerCard";

const DEFAULT_BUILDS: StoreBuild[] = [
  { id: 101, profession: "Guardian", specialization: "Firebrand", mode: "wvw" },
  { id: 102, profession: "Engineer", specialization: "Scrapper", mode: "wvw" },
  { id: 103, profession: "Revenant", specialization: "Herald", mode: "wvw" },
  { id: 104, profession: "Elementalist", specialization: "Tempest", mode: "wvw" },
  { id: 105, profession: "Necromancer", specialization: "Scourge", mode: "wvw" },
  { id: 106, profession: "Engineer", specialization: "Mechanist", mode: "wvw" },
];

export default function OptimizePage() {
  const store = useOptimizeStore();
  const stopStreamRef = useRef<() => void>();
  const [draggedPlayer, setDraggedPlayer] = useState<any>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Initialize on mount
  useEffect(() => {
    store.setBuilds(DEFAULT_BUILDS);
    store.initializePlayers(15, DEFAULT_BUILDS);
  }, []);

  // Cleanup stream on unmount
  useEffect(() => () => stopStreamRef.current?.(), []);

  const onStart = async () => {
    if (store.squadSize < 1 || store.squadSize > 50) return;
    
    const req: ApiOptimizationRequest = {
      players: store.players.map(p => ({
        id: p.id,
        name: p.name,
        eligible_build_ids: DEFAULT_BUILDS.map(b => b.id),
      })),
      builds: store.builds,
      mode: "wvw",
      squad_size: store.squadSize,
      time_limit_ms: 3000,
      targets: {
        quickness_uptime: 0.9,      // 90% quickness (critique pour WvW)
        alacrity_uptime: 0.7,        // 70% alacrity (utile mais pas critique)
        resistance_uptime: 0.8,      // 80% resistance (important vs conditions)
        protection_uptime: 0.6,      // 60% protection (mitigation)
        stability_sources: 2,        // Au moins 2 sources de stability par groupe
      },
      weights: {
        quickness: 1.0,
        alacrity: 0.8,
        stability: 1.0,              // Stability très important en WvW
        resistance: 0.9,
        protection: 0.7,
        might: 0.5,
        fury: 0.4,
        dps: 0.6,
        sustain: 0.5,
      },
    };
    
    try {
      const res = await startOptimize(req);
      store.setJobId(res.job_id);
      store.setStatus("queued");
      
      if (stopStreamRef.current) stopStreamRef.current();
      stopStreamRef.current = streamOptimize(res.job_id, (data) => {
        store.updateFromSSE(data);
      });
    } catch (error) {
      console.error("Optimization failed:", error);
      store.setStatus("error");
    }
  };

  const handleDragStart = (event: any) => {
    const player = store.players.find(p => p.id === event.active.data.current?.playerId);
    setDraggedPlayer(player);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setDraggedPlayer(null);
    const { active, over } = event;
    
    if (!over) return;
    
    const playerId = active.data.current?.playerId;
    const targetGroupId = over.data.current?.groupId;
    
    if (playerId && targetGroupId && playerId !== targetGroupId) {
      const targetGroup = store.groups.find(g => g.id === targetGroupId);
      if (targetGroup && targetGroup.playerIds.length < 5) {
        store.movePlayer(playerId, targetGroupId);
      }
    }
  };

  const handleSquadSizeChange = (newSize: number) => {
    const size = Math.max(1, Math.min(50, newSize));
    store.initializePlayers(size, store.builds);
  };

  const gridCols = Math.min(3, store.groups.length);

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="min-h-screen gw2-fractal-bg gw2-tyria-pattern p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-primary" />
              <h1 className="text-3xl font-bold">Optimize WvW (DnD)</h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Gauge className="w-4 h-4" />
                <span>Score</span>
                <span className="font-semibold text-primary">{Math.round(store.bestScore * 100)}%</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Status</span>
                <span className={`font-semibold ${
                  store.status === "complete" ? "text-green-500" :
                  store.status === "error" ? "text-destructive" :
                  store.status === "running" ? "text-primary" :
                  "text-muted-foreground"
                }`}>
                  {store.status}
                </span>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
            <div className="gw2-card p-5 lg:col-span-3">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-primary" />
                  <h2 className="text-xl font-semibold">Configuration</h2>
                </div>
                <button
                  onClick={() => store.recalculateCoverage()}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-muted hover:bg-muted/80 rounded transition-colors"
                  title="Recalculer la couverture"
                >
                  <RefreshCw className="w-4 h-4" />
                  Recalculer
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Squad size */}
                <div>
                  <label className="block text-sm font-medium mb-2">Taille d'escouade</label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={store.squadSize}
                    onChange={(e) => handleSquadSizeChange(Number(e.target.value) || 1)}
                    className="w-full px-4 py-2 bg-input border border-border rounded"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {Math.ceil(store.squadSize / 5)} groupes de 5 max
                  </p>
                </div>

                {/* Start button */}
                <div className="flex items-end">
                  <button
                    onClick={onStart}
                    disabled={store.status === "running" || store.squadSize < 1}
                    className="gw2-button w-full inline-flex items-center justify-center gap-2 px-4 py-3 disabled:opacity-50"
                  >
                    <Zap className="w-5 h-5" />
                    {store.status === "running" ? "Optimisation en cours..." : "Lancer l'optimisation"}
                  </button>
                </div>
              </div>

              <div className="mt-4 p-3 bg-muted/20 rounded text-sm text-muted-foreground">
                💡 <strong>Astuce:</strong> Glissez-déposez les joueurs entre les groupes pour ajuster manuellement la composition.
                La couverture se recalcule automatiquement.
              </div>
            </div>

            {/* Live panel */}
            <div className="gw2-card p-5">
              <h2 className="text-xl font-semibold mb-4">Live</h2>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Job ID</div>
                  <div className="text-xs font-mono break-all">{store.jobId ?? "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Temps écoulé</div>
                  <div className="text-sm font-semibold">{store.elapsedMs}ms</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Groupes</div>
                  <div className="text-sm font-semibold">{store.groups.length}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Joueurs</div>
                  <div className="text-sm font-semibold">{store.players.length}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Groups grid */}
          <div className="gw2-card p-5">
            <h2 className="text-xl font-semibold mb-4">Sous-groupes (Drag & Drop)</h2>

            {store.groups.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center py-8">
                Configurez la taille d'escouade pour initialiser les groupes.
              </div>
            ) : (
              <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))` }}>
                {store.groups.map(group => (
                  <GroupCard
                    key={group.id}
                    group={group}
                    players={store.players}
                    builds={store.builds}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Drag overlay */}
      <DragOverlay>
        {draggedPlayer ? (
          <div className="opacity-80">
            <PlayerCard player={draggedPlayer} build={store.builds.find(b => b.id === draggedPlayer.buildId)} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
