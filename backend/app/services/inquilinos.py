from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CuentaCobro, Inquilino, Responsable
from app.models.enums import TipoCuentaCobro
from app.schemas.inquilino import InquilinoCreate, InquilinoUpdate


def _responsable_activo(db: Session, responsable_id: int) -> Responsable | None:
    return db.scalar(
        select(Responsable).where(
            Responsable.id == responsable_id,
            Responsable.activo.is_(True),
        )
    )


def crear_inquilino(db: Session, data: InquilinoCreate) -> Inquilino:
    if _responsable_activo(db, data.responsable_id) is None:
        raise LookupError("El responsable no existe o esta inactivo.")

    cuenta = CuentaCobro(tipo=TipoCuentaCobro.INQUILINO)
    db.add(cuenta)
    db.flush()

    inquilino = Inquilino(
        cuenta_cobro_id=cuenta.id,
        responsable_id=data.responsable_id,
        nombre=data.nombre.strip(),
        telefono=data.telefono,
        plan_actual=data.plan_actual,
        dia_pago_actual=data.dia_pago_actual,
        cuota_actual=data.cuota_actual,
        referencia_carta_legacy=data.referencia_carta_legacy,
        observaciones=data.observaciones,
    )
    db.add(inquilino)
    db.commit()
    db.refresh(inquilino)
    return inquilino


def listar_inquilinos(
    db: Session,
    responsable_id: int | None = None,
    activo: bool | None = None,
) -> list[Inquilino]:
    query = select(Inquilino).order_by(Inquilino.nombre)
    if responsable_id is not None:
        query = query.where(Inquilino.responsable_id == responsable_id)
    if activo is not None:
        query = query.where(Inquilino.activo == activo)
    return list(db.scalars(query).all())


def obtener_inquilino(db: Session, inquilino_id: int) -> Inquilino | None:
    return db.get(Inquilino, inquilino_id)


def actualizar_inquilino(
    db: Session,
    inquilino: Inquilino,
    data: InquilinoUpdate,
) -> Inquilino:
    cambios = data.model_dump(exclude_unset=True)

    if "responsable_id" in cambios:
        responsable_id = cambios["responsable_id"]
        if responsable_id is None or _responsable_activo(db, responsable_id) is None:
            raise LookupError("El responsable no existe o esta inactivo.")

    if "nombre" in cambios and cambios["nombre"] is not None:
        cambios["nombre"] = cambios["nombre"].strip()

    for campo, valor in cambios.items():
        setattr(inquilino, campo, valor)

    db.commit()
    db.refresh(inquilino)
    return inquilino

