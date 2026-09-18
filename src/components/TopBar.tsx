import { LogOut } from 'lucide-react';
import { useAuth } from '../auth/context';
import { roleLabels } from '../types/auth';

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  const { session, logout, signingOut, message } = useAuth();
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Panel de trabajo</p>
        <h1>{title}</h1>
      </div>
      <div className="session-tools">
        {message && <p className="auth-error" role="alert">{message}</p>}
        <div className="user-chip" aria-label="Usuario actual">{session?.user.name}<small>{session && roleLabels[session.user.role]}</small></div>
        <button className="ghost-button logout-button" type="button" disabled={signingOut} onClick={() => { void logout(); }}><LogOut size={18} />{signingOut ? 'Cerrando...' : 'Cerrar sesion'}</button>
      </div>
    </header>
  );
}
