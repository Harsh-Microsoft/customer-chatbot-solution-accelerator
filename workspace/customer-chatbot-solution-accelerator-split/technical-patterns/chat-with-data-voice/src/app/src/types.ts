export type CatalogCardVariant = 'grid' | 'list' | 'detail';

export interface CatalogCardSchema {
  title: string;
  subtitle?: string;
  image?: string;
  highlights?: string[];
  description?: string;
}

export interface CatalogPresentationItem {
  highlights: string[];
}

export interface CatalogPresentation {
  defaultImage: string;
  items: Record<string, CatalogPresentationItem>;
  titleAliases: Record<string, string>;
}

export interface CatalogCopy {
  intro: string;
  loadError: string;
}

export interface CatalogConfig {
  routePrefix: string;
  itemSingular: string;
  itemPlural: string;
  cardSchema: CatalogCardSchema;
  enabledEndpoints: string[];
  cardVariant: CatalogCardVariant;
  copy: CatalogCopy;
}

export interface HostConfig {
  appTitle: string;
  iconPath: string;
  widgetTheme: string;
  complianceBanner: string;
  assistantIconPath: string;
}

export interface WelcomeConfig {
  title: string;
  subtitle: string;
  hint: string;
}

export interface ScenarioConfig {
  host: HostConfig;
  welcome: WelcomeConfig;
  catalog: CatalogConfig;
  presentation: CatalogPresentation;
}

export interface CatalogItem {
  id: string;
  title: string;
  category: string;
  description?: string;
  image: string;
  highlights?: string[];
  price?: number;
  rating?: number;
}

declare global {
  interface Window {
    __RUNTIME_CONFIG__?: Partial<Record<'VITE_API_BASE_URL' | 'VITE_HOST_APP_TITLE' | 'VITE_CHAT_WIDGET_THEME', string>>;
  }
}
