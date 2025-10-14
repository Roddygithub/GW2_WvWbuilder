import type { ProfessionData } from "@/types/squad";

export const ALL_PROFESSIONS = [
  'Guardian',
  'Warrior',
  'Engineer',
  'Ranger',
  'Thief',
  'Elementalist',
  'Necromancer',
  'Mesmer',
  'Revenant'
] as const;

export const ALL_ROLES = [
  'Damage',
  'Support',
  'Healer',
  'Tank',
  'Quickness',
  'Alacrity',
  'Might',
  'Fury',
  'Protection',
  'Resolution',
  'Resistance',
  'Stability',
  'Aegis',
  'Vigor'
] as const;

export const PROFESSION_ROLES: Record<string, string[]> = {
  Guardian: ['Support', 'Healer', 'Quickness', 'Aegis', 'Stability'],
  Warrior: ['Damage', 'Support', 'Might', 'Banner'],
  Engineer: ['Damage', 'Support', 'Alacrity', 'Quickness', 'Might'],
  Ranger: ['Damage', 'Support', 'Healer', 'Spirits'],
  Thief: ['Damage', 'Quickness', 'Alacrity'],
  Elementalist: ['Damage', 'Support', 'Healer', 'Might', 'Fury'],
  Necromancer: ['Damage', 'Support', 'Barrier', 'Quickness'],
  Mesmer: ['Support', 'Quickness', 'Alacrity', 'Boon Strip'],
  Revenant: ['Damage', 'Support', 'Alacrity', 'Might', 'Stability']
};

export const PROFESSIONS_DATA: Record<string, ProfessionData> = {
  Guardian: {
    name: 'Guardian',
    icon: '🛡️',
    roles: ['Support', 'Healer', 'Quickness', 'Aegis', 'Stability'],
    description: 'A versatile profession with strong defensive and support capabilities.'
  },
  Warrior: {
    name: 'Warrior',
    icon: '⚔️',
    roles: ['Damage', 'Support', 'Might', 'Banner'],
    description: 'A strong melee fighter with powerful offensive and team support abilities.'
  },
  Engineer: {
    name: 'Engineer',
    icon: '🔧',
    roles: ['Damage', 'Support', 'Alacrity', 'Quickness', 'Might'],
    description: 'A versatile profession with a wide range of gadgets and tools.'
  },
  Ranger: {
    name: 'Ranger',
    icon: '🏹',
    roles: ['Damage', 'Support', 'Healer', 'Spirits'],
    description: 'A nature-based profession that fights alongside pets and spirits.'
  },
  Thief: {
    name: 'Thief',
    icon: '🗡️',
    roles: ['Damage', 'Quickness', 'Alacrity'],
    description: 'A highly mobile profession focused on stealth and burst damage.'
  },
  Elementalist: {
    name: 'Elementalist',
    icon: '🔥',
    roles: ['Damage', 'Support', 'Healer', 'Might', 'Fury'],
    description: 'A master of the four elements with powerful area effects.'
  },
  Necromancer: {
    name: 'Necromancer',
    icon: '💀',
    roles: ['Damage', 'Support', 'Barrier', 'Quickness'],
    description: 'A dark magic user who manipulates life force and death.'
  },
  Mesmer: {
    name: 'Mesmer',
    icon: '✨',
    roles: ['Support', 'Quickness', 'Alacrity', 'Boon Strip'],
    description: 'A master of illusions and manipulation of the battlefield.'
  },
  Revenant: {
    name: 'Revenant',
    icon: '👻',
    roles: ['Damage', 'Support', 'Alacrity', 'Might', 'Stability'],
    description: 'A heavy armor profession that channels legendary powers.'
  }
};

export const ROLE_ICONS: Record<string, string> = {
  Damage: '⚔️',
  Support: '🛡️',
  Healer: '💚',
  Tank: '🛡️',
  Quickness: '⚡',
  Alacrity: '⏳',
  Might: '💪',
  Fury: '😠',
  Protection: '🛡️',
  Resolution: '✨',
  Resistance: '✨',
  Stability: '🛡️',
  Aegis: '✨',
  Vigor: '🏃',
  Barrier: '🛡️',
  'Boon Strip': '🧹',
  'Spirits': '🌿',
  'Banner': '🏴'
};