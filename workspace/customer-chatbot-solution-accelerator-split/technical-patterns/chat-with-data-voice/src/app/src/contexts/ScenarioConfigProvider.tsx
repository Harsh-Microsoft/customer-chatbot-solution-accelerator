import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ScenarioConfig } from '@/types';

const ScenarioConfigContext = createContext<ScenarioConfig | null>(null);

export function useScenarioConfig(): ScenarioConfig | null {
  return useContext(ScenarioConfigContext);
}

export function ScenarioConfigProvider({ children }: { children: React.ReactNode }) {
  const [config, setConfig] = useState<ScenarioConfig | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadConfig() {
      try {
        const response = await fetch('/api/scenario/config', { credentials: 'include' });
        if (!response.ok) {
          throw new Error(`Config request failed with ${response.status}`);
        }
        const data = (await response.json()) as ScenarioConfig;
        if (!cancelled) {
          setConfig(data);
        }
      } catch {
        if (!cancelled) {
          setConfig(null);
        }
      }
    }

    void loadConfig();
    return () => {
      cancelled = true;
    };
  }, []);

  return <ScenarioConfigContext.Provider value={config}>{children}</ScenarioConfigContext.Provider>;
}
