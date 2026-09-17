import type { ReactNode } from 'react';
import { Sidebar } from '../components/Sidebar';
import { TopBar } from '../components/TopBar';
import type { AppSection } from '../types/navigation';

const sectionTitles: Record<AppSection, string> = {
  dashboard: 'Dashboard',
  inquilinos: 'Inquilinos',
  pagos: 'Pagos',
  parqueo: 'Parqueo',
  reportes: 'Reportes',
};

type AppLayoutProps = {
  activeSection: AppSection;
  children: ReactNode;
  onSectionChange: (section: AppSection) => void;
};

export function AppLayout({
  activeSection,
  children,
  onSectionChange,
}: AppLayoutProps) {
  return (
    <div className="app-layout">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={onSectionChange}
      />
      <main className="content-shell">
        <TopBar title={sectionTitles[activeSection]} />
        <section className="page-content">{children}</section>
      </main>
    </div>
  );
}
