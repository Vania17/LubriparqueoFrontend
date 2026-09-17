import { FormField } from '../components/FormField';
import { StatusBadge } from '../components/StatusBadge';

const recentPayments = [
  {
    date: '2026-05-12',
    responsable: 'Billy',
    tenant: 'Baltazar',
    amount: 'Q800.00',
    status: 'parcial' as const,
  },
  {
    date: '2026-05-11',
    responsable: 'Billy',
    tenant: 'Pedro',
    amount: 'Q700.00',
    status: 'al-dia' as const,
  },
  {
    date: '2026-05-09',
    responsable: 'Lino',
    tenant: 'Edgar Esquivel',
    amount: 'Q500.00',
    status: 'al-dia' as const,
  },
];

export function PagosPage() {
  return (
    <div className="module-grid">
      <section className="page-panel page-heading">
        <div>
          <p className="eyebrow">Cobros y abonos</p>
          <h2>Registrar pago</h2>
        </div>
        <span className="table-caption">Datos de prueba</span>
      </section>

      <section className="payment-layout">
        <form className="page-panel payment-form">
          <FormField label="Responsable">
            <select defaultValue="Billy">
              <option>Billy</option>
              <option>Lino</option>
            </select>
          </FormField>

          <FormField label="Inquilino">
            <select defaultValue="Baltazar">
              <option>Baltazar</option>
              <option>Berta Herbalite #3</option>
              <option>Edgar Esquivel</option>
              <option>Henry Hno.</option>
            </select>
          </FormField>

          <FormField label="Fecha de pago">
            <input defaultValue="2026-05-12" type="date" />
          </FormField>

          <FormField label="Monto pagado">
            <input defaultValue="800.00" min="0" step="0.01" type="number" />
          </FormField>

          <FormField label="Observacion">
            <textarea
              defaultValue="Pago parcial registrado por encargada."
              rows={4}
            />
          </FormField>

          <button className="primary-button" type="button">
            Registrar pago
          </button>
        </form>

        <aside className="page-panel payment-preview">
          <p className="eyebrow">Vista previa</p>
          <h2>Aplicacion sugerida</h2>
          <div className="preview-list">
            <div className="activity-row">
              <span>Deuda seleccionada</span>
              <strong>Q1,050.00</strong>
            </div>
            <div className="activity-row">
              <span>Pago aplicado</span>
              <strong>Q800.00</strong>
            </div>
            <div className="activity-row">
              <span>Pendiente</span>
              <strong>Q250.00</strong>
            </div>
            <div className="activity-row">
              <span>Saldo a favor</span>
              <strong>Q0.00</strong>
            </div>
          </div>
        </aside>
      </section>

      <section className="page-panel">
        <div className="table-header">
          <div>
            <p className="eyebrow">Historial</p>
            <h2>Ultimos pagos</h2>
          </div>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Responsable</th>
                <th>Inquilino</th>
                <th>Monto</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {recentPayments.map((payment) => (
                <tr key={`${payment.date}-${payment.tenant}`}>
                  <td>{payment.date}</td>
                  <td>{payment.responsable}</td>
                  <td>{payment.tenant}</td>
                  <td>{payment.amount}</td>
                  <td>
                    <StatusBadge status={payment.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
