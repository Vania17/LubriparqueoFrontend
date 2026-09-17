import { DashboardCharts } from '../components/DashboardCharts';
import { SummaryCard } from '../components/SummaryCard';

const summaryCards = [
  {
    label: 'Ingresos del mes',
    value: 'Q65,480.00',
    helper: 'Inquilinos + parqueo',
    tone: 'good' as const,
  },
  {
    label: 'Pendiente por cobrar',
    value: 'Q1,200.00',
    helper: '4 cuentas con saldo',
    tone: 'warning' as const,
  },
  {
    label: 'Morosos',
    value: '4',
    helper: 'Revisar antes de cierre',
    tone: 'danger' as const,
  },
  {
    label: 'Ocupacion',
    value: '82%',
    helper: 'Cierre diario estimado',
    tone: 'neutral' as const,
  },
];

export function DashboardPage() {
  return (
    <div className="dashboard-grid">
      <section className="summary-grid" aria-label="Resumen del mes">
        {summaryCards.map((card) => (
          <SummaryCard
            helper={card.helper}
            key={card.label}
            label={card.label}
            tone={card.tone}
            value={card.value}
          />
        ))}
      </section>

      <DashboardCharts />

      <section className="page-panel alert-panel">
        <div>
          <p className="eyebrow">Alertas</p>
          <h2>Seguimiento importante</h2>
        </div>

        <div className="alert-list">
          <article className="alert-item danger">
            <strong>Baltazar</strong>
            <span>Saldo pendiente de Q250.00</span>
          </article>
          <article className="alert-item warning">
            <strong>Berta Herbalite #3</strong>
            <span>Pago parcial, revisar abono</span>
          </article>
          <article className="alert-item neutral">
            <strong>Parqueo temporal</strong>
            <span>Cierre pendiente para ocupacion final</span>
          </article>
        </div>
      </section>

      <section className="page-panel">
        <p className="eyebrow">Vista rapida</p>
        <h2>Actividad del dia</h2>
        <div className="activity-row">
          <span>Espacios ocupados</span>
          <strong>41</strong>
        </div>
        <div className="activity-row">
          <span>Espacios libres</span>
          <strong>9</strong>
        </div>
        <div className="activity-row">
          <span>Ingreso temporal</span>
          <strong>Q850.00</strong>
        </div>
      </section>
    </div>
  );
}
