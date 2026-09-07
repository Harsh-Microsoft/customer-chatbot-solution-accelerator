import { useScenarioConfig } from '@/contexts/ScenarioConfigProvider';
import type { HostConfig } from '@/types';

const EMPTY_HOST: HostConfig = {
  appTitle: '',
  iconPath: '',
  widgetTheme: '',
  complianceBanner: '',
  assistantIconPath: '',
};

export function useHostConfig(): HostConfig {
  const config = useScenarioConfig();
  return config?.host ?? EMPTY_HOST;
}
