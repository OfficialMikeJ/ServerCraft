// Theme Configuration for ServerCraft

export const themes = {
  crimson: {
    name: 'Crimson Shadow',
    primary: '#dc2626', // Red
    primaryHover: '#b91c1c',
    primaryLight: '#ef4444',
    accent: '#f87171',
    background: '#0a0a0a',
    backgroundAlt: '#1a1a1a',
    surface: '#262626',
    surfaceHover: '#404040',
    text: '#e5e5e5',
    textSecondary: '#a3a3a3',
    textAccent: '#fca5a5',
    border: '#404040',
    borderAccent: '#dc2626',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    shadow: 'rgba(220, 38, 38, 0.3)',
    gradient: 'linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%)',
    glowColor: '#dc2626'
  },
  ocean: {
    name: 'Ocean Depths',
    primary: '#0891b2', // Cyan/Blue
    primaryHover: '#0e7490',
    primaryLight: '#06b6d4',
    accent: '#22d3ee',
    background: '#0a0a0a',
    backgroundAlt: '#1a1a1a',
    surface: '#262626',
    surfaceHover: '#404040',
    text: '#e5e5e5',
    textSecondary: '#a3a3a3',
    textAccent: '#67e8f9',
    border: '#404040',
    borderAccent: '#0891b2',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    shadow: 'rgba(8, 145, 178, 0.3)',
    gradient: 'linear-gradient(135deg, #0891b2 0%, #164e63 100%)',
    glowColor: '#0891b2'
  },
  emerald: {
    name: 'Emerald Matrix',
    primary: '#10b981', // Green
    primaryHover: '#059669',
    primaryLight: '#34d399',
    accent: '#6ee7b7',
    background: '#0a0a0a',
    backgroundAlt: '#1a1a1a',
    surface: '#262626',
    surfaceHover: '#404040',
    text: '#e5e5e5',
    textSecondary: '#a3a3a3',
    textAccent: '#6ee7b7',
    border: '#404040',
    borderAccent: '#10b981',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    shadow: 'rgba(16, 185, 129, 0.3)',
    gradient: 'linear-gradient(135deg, #10b981 0%, #065f46 100%)',
    glowColor: '#10b981'
  },
  violet: {
    name: 'Violet Nebula',
    primary: '#8b5cf6', // Purple
    primaryHover: '#7c3aed',
    primaryLight: '#a78bfa',
    accent: '#c4b5fd',
    background: '#0a0a0a',
    backgroundAlt: '#1a1a1a',
    surface: '#262626',
    surfaceHover: '#404040',
    text: '#f5f5f5',
    textSecondary: '#d4d4d4',
    textAccent: '#ddd6fe',
    border: '#525252',
    borderAccent: '#8b5cf6',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    shadow: 'rgba(139, 92, 246, 0.3)',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #4c1d95 100%)',
    glowColor: '#8b5cf6'
  }
};

export const getTheme = (themeName) => {
  return themes[themeName] || themes.ocean;
};

export const getThemeNames = () => {
  return Object.keys(themes).map(key => ({
    id: key,
    name: themes[key].name
  }));
};
