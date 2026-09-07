import type { ChatMessage, ChatRole } from '@/lib/types';
import type { CatalogItem } from '@/types';
import { createTimestamp } from '@/lib/api';
import { detectContentType, parseCatalogItemsFromText } from '@/lib/textParsers';

// Ported from chat-app/frontend/src/lib/chatMessageUtils.ts (plan row 24),
// de-domained: `Product` -> `CatalogItem`.

export function mapApiChatMessage(msg: Record<string, unknown>): ChatMessage {
  const metadata = msg.metadata && typeof msg.metadata === 'object' ? (msg.metadata as Record<string, unknown>) : undefined;
  const recommendedProducts = (msg.recommendedProducts ?? metadata?.recommendedProducts) as CatalogItem[] | undefined;

  return withParsedCatalogItems({
    id: String(msg.id ?? `msg-${Date.now()}`),
    content: String(msg.content ?? ''),
    sender: (msg.sender === 'user' ? 'user' : 'assistant') as ChatRole,
    timestamp: String((msg.timestamp as string | undefined) ?? (msg.created_at as string | undefined) ?? createTimestamp()),
    recommendedProducts: recommendedProducts?.length ? recommendedProducts : undefined,
  });
}

export function withParsedCatalogItems(message: ChatMessage): ChatMessage {
  if (message.recommendedProducts?.length || message.sender !== 'assistant') {
    return message;
  }
  if (detectContentType(message.content) !== 'catalog') {
    return message;
  }
  const { items } = parseCatalogItemsFromText(message.content);
  if (!items.length) {
    return message;
  }
  return { ...message, recommendedProducts: items };
}

export function createVoiceChatMessage(
  content: string,
  sender: ChatRole,
  recommendedProducts?: CatalogItem[],
): ChatMessage {
  return withParsedCatalogItems({
    id: `${sender}-${Date.now()}`,
    content,
    sender,
    timestamp: createTimestamp(),
    recommendedProducts,
  });
}
