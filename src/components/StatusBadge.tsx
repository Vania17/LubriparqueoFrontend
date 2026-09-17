type StatusBadgeProps = {
  status: 'al-dia' | 'parcial' | 'moroso';
};

const statusLabels = {
  'al-dia': 'Al dia',
  parcial: 'Parcial',
  moroso: 'Moroso',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`status-badge ${status}`}>{statusLabels[status]}</span>;
}
