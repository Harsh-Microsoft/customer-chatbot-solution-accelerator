import { SunMoon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useTheme } from '@/contexts/ThemeContext';

export function ThemeToggle() {
  const { themeMode, toggleTheme } = useTheme();
  return (
    <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label={`Switch to ${themeMode === 'dark' ? 'light' : 'dark'} theme`}>
      <SunMoon className="h-4 w-4" />
    </Button>
  );
}
