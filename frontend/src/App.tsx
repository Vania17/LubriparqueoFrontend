import { type ReactNode, useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { InquilinosPage } from './pages/InquilinosPage';
import { PagosPage } from './pages/PagosPage';
import { ParqueoPage } from './pages/ParqueoPage';
import { ReportesPage } from './pages/ReportesPage';
import type { AppSection } from './types/navigation';

const pages: Record<AppSection, ReactNode> = {
  dashboard: <DashboardPage />,
  inquilinos: <InquilinosPage />,
  pagos: <PagosPage />,
  parqueo: <ParqueoPage />,
  reportes: <ReportesPage />,
};

export function App() {
  const [activeSection, setActiveSection] = useState<AppSection>('dashboard');

  return (
    <AppLayout activeSection={activeSection} onSectionChange={setActiveSection}>
      {pages[activeSection]}
    </AppLayout>
  );
}
