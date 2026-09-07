import React from 'react';
import ReactDOM from 'react-dom/client';

import { AuthProvider } from '@/contexts/AuthContext';
import { ScenarioConfigProvider } from '@/contexts/ScenarioConfigProvider';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ScenarioApp } from '@/ScenarioApp';

import './main.css';
import './styles/theme.css';
import './styles/coral.css';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ScenarioConfigProvider>
      <AuthProvider>
        <ThemeProvider initialThemeMode="dark">
          <ScenarioApp />
        </ThemeProvider>
      </AuthProvider>
    </ScenarioConfigProvider>
  </React.StrictMode>,
);
