import { Button } from '@/components/ui/button';
import { PanelRight } from '@/components/PanelRight';
import { PanelRightToolbar } from '@/components/PanelRightToolbar';
import { EnhancedChatPanel } from '@/components/EnhancedChatPanel';
import type { ChatMessage } from '@/lib/types';

export function ChatSidebar({
  isOpen,
  onClose,
  messages,
  onSendMessage,
  onVoiceMessage,
  onNewChat,
  isTyping,
  isLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  onSendMessage: (content: string) => void | Promise<void>;
  onVoiceMessage?: (text: string, role: 'user' | 'assistant') => void | Promise<void>;
  onNewChat: () => void;
  isTyping: boolean;
  isLoading: boolean;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <PanelRight>
      <PanelRightToolbar onClose={onClose} onNewChat={onNewChat} />
      <EnhancedChatPanel
        messages={messages}
        onSendMessage={onSendMessage}
        onVoiceMessage={onVoiceMessage}
        onNewChat={onNewChat}
        isTyping={isTyping}
        isLoading={isLoading}
      />
      <div className="border-t border-slate-200 px-4 py-3 text-right">
        <Button variant="ghost" size="sm" onClick={onClose}>
          Hide panel
        </Button>
      </div>
    </PanelRight>
  );
}
