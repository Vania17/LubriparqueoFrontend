import type { AppSection, NavigationItem } from '../types/navigation';
import { useAuth } from '../auth/context';

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    description: 'Resumen general',
  },
  {
    id: 'inquilinos',
    label: 'Inquilinos',
    description: 'Billy y Lino',
  },
  {
    id: 'pagos',
    label: 'Pagos',
    description: 'Cobros y abonos',
  },
  {
    id: 'parqueo',
    label: 'Parqueo',
    description: 'Espacios y vehiculos',
  },
  {
    id: 'reportes',
    label: 'Reportes',
    description: 'Analisis mensual',
  },
];

type SidebarProps = {
  activeSection: AppSection;
  onSectionChange: (section: AppSection) => void;
};

export function Sidebar({ activeSection, onSectionChange }: SidebarProps) {
  const { session } = useAuth();
  return (
    <aside className="sidebar" aria-label="Navegacion principal">
      <div className="brand">
        <span className="brand-mark">L</span>
        <div>
          <p className="brand-name">Lubriparqueo</p>
          <p className="brand-caption">Control administrativo</p>
        </div>
      </div>

      <nav className="nav-list">
        {navigationItems.filter(item => session?.user.sections.includes(item.id)).map((item) => (
          <button
            className={item.id === activeSection ? 'nav-item active' : 'nav-item'}
            key={item.id}
            onClick={() => onSectionChange(item.id)}
            type="button"
          >
            <span>{item.label}</span>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>
    </aside>
  );
}
