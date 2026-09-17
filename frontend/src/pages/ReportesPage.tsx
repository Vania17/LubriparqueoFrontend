import { FormField } from '../components/FormField';
import { SummaryCard } from '../components/SummaryCard';

export function ReportesPage() {
  return (
    <div className="module-grid">
      <section className="page-panel page-heading">
        <div>
          <p className="eyebrow">Informe ejecutivo</p>
          <h2>Reportes mensuales</h2>
          <p>Resumen listo para revisar, imprimir o compartir.</p>
        </div>
        <div className="report-actions">
          <FormField label="Mes">
            <select defaultValue="May2026">
              <option value="May2026">Mayo 2026</option>
              <option value="Jun2026">Junio 2026</option>
              <option value="Jul2026">Julio 2026</option>
            </select>
          </FormField>
          <button className="primary-button" type="button">
            Generar reporte
          </button>
        </div>
      </section>

      <section className="summary-grid compact" aria-label="Resumen de reportes">
        <SummaryCard helper="Inquilinos + parqueo" label="Ingresos" tone="good" value="Q65,480.00" />
        <SummaryCard helper="Saldo por cobrar" label="Pendiente" tone="warning" value="Q1,200.00" />
        <SummaryCard helper="Promedio estimado" label="Ocupacion" value="82%" />
        <SummaryCard helper="Cuentas con alerta" label="Morosos" tone="danger" value="4" />
      </section>

      <section className="report-layout">
        <article className="page-panel report-document">
          <div className="report-title">
            <p className="eyebrow">Mayo 2026</p>
            <h2>Reporte Lubriparqueo</h2>
          </div>

          <div className="report-section">
            <h3>Ingresos del mes</h3>
            <div className="activity-row">
              <span>Inquilinos</span>
              <strong>Q38,675.00</strong>
            </div>
            <div className="activity-row">
              <span>Parqueo mensual</span>
              <strong>Q18,000.00</strong>
            </div>
            <div className="activity-row">
              <span>Parqueo temporal</span>
              <strong>Q8,805.00</strong>
            </div>
          </div>

          <div className="report-section">
            <h3>Resumen en una linea</h3>
            <p>
              Este mes se cobraron Q65,480.00 en total y quedan Q1,200.00
              pendientes por cobrar.
            </p>
          </div>
        </article>

        <aside className="page-panel report-side">
          <div>
            <p className="eyebrow">Alertas</p>
            <h2>Seguimiento</h2>
          </div>

          <div className="alert-list">
            <article className="alert-item danger">
              <strong>Baltazar</strong>
              <span>Debe Q250.00</span>
            </article>
            <article className="alert-item danger">
              <strong>Exmarcos</strong>
              <span>Debe Q100.00</span>
            </article>
            <article className="alert-item warning">
              <strong>Berta Herbalite #3</strong>
              <span>Pago parcial</span>
            </article>
          </div>

          <div className="recommendation-box">
            <p className="eyebrow">Recomendacion</p>
            <p>
              Priorizar llamadas a morosos antes del cierre semanal y confirmar
              pagos parciales con recibo.
            </p>
          </div>
        </aside>
      </section>
    </div>
  );
}
