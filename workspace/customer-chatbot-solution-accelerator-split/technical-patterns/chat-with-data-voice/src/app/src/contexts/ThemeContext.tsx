import React, { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { webDarkTheme, webLightTheme } from '@fluentui/react-components';

export type ThemeMode = 'light' | 'dark';

interface ThemeContextValue {
  theme: typeof webDarkTheme;
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({
  children,
  initialThemeMode = 'dark',
  themeSurface,
}: {
  children: ReactNode;
  initialThemeMode?: ThemeMode;
  themeSurface?: HTMLElement | null;
}) {
  const [themeMode, setThemeMode] = useState<ThemeMode>(initialThemeMode);

  useEffect(() => {
    const surface = themeSurface ?? document.documentElement;
    surface.dataset.theme = themeMode;
    surface.style.colorScheme = themeMode;
  }, [themeMode, themeSurface]);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme: themeMode === 'dark' ? webDarkTheme : webLightTheme,
      themeMode,
      setThemeMode,
      toggleTheme: () => setThemeMode((current) => (current === 'dark' ? 'light' : 'dark')),
    }),
    [themeMode],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const value = useContext(ThemeContext);
  if (!value) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return value;
}
