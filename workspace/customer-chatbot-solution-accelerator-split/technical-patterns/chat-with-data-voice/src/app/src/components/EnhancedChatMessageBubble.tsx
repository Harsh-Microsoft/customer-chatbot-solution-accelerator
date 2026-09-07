import type { ChatMessage } from '@/lib/types';

import { ChatMessageBubble } from '@/components/ChatMessageBubble';

export function EnhancedChatMessageBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="space-y-2">
      <ChatMessageBubble message={message} />
      {message.recommendedProducts?.length ? (
        <div className="flex flex-wrap gap-2 text-xs text-slate-600">
          {message.recommendedProducts.map((product) => (
            <span key={product} className="rounded-full border border-slate-200 bg-slate-50 px-2 py-1">
              {product}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
