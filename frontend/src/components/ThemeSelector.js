import React from 'react';
import { useTheme } from '@/themes/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Palette, Check } from 'lucide-react';

const ThemeSelector = () => {
  const { currentTheme, availableThemes, changeTheme, theme } = useTheme();

  const themeColors = {
    crimson: { primary: '#dc2626', accent: '#f87171' },
    ocean: { primary: '#0891b2', accent: '#22d3ee' },
    emerald: { primary: '#10b981', accent: '#6ee7b7' },
    violet: { primary: '#8b5cf6', accent: '#c4b5fd' }
  };

  return (
    <Card className="glass border-slate-700" data-testid="theme-selector-card">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <Palette className="w-5 h-5" style={{ color: theme.primary }} />
          <span>Theme Customization</span>
        </CardTitle>
        <CardDescription className="text-slate-400">
          Choose your preferred color scheme
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {availableThemes.map((themeOption) => {
            const isActive = currentTheme === themeOption.id;
            const colors = themeColors[themeOption.id];

            return (
              <button
                key={themeOption.id}
                data-testid={`theme-option-${themeOption.id}`}
                onClick={() => changeTheme(themeOption.id)}
                className={`relative p-4 rounded-lg transition-all duration-300 ${
                  isActive
                    ? 'ring-2 scale-105'
                    : 'hover:scale-102 opacity-80 hover:opacity-100'
                }`}
                style={{
                  background: `linear-gradient(135deg, ${colors.primary}20 0%, #1a1a1a 100%)`,
                  borderColor: isActive ? colors.primary : '#404040',
                  borderWidth: '2px',
                  borderStyle: 'solid',
                  ringColor: colors.primary,
                  boxShadow: isActive ? `0 8px 16px ${colors.primary}40` : 'none'
                }}
              >
                {isActive && (
                  <div
                    className="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: colors.primary }}
                  >
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}

                <div className="flex items-center space-x-3 mb-3">
                  <div
                    className="w-10 h-10 rounded-lg"
                    style={{
                      background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.accent} 100%)`
                    }}
                  />
                  <div className="text-left">
                    <p className="font-bold text-white">{themeOption.name}</p>
                    <p className="text-xs text-slate-400">Click to apply</p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <div
                    className="flex-1 h-2 rounded-full"
                    style={{ backgroundColor: colors.primary }}
                  />
                  <div
                    className="flex-1 h-2 rounded-full"
                    style={{ backgroundColor: colors.accent }}
                  />
                  <div className="flex-1 h-2 rounded-full bg-slate-700" />
                </div>
              </button>
            );
          })}
        </div>

        <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: theme.surface }}>
          <p className="text-sm font-medium mb-2" style={{ color: theme.textAccent }}>
            Preview
          </p>
          <div className="space-y-2">
            <Button
              className="w-full themed-button"
              style={{
                background: theme.gradient,
                color: '#ffffff',
                border: `2px solid ${theme.borderAccent}`,
                boxShadow: `0 4px 12px ${theme.shadow}`
              }}
            >
              Primary Button
            </Button>
            <p className="text-sm" style={{ color: theme.text }}>
              This is how text will appear with the selected theme.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ThemeSelector;
