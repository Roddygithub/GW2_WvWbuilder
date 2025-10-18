/**
 * GW2 Profession Icons and Links
 * Icons from GW2 Wiki (official)
 */

export const PROFESSION_ICONS: Record<string, string> = {
  Guardian: "https://wiki.guildwars2.com/images/8/8c/Guardian_icon.png",
  Warrior: "https://wiki.guildwars2.com/images/4/43/Warrior_icon.png",
  Engineer: "https://wiki.guildwars2.com/images/2/27/Engineer_icon.png",
  Ranger: "https://wiki.guildwars2.com/images/4/43/Ranger_icon.png",
  Thief: "https://wiki.guildwars2.com/images/7/7a/Thief_icon.png",
  Elementalist: "https://wiki.guildwars2.com/images/a/aa/Elementalist_icon.png",
  Mesmer: "https://wiki.guildwars2.com/images/6/60/Mesmer_icon.png",
  Necromancer: "https://wiki.guildwars2.com/images/4/43/Necromancer_icon.png",
  Revenant: "https://wiki.guildwars2.com/images/b/b5/Revenant_icon.png",
};

export const PROFESSION_COLORS: Record<string, string> = {
  Guardian: "#72C1D9",
  Warrior: "#FFD166",
  Engineer: "#D09C59",
  Ranger: "#8CDC82",
  Thief: "#C08F95",
  Elementalist: "#F68A87",
  Mesmer: "#B679D5",
  Necromancer: "#52A76F",
  Revenant: "#D16E5A",
};

/**
 * Generate gw2skills.net build editor link
 * TODO: Add elite spec encoding for direct build links
 */
export function getGW2SkillsLink(
  profession: string,
  _eliteSpec?: string | null  // Prefix with _ to mark as intentionally unused
): string {
  const profMap: Record<string, string> = {
    Guardian: "guardian",
    Warrior: "warrior",
    Engineer: "engineer",
    Ranger: "ranger",
    Thief: "thief",
    Elementalist: "elementalist",
    Mesmer: "mesmer",
    Necromancer: "necromancer",
    Revenant: "revenant",
  };

  const prof = profMap[profession] || "guardian";
  
  // For elite specs, we'd need to set the specialization in the URL
  // Format: https://fr.gw2skills.net/editor/?PaQAQlZy6YbMNmNe2Lf6NKXA-e
  // For now, just link to the profession editor
  // TODO v4: Encode build with traits, weapons, skills
  return `https://fr.gw2skills.net/editor/?profession=${prof}`;
}

/**
 * Get profession icon with fallback
 */
export function getProfessionIcon(profession: string): string {
  return PROFESSION_ICONS[profession] || PROFESSION_ICONS.Guardian;
}

/**
 * Get profession color for styling
 */
export function getProfessionColor(profession: string): string {
  return PROFESSION_COLORS[profession] || "#72C1D9";
}
