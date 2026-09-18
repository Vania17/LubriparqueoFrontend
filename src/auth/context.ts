import { createContext, useContext } from 'react';
import type { AuthSession } from '../types/auth';

export type AuthContextValue = {
  session: AuthSession | null;
  status: 'loading' | 'ready' | 'error';
  message: string;
  signingOut: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginDemo: (profile: string) => void;
  logout: () => Promise<void>;
  retry: () => void;
};

export const AuthContext = createContext<AuthContextValue | null>(null);
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('Falta AuthProvider.');
  return context;
}
