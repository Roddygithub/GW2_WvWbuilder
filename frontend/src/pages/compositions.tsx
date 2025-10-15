/**
 * Compositions Page - Real Data Integration
 * Displays and manages squad compositions with CRUD operations
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Layers } from "lucide-react";
import { useCompositions, useDeleteComposition } from '@/hooks/useCompositions';
import LoadingState from '@/components/LoadingState';
import ErrorState from '@/components/ErrorState';
import EmptyState from '@/components/EmptyState';
import { GW2Card } from '@/components/gw2/GW2Card';

export default function CompositionsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: compositions, isLoading, isError, error, refetch } = useCompositions();
  const deleteMutation = useDeleteComposition();

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this composition?')) {
      deleteMutation.mutate(id);
    }
  };

  // Filter compositions based on search
  const filteredCompositions = compositions?.filter((comp) =>
    comp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    comp.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return <LoadingState message="Loading compositions..." />;
  }

  if (isError) {
    return (
      <ErrorState
        message={error?.message || 'Failed to load compositions'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between space-y-4 sm:flex-row sm:items-center sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Saved Compositions</h2>
          <p className="text-muted-foreground">
            Browse and manage your saved squad compositions
          </p>
        </div>
        <Button>Create New</Button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search compositions..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 md:w-[300px]"
        />
      </div>

      {/* Empty State */}
      {filteredCompositions && filteredCompositions.length === 0 && (
        <EmptyState
          title="No Compositions Found"
          message={searchQuery ? "No compositions match your search" : "Create your first squad composition to get started"}
          actionLabel="Create Composition"
          icon={Layers}
        />
      )}

      {/* Compositions Grid */}
      {filteredCompositions && filteredCompositions.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
        >
          {filteredCompositions.map((comp) => (
            <GW2Card key={comp.id} hoverable>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-1">{comp.name}</h3>
                  <p className="text-sm text-slate-400">
                    {comp.squad_size} players • {comp.playstyle}
                  </p>
                </div>
              </div>

              {comp.description && (
                <p className="text-sm text-slate-300 mb-4 line-clamp-2">
                  {comp.description}
                </p>
              )}

              <div className="flex flex-wrap gap-2 mb-4">
                {comp.professions.slice(0, 5).map((prof, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 text-xs rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30"
                  >
                    {prof}
                  </span>
                ))}
                {comp.professions.length > 5 && (
                  <span className="px-2 py-1 text-xs rounded-full bg-slate-700/50 text-slate-400">
                    +{comp.professions.length - 5} more
                  </span>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                <span className="text-xs text-slate-400">
                  Updated {new Date(comp.updated_at).toLocaleDateString()}
                </span>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    View
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(comp.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </GW2Card>
          ))}
        </motion.div>
      )}
    </div>
  )
}
