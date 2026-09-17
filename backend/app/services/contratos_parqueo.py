from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ContratoParqueoMensual,
    CuentaCobro,
    EspacioParqueo,
    Responsable,
    Vehiculo,
)
from app.models.enums import TipoCuentaCobro
from app.schemas.contrato_parqueo import ContratoParqueoCreate, ContratoParqueoUpdate


def _entidades_activas(
    db: Session,
    vehiculo_id: int,
    espacio_id: int,
    responsable_id: int,
) -> tuple[Vehiculo, EspacioParqueo, Responsable]:
    vehiculo = db.get(Vehiculo, vehiculo_id)
    espacio = db.get(EspacioParqueo, espacio_id)
    responsable = db.get(Responsable, responsable_id)
    if vehiculo is None:
        raise LookupError("Vehiculo no encontrado.")
    if espacio is None or not espacio.activo:
        raise LookupError("Espacio no encontrado o inactivo.")
    if responsable is None or not responsable.activo:
        raise LookupError("Responsable no encontrado o inactivo.")
    return vehiculo, espacio, responsable


def _validar_disponibilidad(
    db: Session,
    vehiculo_id: int,
    espacio_id: int,
    excluir_id: int | None = None,
) -> None:
    query = select(ContratoParqueoMensual).where(
        ContratoParqueoMensual.activo.is_(True),
        (
            (ContratoParqueoMensual.espacio_id == espacio_id)
            | (ContratoParqueoMensual.vehiculo_id == vehiculo_id)
        ),
    )
    if excluir_id is not None:
        query = query.where(ContratoParqueoMensual.id != excluir_id)
    existente = db.scalar(query)
    if existente is not None:
        if existente.espacio_id == espacio_id:
            raise ValueError("El espacio ya tiene un contrato activo.")
        raise ValueError("El vehiculo ya tiene un contrato activo.")


def _validar_fechas(fecha_inicio, fecha_fin) -> None:
    if fecha_fin is not None and fecha_fin < fecha_inicio:
        raise ValueError("La fecha final no puede ser anterior a la fecha inicial.")


def crear_contrato(db: Session, data: ContratoParqueoCreate) -> ContratoParqueoMensual:
    _entidades_activas(db, data.vehiculo_id, data.espacio_id, data.responsable_id)
    _validar_disponibilidad(db, data.vehiculo_id, data.espacio_id)

    cuenta = CuentaCobro(tipo=TipoCuentaCobro.PARQUEO_MENSUAL)
    db.add(cuenta)
    db.flush()

    contrato = ContratoParqueoMensual(
        cuenta_cobro_id=cuenta.id,
        vehiculo_id=data.vehiculo_id,
        espacio_id=data.espacio_id,
        responsable_id=data.responsable_id,
        cuota_mensual=data.cuota_mensual,
        plan_actual=data.plan_actual,
        dia_pago=data.dia_pago,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        observaciones=data.observaciones,
    )
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


def listar_contratos(
    db: Session,
    activo: bool | None = None,
    responsable_id: int | None = None,
) -> list[ContratoParqueoMensual]:
    query = select(ContratoParqueoMensual).order_by(ContratoParqueoMensual.id)
    if activo is not None:
        query = query.where(ContratoParqueoMensual.activo == activo)
    if responsable_id is not None:
        query = query.where(ContratoParqueoMensual.responsable_id == responsable_id)
    return list(db.scalars(query).all())


def obtener_contrato(db: Session, contrato_id: int) -> ContratoParqueoMensual | None:
    return db.get(ContratoParqueoMensual, contrato_id)


def actualizar_contrato(
    db: Session,
    contrato: ContratoParqueoMensual,
    data: ContratoParqueoUpdate,
) -> ContratoParqueoMensual:
    cambios = data.model_dump(exclude_unset=True)
    vehiculo_id = cambios.get("vehiculo_id", contrato.vehiculo_id)
    espacio_id = cambios.get("espacio_id", contrato.espacio_id)
    responsable_id = cambios.get("responsable_id", contrato.responsable_id)
    activo = cambios.get("activo", contrato.activo)
    fecha_inicio = cambios.get("fecha_inicio", contrato.fecha_inicio)
    fecha_fin = cambios.get("fecha_fin", contrato.fecha_fin)

    _entidades_activas(db, vehiculo_id, espacio_id, responsable_id)
    _validar_fechas(fecha_inicio, fecha_fin)
    if activo:
        _validar_disponibilidad(db, vehiculo_id, espacio_id, contrato.id)

    for campo, valor in cambios.items():
        setattr(contrato, campo, valor)
    contrato.cuenta_cobro.activo = activo

    db.commit()
    db.refresh(contrato)
    return contrato


def contrato_read(contrato: ContratoParqueoMensual) -> dict:
    return {
        "id": contrato.id,
        "cuenta_cobro_id": contrato.cuenta_cobro_id,
        "vehiculo_id": contrato.vehiculo_id,
        "vehiculo_placa": contrato.vehiculo.placa,
        "propietario": contrato.vehiculo.propietario,
        "espacio_id": contrato.espacio_id,
        "espacio_codigo": contrato.espacio.codigo,
        "responsable_id": contrato.responsable_id,
        "responsable": contrato.responsable.nombre,
        "cuota_mensual": contrato.cuota_mensual,
        "plan_actual": contrato.plan_actual,
        "dia_pago": contrato.dia_pago,
        "fecha_inicio": contrato.fecha_inicio,
        "fecha_fin": contrato.fecha_fin,
        "activo": contrato.activo,
        "observaciones": contrato.observaciones,
    }

