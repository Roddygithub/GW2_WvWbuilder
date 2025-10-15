/**
 * CompositionCreate Page - Minimal create form
 * Creates a new squad composition via useCreateComposition
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateComposition } from "@/hooks/useCompositions";
import { toast } from "sonner";

const PLAYSTYLES = [
  "balanced",
  "offensive",
  "defensive",
  "zerg",
  "havoc",
] as const;

type Playstyle = (typeof PLAYSTYLES)[number];

export default function CompositionCreate() {
  const navigate = useNavigate();
  const createMutation = useCreateComposition();

  const [name, setName] = useState("");
  const [squadSize, setSquadSize] = useState<number>(5);
  const [playstyle, setPlaystyle] = useState<Playstyle>("balanced");
  const [description, setDescription] = useState("");
  const [professionsText, setProfessionsText] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Please enter a name");
      return;
    }

    const professions = professionsText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    createMutation.mutate(
      {
        name,
        squad_size: squadSize,
        playstyle,
        description: description || null,
        professions,
      },
      {
        onSuccess: () => {
          toast.success("Composition created");
          navigate("/compositions");
        },
        onError: (err: any) => {
          toast.error(err?.detail || "Failed to create composition");
        },
      },
    );
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold tracking-tight text-white mb-6">
        Create Composition
      </h2>

      <form
        onSubmit={onSubmit}
        className="space-y-6 bg-slate-900/60 border border-purple-500/20 rounded-xl p-6"
      >
        {/* Name */}
        <div>
          <label className="block text-sm text-slate-300 mb-2">Name</label>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Balanced Zerg"
            className="bg-slate-800/50 border-slate-700 text-white"
          />
        </div>

        {/* Squad Size & Playstyle */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-2">
              Squad Size
            </label>
            <Input
              type="number"
              min={1}
              max={50}
              value={squadSize}
              onChange={(e) =>
                setSquadSize(parseInt(e.target.value || "0", 10))
              }
              className="bg-slate-800/50 border-slate-700 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-2">
              Playstyle
            </label>
            <select
              value={playstyle}
              onChange={(e) => setPlaystyle(e.target.value as Playstyle)}
              className="w-full rounded-md bg-slate-800/50 border border-slate-700 text-white px-3 py-2"
            >
              {PLAYSTYLES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm text-slate-300 mb-2">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            placeholder="Optional description..."
            className="w-full rounded-md bg-slate-800/50 border border-slate-700 text-white px-3 py-2"
          />
        </div>

        {/* Professions */}
        <div>
          <label className="block text-sm text-slate-300 mb-2">
            Professions (comma-separated)
          </label>
          <Input
            value={professionsText}
            onChange={(e) => setProfessionsText(e.target.value)}
            placeholder="e.g., Guardian, Warrior, Necromancer"
            className="bg-slate-800/50 border-slate-700 text-white"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Button type="submit" className="bg-purple-600 hover:bg-purple-700">
            Create
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/compositions")}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
