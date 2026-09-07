let embedAuthBaseUrl: string | null = null;
let useHostPageAuth = false;

export function setEmbedAuthBaseUrl(value: string | null): void {
  embedAuthBaseUrl = value && value.trim() ? value.trim().replace(/\/$/, '') : null;
}

export function getEmbedAuthBaseUrl(): string | null {
  return embedAuthBaseUrl;
}

export function setUseHostPageAuth(value: boolean): void {
  useHostPageAuth = value;
}

export function getUseHostPageAuth(): boolean {
  return useHostPageAuth;
}
