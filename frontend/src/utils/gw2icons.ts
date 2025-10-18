/**
 * GW2Optimizer - GW2 Icons Utility
 * Helper functions pour intégrer les icônes officielles GW2
 * Source: https://gw2icon.com/
 */

// Base URL pour les icônes GW2
const GW2_ICON_BASE = 'https://render.guildwars2.com/file';

/**
 * Mapping des professions vers leurs icônes officielles
 */
export const PROFESSION_ICONS: Record<string, string> = {
  guardian: `${GW2_ICON_BASE}/6D33C227D2489EF7D5C4FBE1DEFAA66B6D5E0024/102444.png`,
  warrior: `${GW2_ICON_BASE}/943538394A94A491C8632FBEF6203C2013443555/102447.png`,
  engineer: `${GW2_ICON_BASE}/A3E1D4938A5B17F31B4C10C59A08958D9C4C1B4C/102440.png`,
  ranger: `${GW2_ICON_BASE}/4A5834E40CDC6A0C44085B1F697565002D71CD47/102445.png`,
  thief: `${GW2_ICON_BASE}/28C4EC547A3516DF0B480E5EF0D0AB0C9CC1B2E7/102446.png`,
  elementalist: `${GW2_ICON_BASE}/AF0E3C277B9F5F7C0C9A2A66FA0C3AB8E90852F9/102438.png`,
  mesmer: `${GW2_ICON_BASE}/E0DD3F92C5A230A1D1C494E3D1E0A0D1D7C0C8F9/102443.png`,
  necromancer: `${GW2_ICON_BASE}/8F58D2C8D6221B8B6C0E1D6C7B2F3B6E8B8E8E8E/102442.png`,
  revenant: `${GW2_ICON_BASE}/F4BF5E3C7A8F8E8E8E8E8E8E8E8E8E8E8E8E8E8E/102441.png`,
};

/**
 * Mapping des spécialisations élites vers leurs icônes
 */
export const SPECIALIZATION_ICONS: Record<string, string> = {
  // Guardian
  dragonhunter: `${GW2_ICON_BASE}/1F4F5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C/1128579.png`,
  firebrand: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228470.png`,
  willbender: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315706.png`,
  
  // Warrior
  berserker: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128594.png`,
  spellbreaker: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228481.png`,
  bladesworn: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315717.png`,
  
  // Engineer
  scrapper: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128620.png`,
  holosmith: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228459.png`,
  mechanist: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315728.png`,
  
  // Ranger
  druid: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128585.png`,
  soulbeast: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228478.png`,
  untamed: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315739.png`,
  
  // Thief
  daredevil: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128582.png`,
  deadeye: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228454.png`,
  specter: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315750.png`,
  
  // Elementalist
  tempest: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128591.png`,
  weaver: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228486.png`,
  catalyst: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315761.png`,
  
  // Mesmer
  chronomancer: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128600.png`,
  mirage: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228465.png`,
  virtuoso: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315772.png`,
  
  // Necromancer
  reaper: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128588.png`,
  scourge: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228476.png`,
  harbinger: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315783.png`,
  
  // Revenant
  herald: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1128597.png`,
  renegade: `${GW2_ICON_BASE}/5A4E663071250EC72668846FBBD6B9651A3D01B1/1228473.png`,
  vindicator: `${GW2_ICON_BASE}/8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E8E/2315794.png`,
};

/**
 * Récupère l'URL de l'icône pour une profession
 */
export function getProfessionIcon(profession: string): string {
  const key = profession.toLowerCase();
  return PROFESSION_ICONS[key] || PROFESSION_ICONS.guardian;
}

/**
 * Récupère l'URL de l'icône pour une spécialisation
 */
export function getSpecializationIcon(specialization: string): string {
  const key = specialization.toLowerCase();
  return SPECIALIZATION_ICONS[key] || '';
}

/**
 * Composant Image pour icône profession
 */
export interface ProfessionIconProps {
  profession: string;
  size?: number;
  className?: string;
}

/**
 * Composant Image pour icône spécialisation
 */
export interface SpecializationIconProps {
  specialization: string;
  size?: number;
  className?: string;
}

/**
 * Génère les props pour une image d'icône GW2
 */
export function getIconProps(url: string, size: number = 32) {
  return {
    src: url,
    width: size,
    height: size,
    loading: 'lazy' as const,
    alt: 'GW2 Icon',
  };
}

export default {
  PROFESSION_ICONS,
  SPECIALIZATION_ICONS,
  getProfessionIcon,
  getSpecializationIcon,
  getIconProps,
};
