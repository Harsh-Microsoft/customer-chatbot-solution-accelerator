import React, { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import { getUseHostPageAuth } from '@/lib/embedContext';

export interface AuthUser {
  userId: string;
  displayName?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  signIn: (user: AuthUser) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);
const AUTH_KEY = 'chat-with-data-voice.user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const stored = window.localStorage.getItem(AUTH_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored) as AuthUser);
      } catch {
        window.localStorage.removeItem(AUTH_KEY);
      }
    }
  }, []);

  const value: AuthContextValue = {
    user,
    isAuthenticated: Boolean(user) || getUseHostPageAuth(),
    signIn(nextUser) {
      setUser(nextUser);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(AUTH_KEY, JSON.stringify(nextUser));
      }
    },
    signOut() {
      setUser(null);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(AUTH_KEY);
      }
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return value;
}
