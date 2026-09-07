import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { ChatMessageBubble } from '@/components/ChatMessageBubble';
import { EnhancedChatMessageBubble } from '@/components/EnhancedChatMessageBubble';
import { CatalogItemSkeleton } from '@/components/CatalogItemSkeleton';
import type { ChatMessage } from '@/lib/types';

export function EnhancedChatPanel({
  messages,
  onSendMessage,
  onVoiceMessage,
  onNewChat,
  isTyping,
  isLoading,
}: {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void | Promise<void>;
  onVoiceMessage?: (text: string, role: 'user' | 'assistant') => void | Promise<void>;
  onNewChat: () => void;
  isTyping: boolean;
  isLoading: boolean;
}) {
  const [draft, setDraft] = useState('');

  const submit = async () => {
    const content = draft.trim();
    if (!content) {
      return;
    }
    setDraft('');
    await onSendMessage(content);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {isLoading ? <CatalogItemSkeleton /> : null}
        {messages.length ? (
          messages.map((message) => <EnhancedChatMessageBubble key={message.id} message={message} />)
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            Start a conversation to see the generic chat experience here.
          </div>
        )}
        {isTyping ? <ChatMessageBubble message={{ id: 'typing', content: 'Assistant is typing…', sender: 'assistant', timestamp: new Date().toISOString() }} /> : null}
      </div>
      <div className="border-t border-slate-200 p-4">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          rows={3}
          className="w-full resize-none rounded-xl border border-slate-200 bg-white p-3 text-sm outline-none ring-0 placeholder:text-slate-400 focus:border-slate-400"
          placeholder="Ask a question..."
        />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button onClick={submit}>Send</Button>
          <Button variant="secondary" onClick={() => onVoiceMessage?.(draft.trim(), 'user')}>
            Voice
          </Button>
          <Button variant="ghost" onClick={onNewChat}>
            Reset
          </Button>
        </div>
      </div>
    </div>
  );
}
