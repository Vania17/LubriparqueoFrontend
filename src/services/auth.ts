import { apiRequest, ApiError } from './api';
import { parseSession, type AuthSession, type UserRole } from '../types/auth';

export const demoAuth = import.meta.env.DEV && import.meta.env.VITE_AUTH_MODE === 'demo';
const storageKey = 'lubriparqueo:demo-session';

export async function restoreSession(): Promise<AuthSession | null> {
  if (demoAuth) {
    const saved = sessionStorage.getItem(storageKey);
    if (!saved) return null;
    try { return parseSession(JSON.parse(saved)); }
    catch { sessionStorage.removeItem(storageKey); return null; }
  }
  try { return parseSession(await apiRequest('/auth/me')); }
  catch (error) { if (error instanceof ApiError && error.status === 401) return null; throw error; }
}

export async function signIn(email: string, password: string): Promise<AuthSession> {
  try {
    return parseSession(await apiRequest('/auth/login', {
      method: 'POST', body: JSON.stringify({ email, password }),
    }));
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      throw new Error('Correo o contrasena incorrectos.');
    }
    throw error;
  }
}

export function createDemoSession(profile: string): AuthSession {
  if (!demoAuth) throw new Error('El acceso de prueba no esta habilitado.');
  const profiles: Record<string, { name: string; role: UserRole; responsable: 'Billy' | 'Lino' | null }> = {
    gerente: { name: 'Gerencia', role: 'gerente', responsable: null },
    encargada: { name: 'Administracion', role: 'encargada', responsable: null },
    billy: { name: 'Billy', role: 'encargado', responsable: 'Billy' },
    lino: { name: 'Lino', role: 'encargado', responsable: 'Lino' },
    consulta: { name: 'Usuario de consulta', role: 'consulta', responsable: null },
  };
  const selected = profiles[profile];
  if (!selected) throw new Error('Selecciona un perfil valido.');
  const session: AuthSession = {
    user: { id: `demo-${profile}`, ...selected,
      sections: selected.responsable ? ['inquilinos', 'pagos', 'parqueo']
        : ['dashboard', 'inquilinos', 'pagos', 'parqueo', 'reportes'] },
    expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
  };
  sessionStorage.setItem(storageKey, JSON.stringify(session));
  return session;
}

export function clearDemoSession() { sessionStorage.removeItem(storageKey); }

export async function signOut() {
  if (demoAuth) { clearDemoSession(); return; }
  try { await apiRequest('/auth/logout', { method: 'POST' }); }
  catch (error) { if (!(error instanceof ApiError && error.status === 401)) throw error; }
}
