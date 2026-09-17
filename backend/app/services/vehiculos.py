from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Vehiculo
from app.models.enums import TipoVehiculo
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate


def _normalizar_placa(placa: str | None) -> str | None:
    if placa is None or not placa.strip():
        return None
    return placa.strip().upper()


def _validar_placa(db: Session, placa: str | None, excluir_id: int | None = None) -> None:
    if placa is None:
        return
    query = select(Vehiculo).where(func.lower(Vehiculo.placa) == placa.lower())
    if excluir_id is not None:
        query = query.where(Vehiculo.id != excluir_id)
    if db.scalar(query) is not None:
        raise ValueError("Ya existe un vehiculo con esa placa.")


def crear_vehiculo(db: Session, data: VehiculoCreate) -> Vehiculo:
    placa = _normalizar_placa(data.placa)
    _validar_placa(db, placa)
    vehiculo = Vehiculo(
        placa=placa,
        tipo=data.tipo,
        propietario=data.propietario,
        telefono=data.telefono,
        observaciones=data.observaciones,
    )
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def listar_vehiculos(db: Session, tipo: TipoVehiculo | None = None) -> list[Vehiculo]:
    query = select(Vehiculo).order_by(Vehiculo.propietario, Vehiculo.placa)
    if tipo is not None:
        query = query.where(Vehiculo.tipo == tipo)
    return list(db.scalars(query).all())


def obtener_vehiculo(db: Session, vehiculo_id: int) -> Vehiculo | None:
    return db.get(Vehiculo, vehiculo_id)


def actualizar_vehiculo(db: Session, vehiculo: Vehiculo, data: VehiculoUpdate) -> Vehiculo:
    cambios = data.model_dump(exclude_unset=True)
    if "placa" in cambios:
        placa = _normalizar_placa(cambios["placa"])
        _validar_placa(db, placa, vehiculo.id)
        cambios["placa"] = placa

    for campo, valor in cambios.items():
        setattr(vehiculo, campo, valor)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

