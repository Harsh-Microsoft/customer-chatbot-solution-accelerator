import type { CatalogItem } from '@/types';

export type ChatRole = 'user' | 'assistant' | 'system' | 'tool';

export interface ChatMessage {
  id: string;
  content: string;
  sender: ChatRole;
  timestamp: string;
  metadata?: Record<string, unknown>;
  recommendedProducts?: CatalogItem[];
}

export interface ChatSessionSummary {
  id: string;
  session_name: string;
  message_count: number;
  last_message_at?: string | null;
  is_active: boolean;
  created_at?: string;
}
