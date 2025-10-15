/**
 * GW2 WvW Builder - Design System
 * Inspired by Guild Wars 2 aesthetic: Dark Mist / Shadow Purple
 */

export const gw2Theme = {
  colors: {
    // Background gradients
    background: {
      primary: "from-slate-950 via-purple-950 to-slate-950",
      secondary: "from-slate-900 via-purple-900 to-slate-900",
      card: "bg-slate-800/60",
      cardHover: "bg-slate-800/80",
    },

    // Accents
    accent: {
      primary: "purple-500",
      secondary: "violet-400",
      tertiary: "indigo-400",
    },

    // Text
    text: {
      primary: "slate-100",
      secondary: "slate-300",
      muted: "slate-400",
      accent: "purple-300",
    },

    // Status
    status: {
      success: "emerald-400",
      warning: "amber-400",
      error: "red-400",
      info: "blue-400",
    },

    // Stat colors (matching icons)
    stats: {
      compositions: "emerald-500",
      builds: "blue-500",
      teams: "purple-500",
      activity: "amber-500",
    },
  },

  effects: {
    blur: "backdrop-blur-sm",
    blurMd: "backdrop-blur-md",
    glow: "shadow-[0_0_15px_rgba(168,85,247,0.4)]",
    glowHover: "shadow-[0_0_25px_rgba(168,85,247,0.6)]",
    border: "border border-purple-500/20",
    borderHover: "border-purple-400/40",
  },

  animation: {
    transition: "transition-all duration-300 ease-in-out",
    transitionSlow: "transition-all duration-500 ease-in-out",
    pulse: "animate-pulse",
  },

  layout: {
    sidebarWidth: "280px",
    sidebarCollapsedWidth: "80px",
    headerHeight: "80px",
    spacing: {
      xs: "0.5rem",
      sm: "1rem",
      md: "1.5rem",
      lg: "2rem",
      xl: "3rem",
    },
  },
} as const;

export type GW2Theme = typeof gw2Theme;
