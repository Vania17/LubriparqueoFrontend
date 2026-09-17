from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AplicacionPago,
    ContratoParqueoMensual,
    CuentaCobro,
    Inquilino,
    ObligacionMensual,
    Pago,
    Responsable,
    Vehiculo,
)
from app.models.enums import EstadoPago, TipoCuentaCobro
from app.schemas.obligacion import GenerarObligacionesRequest
from app.services.cobros import calcular_fecha_limite, calcular_saldo, determinar_estado_pago


def generar_obligaciones(
    db: Session,
    data: GenerarObligacionesRequest,
) -> tuple[int, int]:
    inquilinos_query = (
        select(Inquilino)
        .join(CuentaCobro, CuentaCobro.id == Inquilino.cuenta_cobro_id)
        .join(Responsable, Responsable.id == Inquilino.responsable_id)
        .where(
            Inquilino.activo.is_(True),
            CuentaCobro.activo.is_(True),
            Responsable.activo.is_(True),
        )
        .order_by(Inquilino.id)
    )
    if data.responsable_id is not None:
        inquilinos_query = inquilinos_query.where(
            Inquilino.responsable_id == data.responsable_id
        )

    inquilinos = list(db.scalars(inquilinos_query).all())

    ultimo_dia = monthrange(data.periodo.year, data.periodo.month)[1]
    fin_periodo = date(data.periodo.year, data.periodo.month, ultimo_dia)
    contratos_query = (
        select(ContratoParqueoMensual)
        .join(CuentaCobro, CuentaCobro.id == ContratoParqueoMensual.cuenta_cobro_id)
        .join(Responsable, Responsable.id == ContratoParqueoMensual.responsable_id)
        .where(
            ContratoParqueoMensual.activo.is_(True),
            CuentaCobro.activo.is_(True),
            Responsable.activo.is_(True),
            ContratoParqueoMensual.fecha_inicio <= fin_periodo,
            (
                ContratoParqueoMensual.fecha_fin.is_(None)
                | (ContratoParqueoMensual.fecha_fin >= data.periodo)
            ),
        )
        .order_by(ContratoParqueoMensual.id)
    )
    if data.responsable_id is not None:
        contratos_query = contratos_query.where(
            ContratoParqueoMensual.responsable_id == data.responsable_id
        )

    contratos = list(db.scalars(contratos_query).all())

    cuentas = [item.cuenta_cobro_id for item in inquilinos]
    cuentas.extend(item.cuenta_cobro_id for item in contratos)

    existentes: set[int] = set()
    if cuentas:
        existentes = set(
            db.scalars(
                select(ObligacionMensual.cuenta_cobro_id).where(
                    ObligacionMensual.periodo == data.periodo,
                    ObligacionMensual.cuenta_cobro_id.in_(cuentas),
                )
            ).all()
        )

    creadas = 0
    omitidas = 0

    for inquilino in inquilinos:
        if inquilino.cuenta_cobro_id in existentes:
            omitidas += 1
            continue

        obligacion = ObligacionMensual(
            cuenta_cobro_id=inquilino.cuenta_cobro_id,
            periodo=data.periodo,
            plan_aplicado=inquilino.plan_actual,
            dia_pago_aplicado=inquilino.dia_pago_actual,
            monto_cuota=inquilino.cuota_actual,
            fecha_limite=calcular_fecha_limite(
                data.periodo,
                inquilino.dia_pago_actual,
                inquilino.plan_actual,
            ),
        )
        db.add(obligacion)
        creadas += 1

    for contrato in contratos:
        if contrato.cuenta_cobro_id in existentes:
            omitidas += 1
            continue

        obligacion = ObligacionMensual(
            cuenta_cobro_id=contrato.cuenta_cobro_id,
            periodo=data.periodo,
            plan_aplicado=contrato.plan_actual,
            dia_pago_aplicado=contrato.dia_pago,
            monto_cuota=contrato.cuota_mensual,
            fecha_limite=calcular_fecha_limite(
                data.periodo,
                contrato.dia_pago,
                contrato.plan_actual,
            ),
        )
        db.add(obligacion)
        creadas += 1

    db.commit()
    return creadas, omitidas


def _total_pagado(db: Session, obligacion_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(AplicacionPago.monto_aplicado), 0))
        .join(Pago, Pago.id == AplicacionPago.pago_id)
        .where(
            AplicacionPago.obligacion_id == obligacion_id,
            Pago.anulado.is_(False),
        )
    )
    return Decimal(total or 0)


def _convertir_resumen(
    db: Session,
    obligacion: ObligacionMensual,
    fecha_corte: date,
) -> dict:
    total_pagado = _total_pagado(db, obligacion.id)
    saldo = calcular_saldo(obligacion.monto_cuota, total_pagado)
    estado = determinar_estado_pago(
        obligacion.monto_cuota,
        total_pagado,
        obligacion.fecha_limite,
        fecha_corte,
    )

    cuenta = db.get(CuentaCobro, obligacion.cuenta_cobro_id)
    if cuenta is None:
        raise LookupError("La obligacion no tiene una cuenta de cobro valida.")

    inquilino = None
    contrato = None
    vehiculo = None
    if cuenta.tipo == TipoCuentaCobro.INQUILINO:
        inquilino = db.scalar(
            select(Inquilino).where(Inquilino.cuenta_cobro_id == cuenta.id)
        )
        if inquilino is None:
            raise LookupError("La cuenta no tiene un inquilino asociado.")
        titular = inquilino.nombre
        responsable_id = inquilino.responsable_id
    else:
        contrato = db.scalar(
            select(ContratoParqueoMensual).where(
                ContratoParqueoMensual.cuenta_cobro_id == cuenta.id
            )
        )
        if contrato is None:
            raise LookupError("La cuenta no tiene un contrato de parqueo asociado.")
        vehiculo = db.get(Vehiculo, contrato.vehiculo_id)
        if vehiculo is None:
            raise LookupError("El contrato no tiene un vehiculo valido.")
        titular = vehiculo.propietario or vehiculo.placa or f"Vehiculo {vehiculo.id}"
        responsable_id = contrato.responsable_id

    return {
        "id": obligacion.id,
        "cuenta_cobro_id": obligacion.cuenta_cobro_id,
        "tipo_cuenta": cuenta.tipo,
        "titular": titular,
        "inquilino_id": inquilino.id if inquilino else None,
        "inquilino": inquilino.nombre if inquilino else None,
        "contrato_parqueo_id": contrato.id if contrato else None,
        "vehiculo_id": vehiculo.id if vehiculo else None,
        "vehiculo_placa": vehiculo.placa if vehiculo else None,
        "responsable_id": responsable_id,
        "periodo": obligacion.periodo,
        "plan_aplicado": obligacion.plan_aplicado,
        "dia_pago_aplicado": obligacion.dia_pago_aplicado,
        "monto_cuota": obligacion.monto_cuota,
        "fecha_limite": obligacion.fecha_limite,
        "total_pagado": total_pagado,
        "saldo": saldo,
        "estado": estado,
        "anulada": obligacion.anulada,
    }


def listar_obligaciones(
    db: Session,
    periodo: date | None = None,
    responsable_id: int | None = None,
    estado: EstadoPago | None = None,
    fecha_corte: date | None = None,
) -> list[dict]:
    corte = fecha_corte or date.today()
    query = select(ObligacionMensual).order_by(
        ObligacionMensual.periodo.desc(),
        ObligacionMensual.id,
    )
    if periodo is not None:
        query = query.where(ObligacionMensual.periodo == periodo)
    if responsable_id is not None:
        cuentas_inquilinos = select(Inquilino.cuenta_cobro_id).where(
            Inquilino.responsable_id == responsable_id
        )
        cuentas_contratos = select(ContratoParqueoMensual.cuenta_cobro_id).where(
            ContratoParqueoMensual.responsable_id == responsable_id
        )
        query = query.where(
            ObligacionMensual.cuenta_cobro_id.in_(cuentas_inquilinos.union(cuentas_contratos))
        )

    resultados = [
        _convertir_resumen(db, obligacion, corte)
        for obligacion in db.scalars(query).all()
    ]
    if estado is not None:
        resultados = [item for item in resultados if item["estado"] == estado]
    return resultados


def obtener_obligacion(
    db: Session,
    obligacion_id: int,
    fecha_corte: date | None = None,
) -> dict | None:
    obligacion = db.get(ObligacionMensual, obligacion_id)
    if obligacion is None:
        return None
    return _convertir_resumen(db, obligacion, fecha_corte or date.today())
