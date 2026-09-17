type SummaryCardProps = {
  label: string;
  value: string;
  helper: string;
  tone?: 'neutral' | 'good' | 'warning' | 'danger';
};

export function SummaryCard({
  label,
  value,
  helper,
  tone = 'neutral',
}: SummaryCardProps) {
  return (
    <article className={`summary-card ${tone}`}>
      <p className="summary-label">{label}</p>
      <strong>{value}</strong>
      <span>{helper}</span>
    </article>
  );
}
