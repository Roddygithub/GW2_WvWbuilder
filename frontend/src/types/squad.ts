export interface SquadMember {
  id: number;
  profession: string;
}

export type Role =
  | "Healer"
  | "Support"
  | "DPS"
  | "CC"
  | "Roamer"
  | "Quickness"
  | "Alacrity"
  | "Might"
  | "Fury"
  | "Protection"
  | "Resolution"
  | "Resistance"
  | "Stability"
  | "Aegis"
  | "Vigor"
  | "Barrier"
  | "Boon Strip"
  | "Spirits"
  | "Banner"
  | "Damage"
  | "Tank";

export interface Composition {
  id: number;
  name: string;
  description: string | null;
  squad_size: number;
  playstyle: "balanced" | "offensive" | "defensive" | "zerg" | "havoc";
  professions: string[];
  created_at: string;
  updated_at: string;
}

export interface ProfessionData {
  name: string;
  roles: Role[];
  icon: string;
  description: string;
}
