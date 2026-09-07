import { Button } from '@/components/ui/button';
import { LoginButton } from '@/components/LoginButton';
import { ThemeToggle } from '@/components/ThemeToggle';

export function PanelRightToolbar({ onClose, onNewChat }: { onClose?: () => void; onNewChat: () => void }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
      <div>
        <p className="text-sm font-semibold text-slate-950">Conversation</p>
        <p className="text-xs text-slate-500">A generic chat surface for the current scenario.</p>
      </div>
      <div className="flex items-center gap-2">
        <LoginButton compact showGuestActions />
        <ThemeToggle />
        <Button variant="secondary" size="sm" onClick={onNewChat}>
          New chat
        </Button>
        {onClose ? (
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        ) : null}
      </div>
    </div>
  );
}
