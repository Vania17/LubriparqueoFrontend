from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AplicacionPago, CuentaCobro, ObligacionMensual, Pago
from app.schemas.pago import PagoCreate, PropuestaPagoRequest
from app.services.aplicacion_pagos import ObligacionParaAplicar, proponer_distribucion_pago


def _cuenta(db: Session, cuenta_cobro_id: int) -> CuentaCobro:
    cuenta = db.get(CuentaCobro, cuenta_cobro_id)
    if cuenta is None:
        raise LookupError("Cuenta de cobro no encontrada.")
    return cuenta


def _total_aplicado_obligacion(db: Session, obligacion_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(AplicacionPago.monto_aplicado), 0))
        .join(Pago, Pago.id == AplicacionPago.pago_id)
        .where(
            AplicacionPago.obligacion_id == obligacion_id,
            Pago.anulado.is_(False),
        )
    )
    return Decimal(total or 0)


def _obligaciones_pendientes(db: Session, cuenta_cobro_id: int) -> list[ObligacionParaAplicar]:
    obligaciones = db.scalars(
        select(ObligacionMensual)
        .where(ObligacionMensual.cuenta_cobro_id == cuenta_cobro_id)
        .order_by(ObligacionMensual.periodo, ObligacionMensual.id)
    ).all()

    return [
        ObligacionParaAplicar(
            id=item.id,
            cuenta_cobro_id=item.cuenta_cobro_id,
            periodo=item.periodo,
            monto_cuota=item.monto_cuota,
            total_aplicado=_total_aplicado_obligacion(db, item.id),
            anulada=item.anulada,
        )
        for item in obligaciones
    ]


def proponer_pago(db: Session, data: PropuestaPagoRequest) -> dict:
    _cuenta(db, data.cuenta_cobro_id)
    obligaciones = _obligaciones_pendientes(db, data.cuenta_cobro_id)
    propuesta = proponer_distribucion_pago(
        data.cuenta_cobro_id,
        data.monto_total,
        obligaciones,
    )
    periodos = {item.id: item.periodo for item in obligaciones}

    return {
        "cuenta_cobro_id": data.cuenta_cobro_id,
        "monto_total": data.monto_total,
        "aplicaciones": [
            {
                "obligacion_id": item.obligacion_id,
                "periodo": periodos[item.obligacion_id],
                "monto": item.monto,
            }
            for item in propuesta.aplicaciones
        ],
        "saldo_a_favor": propuesta.saldo_a_favor,
    }


def crear_pago(db: Session, data: PagoCreate) -> Pago:
    _cuenta(db, data.cuenta_cobro_id)

    ids = [item.obligacion_id for item in data.aplicaciones]
    if len(ids) != len(set(ids)):
        raise ValueError("No puede repetirse una obligacion en el mismo pago.")

    obligaciones = {}
    if ids:
        obligaciones = {
            item.id: item
            for item in db.scalars(
                select(ObligacionMensual).where(ObligacionMensual.id.in_(ids))
            ).all()
        }
        if len(obligaciones) != len(ids):
            raise LookupError("Una o mas obligaciones no existen.")

    total_distribuido = Decimal("0.00")
    for aplicacion in data.aplicaciones:
        obligacion = obligaciones[aplicacion.obligacion_id]
        if obligacion.cuenta_cobro_id != data.cuenta_cobro_id:
            raise ValueError("La obligacion pertenece a otra cuenta de cobro.")
        if obligacion.anulada:
            raise ValueError("No se puede pagar una obligacion anulada.")

        saldo = max(
            obligacion.monto_cuota - _total_aplicado_obligacion(db, obligacion.id),
            Decimal("0.00"),
        )
        if aplicacion.monto > saldo:
            raise ValueError("La aplicacion supera el saldo de la obligacion.")
        total_distribuido += aplicacion.monto

    if total_distribuido > data.monto_total:
        raise ValueError("Las aplicaciones superan el monto total del pago.")

    pago = Pago(
        cuenta_cobro_id=data.cuenta_cobro_id,
        monto_total=data.monto_total,
        fecha_pago=data.fecha_pago,
        observaciones=data.observaciones,
    )
    db.add(pago)
    db.flush()

    for aplicacion in data.aplicaciones:
        db.add(
            AplicacionPago(
                pago_id=pago.id,
                obligacion_id=aplicacion.obligacion_id,
                monto_aplicado=aplicacion.monto,
            )
        )

    db.commit()
    db.refresh(pago)
    return pago


def calcular_saldo_a_favor(db: Session, cuenta_cobro_id: int) -> Decimal:
    _cuenta(db, cuenta_cobro_id)
    total_pagos = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(Pago.monto_total), 0)).where(
                Pago.cuenta_cobro_id == cuenta_cobro_id,
                Pago.anulado.is_(False),
            )
        )
        or 0
    )
    total_aplicado = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(AplicacionPago.monto_aplicado), 0))
            .join(Pago, Pago.id == AplicacionPago.pago_id)
            .where(
                Pago.cuenta_cobro_id == cuenta_cobro_id,
                Pago.anulado.is_(False),
            )
        )
        or 0
    )
    return total_pagos - total_aplicado


def _pago_read(db: Session, pago: Pago) -> dict:
    aplicaciones = db.execute(
        select(AplicacionPago, ObligacionMensual)
        .join(ObligacionMensual, ObligacionMensual.id == AplicacionPago.obligacion_id)
        .where(AplicacionPago.pago_id == pago.id)
        .order_by(ObligacionMensual.periodo)
    ).all()
    total_aplicado = sum((item.monto_aplicado for item, _ in aplicaciones), Decimal("0.00"))

    return {
        "id": pago.id,
        "cuenta_cobro_id": pago.cuenta_cobro_id,
        "monto_total": pago.monto_total,
        "fecha_pago": pago.fecha_pago,
        "aplicaciones": [
            {
                "obligacion_id": aplicacion.obligacion_id,
                "periodo": obligacion.periodo,
                "monto": aplicacion.monto_aplicado,
            }
            for aplicacion, obligacion in aplicaciones
        ],
        "saldo_a_favor": pago.monto_total - total_aplicado,
        "observaciones": pago.observaciones,
        "anulado": pago.anulado,
    }


def listar_pagos(db: Session, cuenta_cobro_id: int | None = None) -> list[dict]:
    query = select(Pago).order_by(Pago.fecha_pago.desc(), Pago.id.desc())
    if cuenta_cobro_id is not None:
        query = query.where(Pago.cuenta_cobro_id == cuenta_cobro_id)
    return [_pago_read(db, item) for item in db.scalars(query).all()]


def obtener_pago(db: Session, pago_id: int) -> dict | None:
    pago = db.get(Pago, pago_id)
    return None if pago is None else _pago_read(db, pago)

