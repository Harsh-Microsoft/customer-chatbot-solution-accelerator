import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';

export function LoginButton({ compact = false, showGuestActions = false }: { compact?: boolean; showGuestActions?: boolean }) {
  const { user, signIn, signOut } = useAuth();

  return user ? (
    <Button variant="ghost" size={compact ? 'sm' : 'default'} onClick={signOut}>
      Sign out
    </Button>
  ) : (
    <Button
      variant={showGuestActions ? 'secondary' : 'ghost'}
      size={compact ? 'sm' : 'default'}
      onClick={() => signIn({ userId: 'guest', displayName: 'Guest' })}
    >
      Sign in
    </Button>
  );
}
