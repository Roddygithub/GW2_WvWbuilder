/**
 * Meta Evolution Dashboard — GW2_WvWBuilder v4.3
 * 
 * Real-time visualization of AI-driven meta analysis and weight adjustments.
 * Displays temporal graphs, synergy heatmaps, history timeline, and nerf/buff badges.
 */

import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  getWeights,
  getSynergies,
  getHistory,
  getStats,
  getRecentChanges,
  WeightInfo,
  SynergyInfo,
  HistoryEntry,
  MetaStats,
  PatchChange,
} from '../api/metaEvolution';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { TrendingDown, TrendingUp, Activity, History, Network } from 'lucide-react';

export default function MetaEvolutionPage() {
  const [selectedSpec, setSelectedSpec] = useState<string | null>(null);

  // Fetch data
  const { data: stats, isLoading: statsLoading } = useQuery<MetaStats>({
    queryKey: ['meta-stats'],
    queryFn: getStats,
    refetchInterval: 30000, // Refresh every 30s
  });

  const { data: weights, isLoading: weightsLoading } = useQuery<WeightInfo[]>({
    queryKey: ['meta-weights'],
    queryFn: getWeights,
    refetchInterval: 30000,
  });

  const { data: synergies, isLoading: synergiesLoading } = useQuery<SynergyInfo[]>({
    queryKey: ['meta-synergies'],
    queryFn: () => getSynergies(0.5, 50),
    refetchInterval: 30000,
  });

  const { data: history, isLoading: historyLoading } = useQuery<HistoryEntry[]>({
    queryKey: ['meta-history'],
    queryFn: () => getHistory(100),
    refetchInterval: 60000, // Refresh every 60s
  });

  const { data: recentChanges } = useQuery<PatchChange[]>({
    queryKey: ['recent-changes'],
    queryFn: () => getRecentChanges(30),
    refetchInterval: 60000,
  });

  // Prepare timeline data for graph
  const timelineData = React.useMemo(() => {
    if (!history) return [];

    const data: any[] = [];
    const specWeights: { [spec: string]: number } = {};

    // Initialize all specs with 1.0
    weights?.forEach(w => {
      specWeights[w.spec] = 1.0;
    });

    history.forEach(entry => {
      const timestamp = new Date(entry.timestamp).toLocaleDateString();
      
      // Apply adjustments
      entry.adjustments.forEach(adj => {
        specWeights[adj.spec] = adj.new_weight;
      });

      // Create data point
      data.push({
        timestamp,
        ...specWeights,
      });
    });

    return data;
  }, [history, weights]);

  // Get specs with recent changes
  const recentlyChanged = React.useMemo(() => {
    if (!history || history.length === 0) return [];
    
    const latest = history[history.length - 1];
    return latest.adjustments.map(adj => ({
      spec: adj.spec,
      delta: adj.delta,
      changeType: adj.change_type,
    }));
  }, [history]);

  if (statsLoading || weightsLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading meta evolution data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Meta Evolution Dashboard</h1>
          <p className="text-muted-foreground">
            AI-powered meta analysis for Guild Wars 2 WvW
          </p>
        </div>
        {stats && (
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Last Update</p>
            <p className="font-medium">
              {stats.last_update 
                ? new Date(stats.last_update).toLocaleString()
                : 'Never'}
            </p>
          </div>
        )}
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Specs</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_specs}</div>
              <p className="text-xs text-muted-foreground">
                Elite specializations tracked
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Weight</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avg_weight.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Across all specializations
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Synergies</CardTitle>
              <Network className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_synergies}</div>
              <p className="text-xs text-muted-foreground">
                Active synergy pairs
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">History</CardTitle>
              <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.history_entries}</div>
              <p className="text-xs text-muted-foreground">
                Adjustments tracked
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Changes Alert */}
      {recentlyChanged.length > 0 && (
        <Alert>
          <Activity className="h-4 w-4" />
          <AlertTitle>Recent Meta Changes Detected</AlertTitle>
          <AlertDescription className="flex flex-wrap gap-2 mt-2">
            {recentlyChanged.map((change, idx) => (
              <Badge
                key={idx}
                variant={change.delta < 0 ? 'destructive' : 'default'}
              >
                {change.delta < 0 ? (
                  <TrendingDown className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingUp className="h-3 w-3 mr-1" />
                )}
                {change.spec} ({change.delta > 0 ? '+' : ''}{change.delta.toFixed(2)})
              </Badge>
            ))}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="timeline" className="space-y-4">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="weights">Current Weights</TabsTrigger>
          <TabsTrigger value="synergies">Synergies</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Timeline Graph */}
        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Weight Evolution Over Time</CardTitle>
              <CardDescription>
                Track how specialization weights have changed with each patch
              </CardDescription>
            </CardHeader>
            <CardContent>
              {timelineData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={timelineData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis domain={[0.5, 1.5]} />
                    <Tooltip />
                    <Legend />
                    {stats?.top_specs.slice(0, 5).map((spec, idx) => (
                      <Line
                        key={spec.spec}
                        type="monotone"
                        dataKey={spec.spec}
                        stroke={`hsl(${idx * 72}, 70%, 50%)`}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No historical data available yet. Run the adaptive meta system to start tracking.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Current Weights */}
        <TabsContent value="weights" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Top Specs */}
            <Card>
              <CardHeader>
                <CardTitle>Top Weighted Specs</CardTitle>
                <CardDescription>Currently strongest in meta</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {stats?.top_specs.map((spec, idx) => (
                    <div key={spec.spec} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">
                          #{idx + 1}
                        </span>
                        <span className="capitalize font-medium">{spec.spec}</span>
                      </div>
                      <Badge variant="default">{spec.weight.toFixed(2)}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Bottom Specs */}
            <Card>
              <CardHeader>
                <CardTitle>Bottom Weighted Specs</CardTitle>
                <CardDescription>Recently nerfed or underperforming</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {stats?.bottom_specs.map((spec, idx) => (
                    <div key={spec.spec} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">
                          #{stats.total_specs - stats.bottom_specs.length + idx + 1}
                        </span>
                        <span className="capitalize font-medium">{spec.spec}</span>
                      </div>
                      <Badge variant="destructive">{spec.weight.toFixed(2)}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Synergies */}
        <TabsContent value="synergies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Synergy Pairs</CardTitle>
              <CardDescription>
                Specializations that work well together in WvW
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {synergies?.slice(0, 15).map((syn, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 border rounded">
                    <div className="flex items-center gap-2">
                      <Network className="h-4 w-4 text-muted-foreground" />
                      <span className="capitalize">{syn.spec1}</span>
                      <span className="text-muted-foreground">↔</span>
                      <span className="capitalize">{syn.spec2}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{ width: `${syn.score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-12 text-right">
                        {(syn.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Adjustment History</CardTitle>
              <CardDescription>
                Complete audit trail of all weight adjustments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {history?.slice().reverse().slice(0, 10).map((entry, idx) => (
                  <div key={idx} className="border-l-2 border-primary pl-4 py-2">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">
                        {new Date(entry.timestamp).toLocaleString()}
                      </span>
                      <Badge variant="outline">{entry.source}</Badge>
                    </div>
                    {entry.adjustments.map((adj, adjIdx) => (
                      <div key={adjIdx} className="mb-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="capitalize font-medium">{adj.spec}</span>
                          <Badge
                            variant={adj.delta < 0 ? 'destructive' : 'default'}
                            className="text-xs"
                          >
                            {adj.delta > 0 ? '+' : ''}{adj.delta.toFixed(2)}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {adj.old_weight.toFixed(2)} → {adj.new_weight.toFixed(2)}
                          </span>
                        </div>
                        {adj.reasoning && (
                          <p className="text-sm text-muted-foreground italic">
                            "{adj.reasoning}"
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
