import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { AuthContext } from './context';
import { clearDemoSession, createDemoSession, demoAuth, restoreSession, signIn, signOut } from '../services/auth';
import { SESSION_EXPIRED_EVENT } from '../services/api';
import type { AuthSession } from '../types/auth';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [signingOut, setSigningOut] = useState(false);
  const version = useRef(0);

  const expire = useCallback(() => {
    version.current++;
    if (demoAuth) clearDemoSession();
    setSession(null);
    setStatus('ready');
    setMessage('Tu sesion vencio. Inicia sesion nuevamente.');
  }, []);

  const restore = useCallback(async () => {
    const current = ++version.current;
    setStatus('loading');
    setMessage('');
    try {
      const saved = await restoreSession();
      if (current !== version.current) return;
      if (saved && Date.parse(saved.expiresAt) <= Date.now()) { expire(); return; }
      setSession(saved);
      setStatus('ready');
    } catch (error) {
      if (current !== version.current) return;
      setSession(null);
      setMessage(error instanceof Error ? error.message : 'No se pudo verificar la sesion.');
      setStatus('error');
    }
  }, [expire]);

  const invalidate = useCallback(() => { version.current++; }, []);
  useEffect(() => { void restore(); return invalidate; }, [restore, invalidate]);
  useEffect(() => {
    window.addEventListener(SESSION_EXPIRED_EVENT, expire);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, expire);
  }, [expire]);
  useEffect(() => {
    if (!session) return;
    const check = () => { if (Date.parse(session.expiresAt) <= Date.now()) expire(); };
    const timeout = window.setTimeout(check, Math.min(Math.max(0, Date.parse(session.expiresAt) - Date.now()), 2147483647));
    const interval = window.setInterval(check, 30000);
    window.addEventListener('focus', check);
    document.addEventListener('visibilitychange', check);
    return () => {
      window.clearTimeout(timeout); window.clearInterval(interval);
      window.removeEventListener('focus', check);
      document.removeEventListener('visibilitychange', check);
    };
  }, [session, expire]);

  async function login(email: string, password: string) {
    const current = ++version.current;
    const next = await signIn(email, password);
    if (current !== version.current) return;
    if (Date.parse(next.expiresAt) <= Date.now()) { expire(); return; }
    setSession(next); setStatus('ready'); setMessage('');
  }
  function loginDemo(profile: string) {
    version.current++;
    setSession(createDemoSession(profile)); setStatus('ready'); setMessage('');
  }
  async function logout() {
    setSigningOut(true); setMessage('');
    try { await signOut(); version.current++; setSession(null); setStatus('ready'); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'No se pudo cerrar la sesion.'); }
    finally { setSigningOut(false); }
  }

  return <AuthContext.Provider value={{ session, status, message, signingOut, login, loginDemo, logout, retry: () => { void restore(); } }}>{children}</AuthContext.Provider>;
}
