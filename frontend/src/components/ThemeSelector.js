import React, { useState } from 'react';
import { useTheme } from '@/themes/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Palette, Check } from 'lucide-react';
import { toast } from 'sonner';

const ThemeSelector = () => {
  const { currentTheme, availableThemes, changeTheme, theme } = useTheme();
  const [selectedTheme, setSelectedTheme] = useState(currentTheme);

  const themeColors = {
    crimson: { primary: '#dc2626', accent: '#f87171', name: 'Crimson Shadow' },
    ocean: { primary: '#0891b2', accent: '#22d3ee', name: 'Ocean Depths' },
    emerald: { primary: '#10b981', accent: '#6ee7b7', name: 'Emerald Matrix' },
    violet: { primary: '#8b5cf6', accent: '#c4b5fd', name: 'Violet Nebula' }
  };

  const handleApplyTheme = () => {
    changeTheme(selectedTheme);
    toast.success(`${themeColors[selectedTheme].name} theme applied!`);
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
      <CardContent className="space-y-6">
        {/* Dropdown Theme Selector */}
        <div className="p-4 rounded-lg" style={{ backgroundColor: theme.surface }}>
          <h3 className="text-lg font-semibold mb-4" style={{ color: theme.textAccent }}>
            Quick Theme Selection
          </h3>
          <div className="flex items-center space-x-3">
            <div className="flex-1">
              <Select
                value={selectedTheme}
                onValueChange={setSelectedTheme}
              >
                <SelectTrigger 
                  data-testid="theme-dropdown"
                  className="bg-slate-800 border-slate-600 h-12"
                  style={{
                    borderColor: theme.borderAccent,
                    borderWidth: '2px'
                  }}
                >
                  <SelectValue placeholder="Select a theme" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  {Object.keys(themeColors).map((themeId) => (
                    <SelectItem 
                      key={themeId} 
                      value={themeId}
                      className="cursor-pointer hover:bg-slate-700"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-6 h-6 rounded"
                          style={{
                            background: `linear-gradient(135deg, ${themeColors[themeId].primary} 0%, ${themeColors[themeId].accent} 100%)`
                          }}
                        />
                        <span className="text-white">{themeColors[themeId].name}</span>
                        {currentTheme === themeId && (
                          <Check className="w-4 h-4 text-green-400 ml-2" />
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              data-testid="apply-theme-button"
              onClick={handleApplyTheme}
              disabled={selectedTheme === currentTheme}
              className="themed-button h-12 px-8"
              style={{
                background: selectedTheme === currentTheme 
                  ? 'rgba(100, 100, 100, 0.5)' 
                  : theme.gradient,
                border: `2px solid ${theme.borderAccent}`,
                boxShadow: selectedTheme === currentTheme 
                  ? 'none' 
                  : `0 4px 12px ${theme.shadow}`,
                cursor: selectedTheme === currentTheme ? 'not-allowed' : 'pointer'
              }}
            >
              {selectedTheme === currentTheme ? 'Applied' : 'Apply Theme'}
            </Button>
          </div>
          {selectedTheme !== currentTheme && (
            <p className="text-sm mt-2 text-slate-400">
              Click "Apply Theme" to activate {themeColors[selectedTheme].name}
            </p>
          )}
        </div>

        {/* Visual Theme Cards */}
        <div>
          <h3 className="text-lg font-semibold mb-4" style={{ color: theme.textAccent }}>
            Visual Theme Preview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableThemes.map((themeOption) => {
              const isActive = currentTheme === themeOption.id;
              const colors = themeColors[themeOption.id];

              return (
                <button
                  key={themeOption.id}
                  data-testid={`theme-card-${themeOption.id}`}
                  onClick={() => {
                    setSelectedTheme(themeOption.id);
                    changeTheme(themeOption.id);
                    toast.success(`${colors.name} theme applied!`);
                  }}
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
                      <p className="text-xs text-slate-400">Click to apply instantly</p>
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
        </div>

        {/* Preview Section */}
        <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: theme.surface }}>
          <p className="text-sm font-medium mb-3" style={{ color: theme.textAccent }}>
            Live Preview - Current Theme: {themeColors[currentTheme].name}
          </p>
          <div className="space-y-3">
            <Button
              className="w-full themed-button"
              style={{
                background: theme.gradient,
                color: '#ffffff',
                border: `2px solid ${theme.borderAccent}`,
                boxShadow: `0 4px 12px ${theme.shadow}`
              }}
            >
              Primary Action Button
            </Button>
            <div className="flex space-x-2">
              <Button
                size="sm"
                className="flex-1 themed-button"
                style={{
                  background: theme.gradient,
                  border: `2px solid ${theme.borderAccent}`,
                  boxShadow: `0 4px 12px ${theme.shadow}`
                }}
              >
                Start Server
              </Button>
              <Button
                size="sm"
                className="flex-1 themed-button"
                style={{
                  background: theme.gradient,
                  border: `2px solid ${theme.borderAccent}`,
                  boxShadow: `0 4px 12px ${theme.shadow}`
                }}
              >
                Stop Server
              </Button>
              <Button
                size="sm"
                className="flex-1 themed-button"
                style={{
                  background: theme.gradient,
                  border: `2px solid ${theme.borderAccent}`,
                  boxShadow: `0 4px 12px ${theme.shadow}`
                }}
              >
                Restart
              </Button>
            </div>
            <p className="text-sm" style={{ color: theme.text }}>
              This is sample text showing how content appears with the current theme. 
              <span style={{ color: theme.textAccent }}> Accent text highlights important information.</span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ThemeSelector;
