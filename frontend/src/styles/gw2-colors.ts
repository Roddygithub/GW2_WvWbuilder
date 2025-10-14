/**
 * Guild Wars 2 Color Palette
 * Official-inspired colors for immersive UI
 */

export const gw2Colors = {
  // Primary: Gold & Amber
  gold: {
    50: '#FFF8E1',
    100: '#FFECB3',
    200: '#FFE082',
    300: '#FFD54F',
    400: '#FFCA28',
    500: '#FFC107', // Main gold
    600: '#FFB300',
    700: '#FFA000',
    800: '#FF8F00',
    900: '#FF6F00',
  },
  
  // Secondary: Deep Red
  red: {
    50: '#FFEBEE',
    100: '#FFCDD2',
    200: '#EF9A9A',
    300: '#E57373',
    400: '#EF5350',
    500: '#B71C1C', // Deep red
    600: '#D32F2F',
    700: '#C62828',
    800: '#B71C1C',
    900: '#8B0000',
  },
  
  // Accent: Fractal Black
  fractal: {
    50: '#ECEFF1',
    100: '#CFD8DC',
    200: '#B0BEC5',
    300: '#90A4AE',
    400: '#78909C',
    500: '#455A64', // Medium fractal
    600: '#37474F',
    700: '#263238', // Dark fractal
    800: '#1A1F23',
    900: '#0D1117', // Pure fractal black
  },
  
  // Base: Off-white & Neutrals
  offWhite: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  
  // Profession Colors (for builds)
  professions: {
    guardian: '#72C1D9',
    warrior: '#FFD166',
    engineer: '#D09C59',
    ranger: '#8CDC82',
    thief: '#C08F95',
    elementalist: '#F68A87',
    mesmer: '#B679D5',
    necromancer: '#52A76F',
    revenant: '#D16E5A',
  },
  
  // Status Colors
  status: {
    success: '#4CAF50',
    warning: '#FF9800',
    error: '#F44336',
    info: '#2196F3',
  },
  
  // Boon Colors (for synergies)
  boons: {
    might: '#FF6F00',
    fury: '#D32F2F',
    quickness: '#FFC107',
    alacrity: '#9C27B0',
    protection: '#2196F3',
    resolution: '#FFEB3B',
    resistance: '#FF5722',
    stability: '#607D8B',
  },
} as const;

/**
 * Gradient utilities
 */
export const gw2Gradients = {
  heroGradient: `linear-gradient(135deg, ${gw2Colors.fractal[900]} 0%, ${gw2Colors.fractal[700]} 50%, ${gw2Colors.red[800]} 100%)`,
  goldShimmer: `linear-gradient(90deg, ${gw2Colors.gold[600]} 0%, ${gw2Colors.gold[400]} 50%, ${gw2Colors.gold[600]} 100%)`,
  fractalDepth: `linear-gradient(180deg, ${gw2Colors.fractal[800]} 0%, ${gw2Colors.fractal[900]} 100%)`,
  subtleGlow: `radial-gradient(circle at center, ${gw2Colors.gold[500]}20 0%, transparent 70%)`,
} as const;

/**
 * Shadow utilities
 */
export const gw2Shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  DEFAULT: `0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(${gw2Colors.gold[500]}, 0.06)`,
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  gold: `0 0 20px ${gw2Colors.gold[500]}40`,
  fractal: `0 0 30px ${gw2Colors.fractal[500]}60`,
} as const;

/**
 * Animation durations
 */
export const gw2Timing = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
  verySlow: '1000ms',
} as const;
