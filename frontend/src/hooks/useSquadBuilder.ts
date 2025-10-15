import { useState, useMemo, useCallback } from "react";
import type {
  SquadMember,
  Role,
  Composition as CompositionType,
} from "@/types/squad";
import { ALL_ROLES, PROFESSION_ROLES } from "@/data/professions";

interface UseSquadBuilderProps {
  initialComposition?: CompositionType;
}

export function useSquadBuilder({ initialComposition }: UseSquadBuilderProps) {
  const [composition, setComposition] = useState<SquadMember[]>(
    initialComposition?.professions?.map((prof, index) => ({
      id: Date.now() + index,
      profession: prof,
    })) || [],
  );

  const addProfession = useCallback((profession: string) => {
    const newMember: SquadMember = { id: Date.now(), profession };
    setComposition((prev) => [...prev, newMember]);
  }, []);

  const removeProfession = useCallback((id: number) => {
    setComposition((prev) => prev.filter((member) => member.id !== id));
  }, []);

  const roleCounts = useMemo(() => {
    const counts = {} as Record<Role, number>;
    (ALL_ROLES as readonly Role[]).forEach((role) => {
      counts[role] = 0;
    });

    for (const member of composition) {
      const roles = PROFESSION_ROLES[member.profession] || [];
      roles.forEach((role) => {
        if (role in counts) {
          counts[role as Role] = (counts[role as Role] || 0) + 1;
        }
      });
    }

    return counts;
  }, [composition]);

  // Fonction pour réinitialiser complètement la composition
  const clearComposition = useCallback(() => {
    setComposition([]);
  }, []);

  return {
    composition,
    setComposition,
    addProfession,
    removeProfession,
    roleCounts,
    clearComposition,
  };
}
