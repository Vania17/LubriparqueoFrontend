from datetime import datetime
from decimal import Decimal
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ContratoParqueoMensual,
    EspacioParqueo,
    LiberacionTemporal,
    OcupacionTemporal,
    Responsable,
    Vehiculo,
)
from app.models.enums import TipoTarifa
from app.schemas.parqueo_temporal import LiberacionCreate, OcupacionCreate, RegistrarSalida


def crear_liberacion(db: Session, data: LiberacionCreate) -> LiberacionTemporal:
    contrato = db.get(ContratoParqueoMensual, data.contrato_mensual_id)
    if contrato is None or not contrato.activo:
        raise LookupError("Contrato mensual no encontrado o inactivo.")
    liberacion = LiberacionTemporal(**data.model_dump())
    db.add(liberacion)
    db.commit()
    db.refresh(liberacion)
    return liberacion


def listar_liberaciones(db: Session) -> list[LiberacionTemporal]:
    return list(db.scalars(select(LiberacionTemporal).order_by(LiberacionTemporal.disponible_desde.desc())).all())


def crear_ocupacion(db: Session, data: OcupacionCreate) -> OcupacionTemporal:
    espacio = db.get(EspacioParqueo, data.espacio_id)
    vehiculo = db.get(Vehiculo, data.vehiculo_id)
    responsable = db.get(Responsable, data.responsable_id)
    if espacio is None or not espacio.activo:
        raise LookupError("Espacio no encontrado o inactivo.")
    if vehiculo is None:
        raise LookupError("Vehiculo no encontrado.")
    if responsable is None or not responsable.activo:
        raise LookupError("Responsable no encontrado o inactivo.")

    abierta = db.scalar(
        select(OcupacionTemporal).where(
            OcupacionTemporal.espacio_id == data.espacio_id,
            OcupacionTemporal.fecha_hora_salida.is_(None),
            OcupacionTemporal.anulado.is_(False),
        )
    )
    if abierta is not None:
        raise ValueError("El espacio ya esta ocupado.")

    contrato = db.scalar(
        select(ContratoParqueoMensual).where(
            ContratoParqueoMensual.espacio_id == data.espacio_id,
            ContratoParqueoMensual.activo.is_(True),
        )
    )
    if contrato is not None:
        liberacion = db.get(LiberacionTemporal, data.liberacion_temporal_id)
        if (
            liberacion is None
            or liberacion.contrato_mensual_id != contrato.id
            or not (liberacion.disponible_desde <= data.fecha_hora_entrada < liberacion.disponible_hasta)
        ):
            raise ValueError("El espacio mensual requiere una liberacion temporal vigente.")

    ocupacion = OcupacionTemporal(**data.model_dump())
    db.add(ocupacion)
    db.commit()
    db.refresh(ocupacion)
    return ocupacion


def registrar_salida(db: Session, ocupacion: OcupacionTemporal, data: RegistrarSalida) -> OcupacionTemporal:
    if ocupacion.fecha_hora_salida is not None:
        raise ValueError("La ocupacion ya fue cerrada.")
    if data.fecha_hora_salida < ocupacion.fecha_hora_entrada:
        raise ValueError("La salida no puede ser anterior a la entrada.")

    segundos = max((data.fecha_hora_salida - ocupacion.fecha_hora_entrada).total_seconds(), 1)
    if ocupacion.tipo_tarifa == TipoTarifa.POR_HORA:
        monto = Decimal(ceil(segundos / 3600)) * ocupacion.tarifa
    elif ocupacion.tipo_tarifa == TipoTarifa.DIARIA:
        monto = Decimal(ceil(segundos / 86400)) * ocupacion.tarifa
    else:
        monto = data.monto_acordado if data.monto_acordado is not None else ocupacion.tarifa

    ocupacion.fecha_hora_salida = data.fecha_hora_salida
    ocupacion.monto_cobrado = monto
    db.commit()
    db.refresh(ocupacion)
    return ocupacion


def listar_ocupaciones(db: Session, abiertas: bool | None = None) -> list[OcupacionTemporal]:
    query = select(OcupacionTemporal).order_by(OcupacionTemporal.fecha_hora_entrada.desc())
    if abiertas is True:
        query = query.where(OcupacionTemporal.fecha_hora_salida.is_(None))
    elif abiertas is False:
        query = query.where(OcupacionTemporal.fecha_hora_salida.is_not(None))
    return list(db.scalars(query).all())


def ocupacion_read(item: OcupacionTemporal) -> dict:
    return {
        "id": item.id,
        "vehiculo_id": item.vehiculo_id,
        "placa": item.vehiculo.placa,
        "espacio_id": item.espacio_id,
        "espacio": item.espacio.codigo,
        "responsable_id": item.responsable_id,
        "fecha_hora_entrada": item.fecha_hora_entrada,
        "fecha_hora_salida": item.fecha_hora_salida,
        "tipo_tarifa": item.tipo_tarifa,
        "tarifa": item.tarifa,
        "monto_cobrado": item.monto_cobrado,
        "liberacion_temporal_id": item.liberacion_temporal_id,
        "observaciones": item.observaciones,
        "anulado": item.anulado,
    }
