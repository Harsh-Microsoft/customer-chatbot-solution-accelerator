import type { ChatMessage } from '@/lib/types';
import { cn, formatTimestamp } from '@/lib/utils';

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isAssistant = message.sender === 'assistant';
  return (
    <article className={cn('rounded-2xl border px-4 py-3', isAssistant ? 'border-sky-200 bg-sky-50' : 'border-slate-200 bg-white')}>
      <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
        <span>{message.sender}</span>
        <span>{formatTimestamp(message.timestamp)}</span>
      </div>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-900">{message.content}</p>
    </article>
  );
}
