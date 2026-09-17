from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Responsable
from app.schemas.responsable import ResponsableCreate, ResponsableUpdate


def crear_responsable(db: Session, data: ResponsableCreate) -> Responsable:
    nombre = data.nombre.strip()
    existente = db.scalar(select(Responsable).where(func.lower(Responsable.nombre) == nombre.lower()))
    if existente is not None:
        raise ValueError("Ya existe un responsable con ese nombre.")

    responsable = Responsable(nombre=nombre)
    db.add(responsable)
    db.commit()
    db.refresh(responsable)
    return responsable


def listar_responsables(db: Session, activo: bool | None = None) -> list[Responsable]:
    query = select(Responsable).order_by(Responsable.nombre)
    if activo is not None:
        query = query.where(Responsable.activo == activo)
    return list(db.scalars(query).all())


def obtener_responsable(db: Session, responsable_id: int) -> Responsable | None:
    return db.get(Responsable, responsable_id)


def actualizar_responsable(
    db: Session,
    responsable: Responsable,
    data: ResponsableUpdate,
) -> Responsable:
    cambios = data.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        nombre = cambios["nombre"].strip()
        existente = db.scalar(
            select(Responsable).where(
                func.lower(Responsable.nombre) == nombre.lower(),
                Responsable.id != responsable.id,
            )
        )
        if existente is not None:
            raise ValueError("Ya existe un responsable con ese nombre.")
        cambios["nombre"] = nombre

    for campo, valor in cambios.items():
        if valor is not None:
            setattr(responsable, campo, valor)

    db.commit()
    db.refresh(responsable)
    return responsable

