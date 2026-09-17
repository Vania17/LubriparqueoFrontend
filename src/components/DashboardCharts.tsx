import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const dailyIncome = [
  { day: 'Lun 1', amount: 1000 },
  { day: 'Mar 2', amount: 1305 },
  { day: 'Mie 3', amount: 760 },
  { day: 'Jue 4', amount: 1110 },
  { day: 'Vie 5', amount: 1345 },
  { day: 'Sab 6', amount: 1445 },
  { day: 'Dom 7', amount: 355 },
];

const incomeDistribution = [
  { name: 'Inquilinos', value: 38675, color: '#1f7a4d' },
  { name: 'Parqueo mensual', value: 18000, color: '#2f6f9f' },
  { name: 'Parqueo temporal', value: 8805, color: '#d69722' },
];

const monthlyComparison = [
  {
    month: 'May 2026',
    inquilinos: 38675,
    parqueoMensual: 18000,
    parqueoTemporal: 8805,
  },
];

const managerComparison = [
  { manager: 'Billy', cobrado: 23950, pendiente: 1200 },
  { manager: 'Lino', cobrado: 14725, pendiente: 0 },
];

const currencyFormatter = new Intl.NumberFormat('es-GT', {
  currency: 'GTQ',
  maximumFractionDigits: 0,
  style: 'currency',
});

export function DashboardCharts() {
  return (
    <section className="charts-grid" aria-label="Graficas del dashboard">
      <article className="chart-panel">
        <div>
          <p className="eyebrow">Ingresos</p>
          <h2>Por dia del mes</h2>
        </div>
        <div className="chart-box">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={dailyIncome}>
              <XAxis dataKey="day" tickLine={false} />
              <YAxis
                tickFormatter={(value) => `Q${Number(value) / 1000}k`}
                tickLine={false}
                width={46}
              />
              <Tooltip
                formatter={(value) => currencyFormatter.format(Number(value))}
                labelStyle={{ color: '#172026', fontWeight: 700 }}
              />
              <Bar dataKey="amount" fill="#1f7a4d" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="chart-panel">
        <div>
          <p className="eyebrow">Distribucion</p>
          <h2>Ingresos por categoria</h2>
        </div>
        <div className="donut-layout">
          <div className="chart-box donut">
            <ResponsiveContainer height="100%" width="100%">
              <PieChart>
                <Pie
                  cx="50%"
                  cy="50%"
                  data={incomeDistribution}
                  dataKey="value"
                  innerRadius={58}
                  outerRadius={88}
                  paddingAngle={3}
                >
                  {incomeDistribution.map((item) => (
                    <Cell fill={item.color} key={item.name} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => currencyFormatter.format(Number(value))}
                  labelStyle={{ color: '#172026', fontWeight: 700 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="legend-list">
            {incomeDistribution.map((item) => (
              <div className="legend-item" key={item.name}>
                <span style={{ backgroundColor: item.color }} />
                <div>
                  <strong>{item.name}</strong>
                  <small>{currencyFormatter.format(item.value)}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      </article>

      <article className="chart-panel chart-panel-wide">
        <div>
          <p className="eyebrow">Comparacion mensual</p>
          <h2>Ingresos por tipo</h2>
        </div>
        <div className="chart-box">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={monthlyComparison}>
              <XAxis dataKey="month" tickLine={false} />
              <YAxis
                tickFormatter={(value) => `Q${Number(value) / 1000}k`}
                tickLine={false}
                width={48}
              />
              <Tooltip
                formatter={(value) => currencyFormatter.format(Number(value))}
                labelStyle={{ color: '#172026', fontWeight: 700 }}
              />
              <Bar
                dataKey="inquilinos"
                fill="#1f7a4d"
                name="Inquilinos"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="parqueoMensual"
                fill="#2f6f9f"
                name="Parqueo mensual"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="parqueoTemporal"
                fill="#d69722"
                name="Parqueo temporal"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="chart-panel chart-panel-wide">
        <div>
          <p className="eyebrow">Encargados</p>
          <h2>Billy vs Lino</h2>
        </div>
        <div className="chart-box">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={managerComparison}>
              <XAxis dataKey="manager" tickLine={false} />
              <YAxis
                tickFormatter={(value) => `Q${Number(value) / 1000}k`}
                tickLine={false}
                width={48}
              />
              <Tooltip
                formatter={(value) => currencyFormatter.format(Number(value))}
                labelStyle={{ color: '#172026', fontWeight: 700 }}
              />
              <Bar
                dataKey="cobrado"
                fill="#1f7a4d"
                name="Cobrado"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="pendiente"
                fill="#c2413b"
                name="Pendiente"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>
    </section>
  );
}
