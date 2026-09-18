import type { AppSection } from './navigation';

export type UserRole = 'gerente' | 'encargada' | 'encargado' | 'consulta';
export type Responsable = 'Billy' | 'Lino';
export type AuthUser = {
  id: string;
  name: string;
  role: UserRole;
  responsable: Responsable | null;
  sections: AppSection[];
};
export type AuthSession = { user: AuthUser; expiresAt: string };

export const roleLabels: Record<UserRole, string> = {
  gerente: 'Gerencia', encargada: 'Administracion',
  encargado: 'Encargado', consulta: 'Solo consulta',
};

const allSections: AppSection[] = ['dashboard', 'inquilinos', 'pagos', 'parqueo', 'reportes'];

export function parseSession(value: unknown): AuthSession {
  const session = value as Partial<AuthSession> | null;
  const user = session?.user;
  if (!user || typeof user.id !== 'string' || !user.id ||
    typeof user.name !== 'string' || !user.name ||
    !Object.prototype.hasOwnProperty.call(roleLabels, user.role) ||
    ![null, 'Billy', 'Lino'].includes(user.responsable) ||
    (user.role === 'encargado' && !user.responsable) ||
    !Array.isArray(user.sections) || !user.sections.every(s => allSections.includes(s)) ||
    typeof session?.expiresAt !== 'string' || !Number.isFinite(Date.parse(session.expiresAt))) {
    throw new Error('El servidor devolvio una sesion invalida.');
  }
  return { user, expiresAt: session.expiresAt };
}

export function canManage(user: AuthUser, responsable?: Responsable): boolean {
  if (user.role === 'gerente' || user.role === 'encargada') return true;
  return user.role === 'encargado' && !!user.responsable &&
    (!responsable || user.responsable === responsable);
}
