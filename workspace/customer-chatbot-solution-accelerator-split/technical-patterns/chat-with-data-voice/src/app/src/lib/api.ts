import type { ChatMessage, ChatRole } from '@/lib/types';
import { getEmbedAuthBaseUrl, getUseHostPageAuth } from '@/lib/embedContext';

let widgetApiBaseOverride: string | null = null;
const SESSION_KEY = 'chat-with-data-voice.session-id';

function runtimeConfig(key: keyof NonNullable<Window['__RUNTIME_CONFIG__']>): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return String(window.__RUNTIME_CONFIG__?.[key] ?? '').trim();
}

function resolveBaseUrl(): string {
  const candidate = widgetApiBaseOverride || runtimeConfig('VITE_CHAT_API_BASE_URL') || import.meta.env.VITE_CHAT_API_BASE_URL || '/api';
  return String(candidate).trim().replace(/\/$/, '') || '/api';
}

function resolveUrl(path: string): string {
  const base = resolveBaseUrl();
  if (/^https?:\/\//i.test(base)) {
    return new URL(path.replace(/^\//, ''), `${base}/`).toString();
  }
  return `${base}${path}`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(resolveUrl(path), {
    credentials: getUseHostPageAuth() ? 'include' : 'same-origin',
    headers: {
      'content-type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return (await response.json()) as T;
}

export function setWidgetApiBaseOverride(baseUrl: string | null): void {
  widgetApiBaseOverride = baseUrl && baseUrl.trim() ? baseUrl.trim().replace(/\/$/, '') : null;
}

export function getCurrentSessionId(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(SESSION_KEY);
}

export function saveCurrentSessionId(sessionId: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(SESSION_KEY, sessionId);
}

export function clearCurrentSessionId(): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.removeItem(SESSION_KEY);
}

export function createTimestamp(): string {
  return new Date().toISOString();
}

export async function createNewChatSession(): Promise<{ session_id: string; session_name: string; created_at: string }> {
  // The backend wraps this response in an APIResponse envelope: { success, message, data }.
  const envelope = await requestJson<{ data: { session_id: string; session_name: string; created_at: string } }>(
    '/chat/sessions/new',
    { method: 'POST', body: '{}' },
  );
  return envelope.data;
}

export async function getChatHistory(sessionId?: string): Promise<ChatMessage[]> {
  const query = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
  return requestJson(`/chat/history${query}`);
}

export async function sendMessageToChat(message: string, sessionId?: string): Promise<ChatMessage> {
  return requestJson('/chat/message', {
    method: 'POST',
    body: JSON.stringify({ content: message, session_id: sessionId }),
  });
}

export async function saveVoiceMessage(sessionId: string, text: string, role: ChatRole): Promise<{ success: boolean }> {
  return requestJson('/chat/save-voice-message', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, content: text, message_type: role }),
  });
}

export function getAuthBaseUrl(): string | null {
  return getEmbedAuthBaseUrl();
}
