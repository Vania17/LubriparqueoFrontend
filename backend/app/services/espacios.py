from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import EspacioParqueo
from app.models.enums import TipoVehiculo
from app.schemas.espacio import EspacioCreate, EspacioUpdate


def crear_espacio(db: Session, data: EspacioCreate) -> EspacioParqueo:
    codigo = data.codigo.strip().upper()
    existente = db.scalar(
        select(EspacioParqueo).where(func.lower(EspacioParqueo.codigo) == codigo.lower())
    )
    if existente is not None:
        raise ValueError("Ya existe un espacio con ese codigo.")

    espacio = EspacioParqueo(
        codigo=codigo,
        tipo_vehiculo=data.tipo_vehiculo,
        observaciones=data.observaciones,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def listar_espacios(
    db: Session,
    activo: bool | None = None,
    tipo: TipoVehiculo | None = None,
) -> list[EspacioParqueo]:
    query = select(EspacioParqueo).order_by(EspacioParqueo.codigo)
    if activo is not None:
        query = query.where(EspacioParqueo.activo == activo)
    if tipo is not None:
        query = query.where(EspacioParqueo.tipo_vehiculo == tipo)
    return list(db.scalars(query).all())


def obtener_espacio(db: Session, espacio_id: int) -> EspacioParqueo | None:
    return db.get(EspacioParqueo, espacio_id)


def actualizar_espacio(db: Session, espacio: EspacioParqueo, data: EspacioUpdate) -> EspacioParqueo:
    cambios = data.model_dump(exclude_unset=True)
    if "codigo" in cambios and cambios["codigo"] is not None:
        codigo = cambios["codigo"].strip().upper()
        existente = db.scalar(
            select(EspacioParqueo).where(
                func.lower(EspacioParqueo.codigo) == codigo.lower(),
                EspacioParqueo.id != espacio.id,
            )
        )
        if existente is not None:
            raise ValueError("Ya existe un espacio con ese codigo.")
        cambios["codigo"] = codigo

    for campo, valor in cambios.items():
        setattr(espacio, campo, valor)
    db.commit()
    db.refresh(espacio)
    return espacio

