import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Eye, Pencil, Trash2 } from 'lucide-react';
import { FormField } from '../components/FormField';
import { StatusBadge } from '../components/StatusBadge';
import { SummaryCard } from '../components/SummaryCard';

type Responsable = 'Billy' | 'Lino';
type ControlMonth = 'May2026' | 'Jun2026' | 'Jul2026';

type TenantStatus = 'al-dia' | 'parcial' | 'moroso';

type TenantRow = {
  alert: string;
  dueDay: number;
  dueMonth: string;
  name: string;
  note: string;
  paidAt: string;
  plan: 'A' | 'V';
  monthlyAmount: number;
  paid: number;
  pending: number;
  status: TenantStatus;
};

type TenantFormMode = 'new' | 'edit';
type TenantModalMode = TenantFormMode | 'detail';

const tenantData: Record<Responsable, TenantRow[]> = {
  Billy: [
    {
      alert: '',
      dueDay: 2,
      dueMonth: 'dic',
      name: 'Timoteo Lopez #2',
      note: 'Registro sin observaciones especiales.',
      paidAt: '20-dic',
      plan: 'V',
      monthlyAmount: 1000,
      paid: 1000,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: 'Cobrar diferencia',
      dueDay: 3,
      dueMonth: 'ene',
      name: 'Baltazar',
      note: 'Dar seguimiento porque pago incompleto este mes.',
      paidAt: '12-ene',
      plan: 'V',
      monthlyAmount: 1050,
      paid: 800,
      pending: 250,
      status: 'moroso',
    },
    {
      alert: 'Revisar cartapacio',
      dueDay: 15,
      dueMonth: 'nov',
      name: 'Berta Herbalite #3',
      note: 'Suele pagar en abonos. Confirmar contra recibo.',
      paidAt: '3-ene',
      plan: 'V',
      monthlyAmount: 650,
      paid: 200,
      pending: 450,
      status: 'parcial',
    },
    {
      alert: '',
      dueDay: 10,
      dueMonth: 'may',
      name: 'Susana de la Pacaya',
      note: 'Inquilina anticipada, usualmente paga antes de fecha.',
      paidAt: '8-may',
      plan: 'A',
      monthlyAmount: 600,
      paid: 600,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: '',
      dueDay: 30,
      dueMonth: 'ago',
      name: 'Exmarcos',
      note: 'Revisar deuda acumulada antes de cierre mensual.',
      paidAt: '11-ene',
      plan: 'V',
      monthlyAmount: 400,
      paid: 300,
      pending: 100,
      status: 'moroso',
    },
  ],
  Lino: [
    {
      alert: '',
      dueDay: 1,
      dueMonth: 'feb',
      name: 'Edgar Esquivel',
      note: 'Registro sin observaciones especiales.',
      paidAt: '2-ene',
      plan: 'A',
      monthlyAmount: 500,
      paid: 500,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: '',
      dueDay: 1,
      dueMonth: 'ene',
      name: 'Chino Chema #1',
      note: 'Registro sin observaciones especiales.',
      paidAt: '4-dic',
      plan: 'A',
      monthlyAmount: 500,
      paid: 500,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: '',
      dueDay: 1,
      dueMonth: 'ene',
      name: 'Gabriel',
      note: 'Registro sin observaciones especiales.',
      paidAt: '2-dic',
      plan: 'A',
      monthlyAmount: 1000,
      paid: 1000,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: '',
      dueDay: 15,
      dueMonth: 'abr',
      name: 'Marco Tulio Lopez #1',
      note: 'Plan vencido. Confirmar fechas al cierre.',
      paidAt: '18-may',
      plan: 'V',
      monthlyAmount: 500,
      paid: 500,
      pending: 0,
      status: 'al-dia',
    },
    {
      alert: '',
      dueDay: 7,
      dueMonth: 'ene',
      name: 'Henry Hno.',
      note: 'Registro sin observaciones especiales.',
      paidAt: '10-dic',
      plan: 'A',
      monthlyAmount: 375,
      paid: 375,
      pending: 0,
      status: 'al-dia',
    },
  ],
};

const currencyFormatter = new Intl.NumberFormat('es-GT', {
  currency: 'GTQ',
  maximumFractionDigits: 2,
  style: 'currency',
});

const controlMonthLabels: Record<ControlMonth, string> = {
  May2026: 'Mayo 2026',
  Jun2026: 'Junio 2026',
  Jul2026: 'Julio 2026',
};

export function InquilinosPage() {
  const [activeResponsable, setActiveResponsable] = useState<Responsable>('Billy');
  const [controlMonth, setControlMonth] = useState<ControlMonth>('May2026');
  const [editableTenantData, setEditableTenantData] = useState(tenantData);
  const [modalMode, setModalMode] = useState<TenantModalMode | null>(null);
  const [selectedTenant, setSelectedTenant] = useState<TenantRow | null>(null);
  const [tenantToDelete, setTenantToDelete] = useState<TenantRow | null>(null);
  const [notice, setNotice] = useState<{
    message: string;
    tone: 'success' | 'error';
  } | null>(null);
  const tenants = editableTenantData[activeResponsable];

  function handleTenantSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const responsable = formData.get('responsable') as Responsable;
    const plan = formData.get('plan') as 'A' | 'V';
    const status = formData.get('status') as TenantStatus;
    const name = String(formData.get('name') ?? '').trim();

    if (!name) {
      setNotice({
        message: 'No se pudo guardar: el nombre es obligatorio.',
        tone: 'error',
      });
      return;
    }

    const nextTenant: TenantRow = {
      alert: String(formData.get('alert') ?? '').trim(),
      dueDay: Number(formData.get('dueDay') ?? 1),
      dueMonth: controlMonth.slice(0, 3).toLowerCase(),
      monthlyAmount: Number(formData.get('monthlyAmount') ?? 0),
      name,
      note: String(formData.get('note') ?? '').trim(),
      paid: selectedTenant?.paid ?? 0,
      paidAt: selectedTenant?.paidAt ?? '-',
      pending: selectedTenant?.pending ?? Number(formData.get('monthlyAmount') ?? 0),
      plan,
      status,
    };

    setEditableTenantData((current) => {
      const currentWithoutEditedTenant =
        modalMode === 'edit' && selectedTenant
          ? {
              Billy: current.Billy.filter(
                (tenant) => tenant.name !== selectedTenant.name,
              ),
              Lino: current.Lino.filter(
                (tenant) => tenant.name !== selectedTenant.name,
              ),
            }
          : current;

      return {
        ...currentWithoutEditedTenant,
        [responsable]: [...currentWithoutEditedTenant[responsable], nextTenant],
      };
    });

    setActiveResponsable(responsable);
    setModalMode(null);
    setSelectedTenant(null);
    setNotice({
      message:
        modalMode === 'new'
          ? 'Inquilino agregado correctamente.'
          : 'Inquilino actualizado correctamente.',
      tone: 'success',
    });
  }

  function handleDeleteTenant() {
    if (!tenantToDelete) {
      return;
    }

    setEditableTenantData((current) => ({
      Billy: current.Billy.filter((tenant) => tenant.name !== tenantToDelete.name),
      Lino: current.Lino.filter((tenant) => tenant.name !== tenantToDelete.name),
    }));
    setTenantToDelete(null);
    setNotice({
      message: 'Inquilino eliminado correctamente.',
      tone: 'success',
    });
  }

  const summary = useMemo(() => {
    return tenants.reduce(
      (totals, tenant) => {
        totals.paid += tenant.paid;
        totals.pending += tenant.pending;
        totals.morosos += tenant.status === 'moroso' ? 1 : 0;
        totals.alDia += tenant.status === 'al-dia' ? 1 : 0;
        return totals;
      },
      { alDia: 0, morosos: 0, paid: 0, pending: 0 },
    );
  }, [tenants]);

  useEffect(() => {
    if (!notice) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setNotice(null);
    }, 3200);

    return () => window.clearTimeout(timeoutId);
  }, [notice]);

  return (
    <div className="module-grid">
      <section className="page-panel page-heading inquilinos-hero">
        <div>
          <p className="eyebrow">Control mensual</p>
          <h2>Inquilinos - {controlMonthLabels[controlMonth]}</h2>
          <p>
            Vista operativa del mes seleccionado, separada por responsable.
          </p>
        </div>
        <div className="tenant-toolbar">
          <div className="segmented-control" aria-label="Responsable">
            {(['Billy', 'Lino'] as Responsable[]).map((responsable) => (
              <button
                className={responsable === activeResponsable ? 'active' : ''}
                key={responsable}
                onClick={() => setActiveResponsable(responsable)}
                type="button"
              >
                {responsable}
              </button>
            ))}
          </div>

          <label className="month-selector">
            <span>Mes de control</span>
            <select
              onChange={(event) =>
                setControlMonth(event.target.value as ControlMonth)
              }
              value={controlMonth}
            >
              <option value="May2026">Mayo 2026</option>
              <option value="Jun2026">Junio 2026</option>
              <option value="Jul2026">Julio 2026</option>
            </select>
          </label>

          <button
            className="primary-button compact-button"
            onClick={() => {
              setSelectedTenant(null);
              setModalMode('new');
            }}
            type="button"
          >
            Nuevo inquilino
          </button>
        </div>
      </section>

      {notice ? (
        <div className={`toast-notice ${notice.tone}`} role="status">
          {notice.message}
        </div>
      ) : null}

      <section className="summary-grid compact" aria-label="Resumen inquilinos">
        <SummaryCard
          helper={`${activeResponsable} - ${controlMonthLabels[controlMonth]}`}
          label="Cobrado"
          tone="good"
          value={currencyFormatter.format(summary.paid)}
        />
        <SummaryCard
          helper={`Saldo del mes seleccionado`}
          label="Pendiente"
          tone={summary.pending > 0 ? 'warning' : 'good'}
          value={currencyFormatter.format(summary.pending)}
        />
        <SummaryCard
          helper="Necesitan seguimiento"
          label="Morosos"
          tone={summary.morosos > 0 ? 'danger' : 'good'}
          value={String(summary.morosos)}
        />
        <SummaryCard
          helper="Pagaron completo"
          label="Al dia"
          value={String(summary.alDia)}
        />
      </section>

      <section className="page-panel tenant-table-panel">
        <div className="table-header">
          <div>
            <p className="eyebrow">{activeResponsable}</p>
            <h2>Listado de pagos - {controlMonthLabels[controlMonth]}</h2>
          </div>
          <span className="table-caption">Datos de prueba</span>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>No.</th>
                <th>Fecha al</th>
                <th>Mes</th>
                <th>Pago fecha</th>
                <th>Inquilino</th>
                <th>Pago</th>
                <th>Resta</th>
                <th>Plan</th>
                <th>Mes Q.</th>
                <th>Alerta</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant, index) => (
                <tr className={tenant.pending > 0 ? 'row-attention' : ''} key={tenant.name}>
                  <td className="number-cell">{index + 1}</td>
                  <td>
                    <span className="date-pill">{tenant.dueDay}</span>
                  </td>
                  <td>
                    <span className="month-pill">{tenant.dueMonth}</span>
                  </td>
                  <td>{tenant.paidAt}</td>
                  <td className="tenant-name-cell">{tenant.name}</td>
                  <td className="money-cell positive">
                    {currencyFormatter.format(tenant.paid)}
                  </td>
                  <td className={tenant.pending > 0 ? 'money-cell pending' : 'muted-cell'}>
                    {tenant.pending > 0 ? currencyFormatter.format(tenant.pending) : '-'}
                  </td>
                  <td>
                    <span className={`plan-pill ${tenant.plan.toLowerCase()}`}>
                      {tenant.plan}
                    </span>
                  </td>
                  <td className="money-cell">
                    {currencyFormatter.format(tenant.monthlyAmount)}
                  </td>
                  <td className={tenant.alert ? 'alert-cell' : 'muted-cell'}>
                    {tenant.alert || '-'}
                  </td>
                  <td>
                    <StatusBadge status={tenant.status} />
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        aria-label={`Ver detalle de ${tenant.name}`}
                        className="icon-button"
                        onClick={() => {
                          setSelectedTenant(tenant);
                          setModalMode('detail');
                        }}
                        title={`Ver detalle de ${tenant.name}`}
                        type="button"
                      >
                        <Eye size={16} />
                      </button>
                    <button
                      aria-label={`Editar ${tenant.name}`}
                      className="icon-button"
                      onClick={() => {
                        setSelectedTenant(tenant);
                        setModalMode('edit');
                      }}
                      title={`Editar ${tenant.name}`}
                      type="button"
                    >
                      <Pencil size={16} />
                    </button>
                      <button
                        aria-label={`Eliminar ${tenant.name}`}
                        className="icon-button danger"
                        onClick={() => setTenantToDelete(tenant)}
                        title={`Eliminar ${tenant.name}`}
                        type="button"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {modalMode ? (
        <div className="modal-backdrop" role="presentation">
          <section
            aria-labelledby="tenant-modal-title"
            aria-modal="true"
            className="modal-panel"
            role="dialog"
          >
            <div className="modal-header">
              <div>
                <p className="eyebrow">
                  {modalMode === 'new'
                    ? 'Nuevo registro'
                    : modalMode === 'edit'
                      ? 'Editar registro'
                      : 'Detalle'}
                </p>
                <h2 id="tenant-modal-title">
                  {modalMode === 'new'
                    ? 'Agregar inquilino'
                    : selectedTenant?.name}
                </h2>
              </div>
              <button
                className="ghost-button"
                onClick={() => {
                  setModalMode(null);
                  setSelectedTenant(null);
                }}
                type="button"
              >
                Cerrar
              </button>
            </div>

            {modalMode === 'detail' && selectedTenant ? (
              <div className="tenant-detail-grid">
                <div>
                  <span>Responsable</span>
                  <strong>{activeResponsable}</strong>
                </div>
                <div>
                  <span>Plan</span>
                  <strong>{selectedTenant.plan}</strong>
                </div>
                <div>
                  <span>Dia de pago</span>
                  <strong>{selectedTenant.dueDay}</strong>
                </div>
                <div>
                  <span>Mensualidad</span>
                  <strong>
                    {currencyFormatter.format(selectedTenant.monthlyAmount)}
                  </strong>
                </div>
                <div>
                  <span>Alerta</span>
                  <strong>{selectedTenant.alert || '-'}</strong>
                </div>
                <div>
                  <span>Estado</span>
                  <strong>{selectedTenant.status}</strong>
                </div>
                <div className="detail-note">
                  <span>Observacion</span>
                  <p>{selectedTenant.note || 'Sin observaciones.'}</p>
                </div>
              </div>
            ) : (
            <form className="tenant-edit-form" onSubmit={handleTenantSubmit}>
            <div className="tenant-form-grid">
            <FormField label="Nombre">
              <input defaultValue={selectedTenant?.name ?? ''} name="name" />
            </FormField>
            <FormField label="Responsable">
              <select defaultValue={activeResponsable} name="responsable">
                <option>Billy</option>
                <option>Lino</option>
              </select>
            </FormField>
            <FormField label="Plan">
              <select defaultValue={selectedTenant?.plan ?? 'A'} name="plan">
                <option value="A">Anticipado</option>
                <option value="V">Vencido</option>
              </select>
            </FormField>
            <FormField label="Dia de pago">
              <input
                defaultValue={selectedTenant?.dueDay ?? 15}
                max="31"
                min="1"
                name="dueDay"
                type="number"
              />
            </FormField>
            <FormField label="Mensualidad">
              <input
                defaultValue={selectedTenant?.monthlyAmount ?? 0}
                min="0"
                name="monthlyAmount"
                step="0.01"
                type="number"
              />
            </FormField>
            <FormField label="Estado">
              <select defaultValue={selectedTenant?.status ?? 'al-dia'} name="status">
                <option value="al-dia">Al dia</option>
                <option value="parcial">Parcial</option>
                <option value="moroso">Moroso</option>
              </select>
            </FormField>
            <FormField label="Observacion del inquilino">
              <textarea
                defaultValue={selectedTenant?.note ?? ''}
                name="note"
                rows={3}
              />
            </FormField>
            <FormField label="Alerta visible en tabla">
              <input defaultValue={selectedTenant?.alert ?? ''} name="alert" />
            </FormField>
            </div>

            <div className="form-actions">
            <button className="primary-button" type="submit">
              Guardar cambios
            </button>
            <button
              className="ghost-button"
              onClick={() => {
                setModalMode(null);
                setSelectedTenant(null);
              }}
              type="button"
            >
              Cancelar
            </button>
            </div>
            </form>
            )}
          </section>
        </div>
      ) : null}

      {tenantToDelete ? (
        <div className="modal-backdrop" role="presentation">
          <section
            aria-labelledby="delete-tenant-title"
            aria-modal="true"
            className="confirm-modal"
            role="dialog"
          >
            <div>
              <p className="eyebrow">Confirmar eliminacion</p>
              <h2 id="delete-tenant-title">Eliminar inquilino</h2>
              <p>
                Se eliminara {tenantToDelete.name} de la tabla temporal. Esta
                accion no afecta backend porque aun no esta conectado.
              </p>
            </div>
            <div className="form-actions">
              <button
                className="danger-button"
                onClick={handleDeleteTenant}
                type="button"
              >
                Eliminar
              </button>
              <button
                className="ghost-button"
                onClick={() => setTenantToDelete(null)}
                type="button"
              >
                Cancelar
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
