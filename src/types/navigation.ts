export type AppSection =
  | 'dashboard'
  | 'inquilinos'
  | 'pagos'
  | 'parqueo'
  | 'reportes';

export type NavigationItem = {
  id: AppSection;
  label: string;
  description: string;
};
