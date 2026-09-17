import { StatusBadge } from '../components/StatusBadge';
import { SummaryCard } from '../components/SummaryCard';

const monthlySpaces = [
  {
    space: 'M-01',
    owner: 'Carlos Ruiz',
    vehicle: 'P-123ABC',
    type: 'Mensual',
    status: 'Ocupado',
  },
  {
    space: 'M-02',
    owner: 'Doña Lesvia',
    vehicle: 'P-456DEF',
    type: 'Mensual',
    status: 'Reservado libre',
  },
  {
    space: 'M-03',
    owner: 'Susana de la Pacaya',
    vehicle: 'P-789GHI',
    type: 'Mensual',
    status: 'Ocupado',
  },
];

const temporaryVehicles = [
  {
    plate: 'C-102JKL',
    entry: '08:35',
    space: 'T-04',
    rate: 'Por dia',
    amount: 'Q50.00',
  },
  {
    plate: 'TC-88MNO',
    entry: '10:20',
    space: 'M-02',
    rate: 'Acordada',
    amount: 'Q75.00',
  },
  {
    plate: 'P-55XYZ',
    entry: '13:10',
    space: 'T-07',
    rate: 'Por hora',
    amount: 'Q20.00',
  },
];

export function ParqueoPage() {
  return (
    <div className="module-grid">
      <section className="page-panel page-heading">
        <div>
          <p className="eyebrow">Operacion diaria</p>
          <h2>Control de parqueo</h2>
          <p>Espacios mensuales, temporales y ocupacion del dia.</p>
        </div>
        <span className="table-caption">Datos de prueba</span>
      </section>

      <section className="summary-grid compact" aria-label="Resumen de parqueo">
        <SummaryCard helper="Capacidad registrada" label="Espacios" value="50" />
        <SummaryCard helper="Mensuales + temporales" label="Ocupados" tone="good" value="41" />
        <SummaryCard helper="Disponibles para el dia" label="Libres" value="9" />
        <SummaryCard helper="Cierre estimado 3:00 p.m." label="Ocupacion" tone="warning" value="82%" />
      </section>

      <section className="parking-grid">
        <article className="page-panel">
          <div className="table-header">
            <div>
              <p className="eyebrow">Mensual</p>
              <h2>Espacios fijos</h2>
            </div>
          </div>

          <div className="parking-list">
            {monthlySpaces.map((space) => (
              <div className="parking-card" key={space.space}>
                <div>
                  <strong>{space.space}</strong>
                  <span>{space.owner}</span>
                </div>
                <div>
                  <span>{space.vehicle}</span>
                  <small>{space.type}</small>
                </div>
                <span className={space.status === 'Ocupado' ? 'parking-state busy' : 'parking-state open'}>
                  {space.status}
                </span>
              </div>
            ))}
          </div>
        </article>

        <article className="page-panel">
          <div className="table-header">
            <div>
              <p className="eyebrow">Temporal</p>
              <h2>Entradas activas</h2>
            </div>
          </div>

          <div className="table-scroll simple-table">
            <table className="data-table temporary-table">
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Entrada</th>
                  <th>Espacio</th>
                  <th>Tarifa</th>
                  <th>Monto</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {temporaryVehicles.map((vehicle) => (
                  <tr key={vehicle.plate}>
                    <td>{vehicle.plate}</td>
                    <td>{vehicle.entry}</td>
                    <td>{vehicle.space}</td>
                    <td>{vehicle.rate}</td>
                    <td className="money-cell positive">{vehicle.amount}</td>
                    <td>
                      <StatusBadge status="parcial" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </div>
  );
}
