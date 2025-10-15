/**
 * Builder V2 - Refonte complète
 * Flux: Squad Size → Game Type (McM/PvE) → Sub-Mode → Fixed Classes (optional) → Optimize
 * Le moteur choisit automatiquement les rôles et spécialisations
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  Users,
  Swords,
  Shield,
  Loader2,
  Check,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import OptimizationResults from '@/components/OptimizationResults';
import CompositionMembersList from '@/components/CompositionMembersList';
import {
  useOptimizeComposition,
  useGameModes,
} from '@/hooks/useBuilder';
import type { CompositionOptimizationRequest } from '@/api/builder';
import apiClient from '@/api/client';

interface Profession {
  id: number;
  name: string;
  color: string;
}

export default function BuilderV2Page() {
  const [squadSize, setSquadSize] = useState(10);
  const [gameType, setGameType] = useState<'wvw' | 'pve'>('wvw');
  const [gameMode, setGameMode] = useState('zerg');
  const [wantChooseClasses, setWantChooseClasses] = useState(false);
  const [selectedProfessions, setSelectedProfessions] = useState<number[]>([]);
  const [professions, setProfessions] = useState<Profession[]>([]);

  const optimize = useOptimizeComposition();
  const { data: modesData } = useGameModes();

  // Charger les professions disponibles
  useEffect(() => {
    const loadProfessions = async () => {
      try {
        const response = await apiClient.get('/builder/professions') as any;
        setProfessions(response.data?.professions || []);
      } catch (error) {
        console.error('Failed to load professions:', error);
      }
    };
    loadProfessions();
  }, []);

  // Récupérer les modes disponibles pour le game type sélectionné
  const availableModes = (modesData as any)?.game_types?.[gameType]?.modes || [];

  // Mettre à jour le mode quand on change de game type
  useEffect(() => {
    if (availableModes.length > 0) {
      setGameMode(availableModes[0].id);
    }
  }, [gameType, availableModes]);

  // Récupérer les infos du mode sélectionné
  const selectedModeInfo = availableModes.find((m: any) => m.id === gameMode);

  const handleOptimize = () => {
    const request: CompositionOptimizationRequest = {
      squad_size: squadSize,
      game_type: gameType,
      game_mode: gameMode,
      fixed_professions: wantChooseClasses && selectedProfessions.length > 0 
        ? selectedProfessions 
        : undefined,
    };

    optimize.mutate(request);
  };

  const toggleProfession = (profId: number) => {
    setSelectedProfessions(prev =>
      prev.includes(profId)
        ? prev.filter(id => id !== profId)
        : [...prev, profId]
    );
  };

  const professionColors: Record<string, string> = {
    blue: 'from-blue-500 to-cyan-500',
    red: 'from-red-500 to-pink-500',
    green: 'from-green-500 to-emerald-500',
    yellow: 'from-yellow-500 to-orange-500',
    amber: 'from-amber-500 to-yellow-500',
    gray: 'from-gray-500 to-slate-500',
    purple: 'from-purple-500 to-violet-500',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 mb-2">
            Optimiseur de Composition GW2
          </h1>
          <p className="text-slate-400 text-lg">
            McM & PvE - Le moteur choisit automatiquement les rôles et spécialisations optimales
          </p>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Configuration Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Étape 1: Squad Size */}
            <Card className="bg-slate-900/50 border-purple-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-slate-200">
                  <Users className="w-5 h-5 text-purple-400" />
                  <span>Étape 1: Nombre de joueurs</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="squad-size" className="text-slate-300">
                    Taille de la squad
                  </Label>
                  <Input
                    id="squad-size"
                    type="number"
                    min="1"
                    max="50"
                    value={squadSize}
                    onChange={(e) => setSquadSize(parseInt(e.target.value) || 1)}
                    className="bg-slate-800 border-slate-700 text-lg"
                  />
                  <p className="text-xs text-slate-400">
                    Entre 1 et 50 joueurs
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Étape 2: Game Type & Mode */}
            <Card className="bg-slate-900/50 border-purple-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-slate-200">
                  <Swords className="w-5 h-5 text-purple-400" />
                  <span>Étape 2: Type de jeu et mode</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Game Type */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Type de jeu</Label>
                  <div className="grid grid-cols-2 gap-3">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setGameType('wvw')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        gameType === 'wvw'
                          ? 'bg-purple-500/20 border-purple-500 shadow-lg shadow-purple-500/20'
                          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <Shield className={`w-8 h-8 mx-auto mb-2 ${
                        gameType === 'wvw' ? 'text-purple-400' : 'text-slate-400'
                      }`} />
                      <p className={`font-semibold ${
                        gameType === 'wvw' ? 'text-purple-300' : 'text-slate-300'
                      }`}>
                        McM (WvW)
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        World vs World
                      </p>
                    </motion.button>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setGameType('pve')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        gameType === 'pve'
                          ? 'bg-purple-500/20 border-purple-500 shadow-lg shadow-purple-500/20'
                          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <Swords className={`w-8 h-8 mx-auto mb-2 ${
                        gameType === 'pve' ? 'text-purple-400' : 'text-slate-400'
                      }`} />
                      <p className={`font-semibold ${
                        gameType === 'pve' ? 'text-purple-300' : 'text-slate-300'
                      }`}>
                        PvE
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Player vs Environment
                      </p>
                    </motion.button>
                  </div>
                </div>

                {/* Game Mode */}
                <div className="space-y-2">
                  <Label htmlFor="game-mode" className="text-slate-300">
                    Mode de jeu
                  </Label>
                  <Select value={gameMode} onValueChange={setGameMode}>
                    <SelectTrigger className="bg-slate-800 border-slate-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {availableModes.map((mode: any) => (
                        <SelectItem key={mode.id} value={mode.id}>
                          {mode.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {selectedModeInfo && (
                    <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30 mt-2">
                      <p className="text-sm text-slate-300">{selectedModeInfo.description}</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {selectedModeInfo.emphasis?.map((e: string) => (
                          <Badge key={e} variant="outline" className="text-xs">
                            {e}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Étape 3: Fixed Classes (Optional) */}
            <Card className="bg-slate-900/50 border-purple-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-slate-200">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  <span>Étape 3: Classes (optionnel)</span>
                </CardTitle>
                <CardDescription>
                  Le moteur choisira automatiquement les rôles et spécialisations optimales
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="choose-classes"
                    checked={wantChooseClasses}
                    onChange={(e) => {
                      setWantChooseClasses(e.target.checked);
                      if (!e.target.checked) setSelectedProfessions([]);
                    }}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-purple-600 focus:ring-purple-500"
                  />
                  <Label
                    htmlFor="choose-classes"
                    className="text-slate-300 cursor-pointer"
                  >
                    Je veux choisir les classes
                  </Label>
                </div>

                {wantChooseClasses && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="grid grid-cols-3 gap-3"
                  >
                    {professions.map((prof) => {
                      const isSelected = selectedProfessions.includes(prof.id);
                      const gradient = professionColors[prof.color] || 'from-slate-500 to-slate-600';
                      
                      return (
                        <motion.button
                          key={prof.id}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => toggleProfession(prof.id)}
                          className={`relative p-3 rounded-lg border-2 transition-all ${
                            isSelected
                              ? 'border-purple-500 shadow-lg shadow-purple-500/20'
                              : 'border-slate-700 hover:border-slate-600'
                          }`}
                        >
                          {isSelected && (
                            <div className="absolute top-1 right-1">
                              <Check className="w-4 h-4 text-purple-400" />
                            </div>
                          )}
                          <div className={`w-12 h-12 mx-auto rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center text-white font-bold text-lg mb-2`}>
                            {prof.name.charAt(0)}
                          </div>
                          <p className="text-xs font-medium text-slate-300 text-center">
                            {prof.name}
                          </p>
                        </motion.button>
                      );
                    })}
                  </motion.div>
                )}

                {wantChooseClasses && selectedProfessions.length > 0 && (
                  <p className="text-sm text-slate-400">
                    {selectedProfessions.length} classe{selectedProfessions.length > 1 ? 's' : ''} sélectionnée{selectedProfessions.length > 1 ? 's' : ''}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Action Panel */}
          <div className="space-y-6">
            {/* Optimize Button */}
            <Card className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 border-purple-500/50">
              <CardContent className="pt-6">
                <Button
                  size="lg"
                  onClick={handleOptimize}
                  disabled={optimize.isPending}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-6 text-lg shadow-lg shadow-purple-500/50"
                >
                  {optimize.isPending ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Optimisation...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Optimiser la composition
                      <ChevronRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Configuration Summary */}
            <Card className="bg-slate-900/50 border-purple-500/30">
              <CardHeader>
                <CardTitle className="text-sm text-slate-300">Récapitulatif</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Joueurs:</span>
                  <span className="text-slate-200 font-medium">{squadSize}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Type:</span>
                  <span className="text-slate-200 font-medium uppercase">{gameType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Mode:</span>
                  <span className="text-slate-200 font-medium capitalize">{gameMode}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Classes fixes:</span>
                  <span className="text-slate-200 font-medium">
                    {wantChooseClasses ? selectedProfessions.length : 'Auto'}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Results */}
        <AnimatePresence>
          {optimize.isSuccess && optimize.data && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Card className="bg-slate-900/50 border-purple-500/30">
                <CardHeader>
                  <CardTitle className="text-2xl text-slate-200">Résultats de l'optimisation</CardTitle>
                  <CardDescription>
                    Composition générée pour {optimize.data.composition.squad_size} joueurs
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <OptimizationResults
                    score={Math.round(optimize.data.score * 100)}
                    synergy={{
                      boons: Object.fromEntries(
                        Object.entries(optimize.data.boon_coverage).map(([k, v]) => [
                          k,
                          Math.round((v as number) * 100),
                        ])
                      ),
                      healing: Math.round((optimize.data.metrics.healing || 0) * 100),
                      damage: Math.round((optimize.data.metrics.damage || 0) * 100),
                      survivability: Math.round((optimize.data.metrics.survivability || 0) * 100),
                      crowdControl: Math.round((optimize.data.metrics.crowd_control || 0) * 100),
                    }}
                    suggestions={optimize.data.notes?.filter((n) => n.includes('✓')) || []}
                    warnings={optimize.data.notes?.filter((n) => n.includes('⚠')) || []}
                  />

                  {/* Role Distribution */}
                  <div className="mt-6 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                    <h4 className="text-lg font-semibold text-slate-200 mb-3">
                      Distribution des rôles
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(optimize.data.role_distribution).map(([role, count]) => (
                        <div
                          key={role}
                          className="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30"
                        >
                          <p className="text-xs text-slate-400 capitalize">
                            {role.replace('_', ' ')}
                          </p>
                          <p className="text-2xl font-bold text-purple-300">{count}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Squad Members List */}
              {optimize.data.composition.members && optimize.data.composition.members.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mt-6"
                >
                  <CompositionMembersList
                    members={optimize.data.composition.members}
                    squadSize={optimize.data.composition.squad_size}
                  />
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
