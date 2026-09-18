import { type ReactNode, useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { InquilinosPage } from './pages/InquilinosPage';
import { PagosPage } from './pages/PagosPage';
import { ParqueoPage } from './pages/ParqueoPage';
import { ReportesPage } from './pages/ReportesPage';
import type { AppSection } from './types/navigation';
import { useAuth } from './auth/context';
import { LoginPage } from './pages/LoginPage';
import { ViewState } from './components/ViewState';

const pages: Record<AppSection, ReactNode> = {
  dashboard: <DashboardPage />,
  inquilinos: <InquilinosPage />,
  pagos: <PagosPage />,
  parqueo: <ParqueoPage />,
  reportes: <ReportesPage />,
};

export function App() {
  const { session, status } = useAuth();
  const [activeSection, setActiveSection] = useState<AppSection>('dashboard');

  if (status === 'loading') return <div className="login-shell"><ViewState kind="loading" title="Verificando sesion..." /></div>;
  if (!session) return <LoginPage />;
  const allowed = session.user.sections;
  const current = allowed.includes(activeSection) ? activeSection : allowed[0];
  const scoped = !!session.user.responsable;
  const page = !current ? <ViewState kind="empty" title="Sin secciones habilitadas" message="Solicita acceso a la administracion." />
    : scoped && ['dashboard', 'reportes', 'parqueo'].includes(current)
      ? <ViewState kind="empty" title="Sin registros disponibles" message="Los registros de tu grupo estaran disponibles al conectar esta seccion." />
      : pages[current];

  return (
    <AppLayout activeSection={current ?? 'dashboard'} onSectionChange={section => { if (allowed.includes(section)) setActiveSection(section); }}>
      {page}
    </AppLayout>
  );
}
