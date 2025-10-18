/**
 * Optimization Builder Page
 * Interface for squad composition optimization with GW2 theme
 */

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Sword, Users, Target, Zap, CheckCircle, AlertCircle, Users2 } from "lucide-react";
import { optimizeComposition, type CompositionOptimizationResult } from "../api/builder";
import BuildCard from "../components/BuildCard";

// Types
interface OptimizationRequest {
  mode: string;
  sub_mode: string;
  player_count: number;
  manual_classes: boolean;
  selected_classes?: string[];
}

// Use the API type directly
type OptimizationResult = CompositionOptimizationResult;

const GW2_PROFESSIONS = [
  "Guardian",
  "Warrior",
  "Engineer",
  "Ranger",
  "Thief",
  "Elementalist",
  "Mesmer",
  "Necromancer",
  "Revenant",
];

const MODE_OPTIONS = {
  wvw: {
    label: "WvW (World vs World)",
    icon: "⚔️",
    submodes: [
      { value: "roaming", label: "Roaming (2-10 joueurs)" },
      { value: "zerg", label: "Zerg (30-50 joueurs)" },
      { value: "guild_raid", label: "Raid de guilde (15-30 joueurs)" },
    ],
  },
  pve: {
    label: "PvE",
    icon: "🗡️",
    submodes: [
      { value: "open_world", label: "Open World" },
      { value: "fractale", label: "Fractale (5 joueurs)" },
      { value: "raid", label: "Raid / Strike mission (10 joueurs)" },
    ],
  },
};

export default function OptimizationBuilder() {
  // State
  const [playerCount, setPlayerCount] = useState(5);
  const [mode, setMode] = useState<"wvw" | "pve">("wvw");
  const [subMode, setSubMode] = useState("roaming");
  const [manualChoice, setManualChoice] = useState(false);
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  const [result, setResult] = useState<OptimizationResult | null>(null);

  // Optimization mutation
  const optimizeMutation = useMutation({
    mutationFn: async (request: OptimizationRequest) => {
      // Map to backend format
      // Note: fixed_professions needs profession IDs (numbers), not names
      // TODO: Map profession names to IDs from GW2 API
      const backendRequest = {
        squad_size: request.player_count,
        game_type: request.mode, // mcm or pve
        game_mode: request.sub_mode, // roaming, zerg, etc.
        optimization_goals: ["boon_uptime", "healing", "damage"],
      };
      
      return optimizeComposition(backendRequest);
    },
    onSuccess: (data) => {
      setResult(data);
    },
  });

  // Handlers
  const handleModeChange = (newMode: "wvw" | "pve") => {
    setMode(newMode);
    setSubMode(MODE_OPTIONS[newMode].submodes[0].value);
  };

  const handleClassToggle = (className: string) => {
    setSelectedClasses((prev) =>
      prev.includes(className)
        ? prev.filter((c) => c !== className)
        : [...prev, className]
    );
  };

  const handleOptimize = () => {
    const request: OptimizationRequest = {
      mode,
      sub_mode: subMode,
      player_count: playerCount,
      manual_classes: manualChoice,
      selected_classes: manualChoice ? selectedClasses : undefined,
    };

    optimizeMutation.mutate(request);
  };

  const canOptimize = playerCount >= 1 && playerCount <= 50;

  return (
    <div className="min-h-screen gw2-fractal-bg gw2-tyria-pattern p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-2">
            <Sword className="h-10 w-10 text-primary" />
            <h1 className="text-4xl font-bold">Squad Optimizer</h1>
          </div>
          <p className="text-muted-foreground">
            Créez des compositions optimales pour Guild Wars 2
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Configuration du groupe */}
            <div className="gw2-card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Users className="h-6 w-6 text-primary" />
                <h2 className="text-2xl font-bold">Configuration du groupe</h2>
              </div>

              {/* Nombre de joueurs */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  🧍 Nombre de joueurs
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={playerCount}
                  onChange={(e) => setPlayerCount(parseInt(e.target.value) || 1)}
                  className="w-full px-4 py-3 bg-input border border-border rounded-lg
                           text-foreground focus:ring-2 focus:ring-primary focus:border-primary
                           transition-all"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Min: 1 | Max: 50
                </p>
              </div>

              {/* Mode de jeu */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  🎮 Mode de jeu
                </label>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(MODE_OPTIONS).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => handleModeChange(key as "wvw" | "pve")}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        mode === key
                          ? "border-primary bg-primary/10 gw2-gold-glow"
                          : "border-border bg-card hover:border-primary/50"
                      }`}
                    >
                      <div className="text-2xl mb-1">{config.icon}</div>
                      <div className="font-semibold">{config.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Sous-mode dynamique */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  🎯 Type de contenu
                </label>
                <select
                  value={subMode}
                  onChange={(e) => setSubMode(e.target.value)}
                  className="w-full px-4 py-3 bg-input border border-border rounded-lg
                           text-foreground focus:ring-2 focus:ring-primary focus:border-primary
                           transition-all cursor-pointer"
                >
                  {MODE_OPTIONS[mode].submodes.map((sm) => (
                    <option key={sm.value} value={sm.value}>
                      {sm.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Choix des classes */}
            <div className="gw2-card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Target className="h-6 w-6 text-primary" />
                <h2 className="text-2xl font-bold">Choix des classes</h2>
              </div>

              {/* Toggle manuel/automatique */}
              <div className="mb-6">
                <label className="flex items-center space-x-3 cursor-pointer p-4 rounded-lg
                               bg-muted/20 hover:bg-muted/30 transition-colors">
                  <input
                    type="checkbox"
                    checked={manualChoice}
                    onChange={(e) => {
                      setManualChoice(e.target.checked);
                      if (!e.target.checked) setSelectedClasses([]);
                    }}
                    className="w-5 h-5 rounded border-primary text-primary
                             focus:ring-2 focus:ring-primary"
                  />
                  <span className="font-medium">
                    ☑️ Je veux choisir les classes manuellement
                  </span>
                </label>

                {!manualChoice && (
                  <p className="text-sm text-muted-foreground mt-2 ml-8">
                    🧠 Le moteur choisira automatiquement les classes optimales
                  </p>
                )}
              </div>

              {/* Sélection des classes */}
              {manualChoice && (
                <div>
                  <label className="block text-sm font-medium mb-3">
                    🧙 Professions à inclure ({selectedClasses.length} sélectionnées)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {GW2_PROFESSIONS.map((profession) => (
                      <button
                        key={profession}
                        onClick={() => handleClassToggle(profession)}
                        className={`p-3 rounded-lg border-2 transition-all text-left ${
                          selectedClasses.includes(profession)
                            ? "border-primary bg-primary/10 gw2-gold-glow"
                            : "border-border bg-card hover:border-primary/50"
                        }`}
                      >
                        <div className="font-semibold text-sm">{profession}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Bouton d'optimisation */}
            <button
              onClick={handleOptimize}
              disabled={!canOptimize || optimizeMutation.isPending}
              className="gw2-button w-full py-4 text-lg flex items-center justify-center space-x-3
                       disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Zap className="h-6 w-6" />
              <span>
                {optimizeMutation.isPending
                  ? "Optimisation en cours..."
                  : "🚀 Lancer l'optimisation"}
              </span>
            </button>

            {/* Erreur */}
            {optimizeMutation.isError && (
              <div className="gw2-card p-4 bg-destructive/10 border-destructive">
                <div className="flex items-center space-x-2 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">
                    Erreur: {(optimizeMutation.error as Error).message}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-1">
            {result ? (
              <div className="gw2-card gw2-gold-glow p-6 sticky top-8">
                <div className="flex items-center space-x-3 mb-6">
                  <CheckCircle className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-bold">Résultats</h2>
                </div>

                {/* Score global */}
                <div className="mb-6 p-4 bg-primary/10 rounded-lg border border-primary">
                  <div className="text-sm text-muted-foreground mb-1">
                    Score d'efficacité
                  </div>
                  <div className="text-4xl font-bold text-primary">
                    {Math.round(result.score * 100)}%
                  </div>
                </div>

                {/* Métriques */}
                <div className="space-y-3 mb-6">
                  <h3 className="font-semibold text-sm text-muted-foreground">
                    Métriques
                  </h3>
                  {Object.entries(result.metrics).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize">
                          {key.replace("_", " ")}
                        </span>
                        <span className="font-semibold text-primary">
                          {Math.round(value * 100)}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Distribution des rôles */}
                <div className="mb-6">
                  <h3 className="font-semibold text-sm text-muted-foreground mb-3">
                    Distribution des rôles
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(result.role_distribution).map(
                      ([role, count]) => (
                        <div
                          key={role}
                          className="flex justify-between items-center p-2 bg-muted/20 rounded"
                        >
                          <span className="text-sm capitalize">
                            {role.replace("_", " ")}
                          </span>
                          <span className="font-bold text-primary">{count}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Couverture des boons */}
                {result.boon_coverage && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-3">
                      Couverture des boons
                    </h3>
                    <div className="space-y-2">
                      {Object.entries(result.boon_coverage).map(
                        ([boon, coverage]) => (
                          <div key={boon} className="flex justify-between text-sm">
                            <span className="capitalize">{boon}</span>
                            <span className="text-primary">
                              {Math.round(coverage * 100)}%
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* Squad by Subgroups */}
                {result.subgroups && result.subgroups.length > 0 ? (
                  <div className="mt-6 pt-6 border-t border-border">
                    <h3 className="font-semibold text-sm text-muted-foreground mb-4 flex items-center gap-2">
                      <Users2 className="w-4 h-4" />
                      Votre Squad ({result.composition.squad_size} joueurs, {result.subgroups.length} groupes)
                    </h3>
                    
                    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                      {result.subgroups.map((subgroup: any) => {
                        // Get members for this subgroup
                        const groupMembers = result.composition.members?.filter((m: any) =>
                          subgroup.members.includes(m.id)
                        );

                        return (
                          <div key={subgroup.group_number} className="bg-muted/5 rounded-lg p-3 border border-border">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-semibold text-sm">
                                Groupe {subgroup.group_number} ({subgroup.size} joueurs)
                              </h4>
                              <div className="text-xs text-muted-foreground">
                                Boons: {Math.round(subgroup.avg_boon_coverage * 100)}%
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              {groupMembers?.map((member: any) => (
                                <BuildCard
                                  key={member.id}
                                  professionName={member.profession_name}
                                  eliteSpecializationName={member.elite_specialization_name}
                                  roleType={member.role_type}
                                  isCommander={member.is_commander}
                                  playerNumber={member.id}
                                />
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : result.composition.members && result.composition.members.length > 0 && (
                  // Fallback if no subgroups (old API response)
                  <div className="mt-6 pt-6 border-t border-border">
                    <h3 className="font-semibold text-sm text-muted-foreground mb-3">
                      Votre Squad ({result.composition.members.length} membres)
                    </h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {result.composition.members.map((member) => (
                        <BuildCard
                          key={member.id}
                          professionName={member.profession_name}
                          eliteSpecializationName={member.elite_specialization_name}
                          roleType={member.role_type}
                          isCommander={member.is_commander}
                          playerNumber={member.id}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="mt-6 pt-6 border-t border-border space-y-3">
                  <button
                    className="gw2-button w-full py-2"
                    onClick={() => {
                      // TODO: Implement save composition
                      alert("Fonctionnalité de sauvegarde à venir!");
                    }}
                  >
                    💾 Sauvegarder la composition
                  </button>
                  <button
                    className="gw2-button-secondary w-full py-2"
                    onClick={() => setResult(null)}
                  >
                    🔄 Nouvelle optimisation
                  </button>
                </div>
              </div>
            ) : (
              <div className="gw2-card p-6 sticky top-8">
                <div className="text-center text-muted-foreground">
                  <Zap className="h-12 w-12 mx-auto mb-4 opacity-30" />
                  <p className="font-medium">Aucun résultat</p>
                  <p className="text-sm mt-2">
                    Configurez votre groupe et lancez l'optimisation pour voir les
                    résultats ici.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
