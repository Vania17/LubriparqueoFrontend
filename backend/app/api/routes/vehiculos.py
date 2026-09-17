from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import TipoVehiculo
from app.schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate
from app.services.vehiculos import actualizar_vehiculo, crear_vehiculo, listar_vehiculos, obtener_vehiculo


router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])
Database = Annotated[Session, Depends(get_db)]


@router.post("", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED)
def crear(data: VehiculoCreate, db: Database) -> VehiculoRead:
    try:
        return crear_vehiculo(db, data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[VehiculoRead])
def listar(
    db: Database,
    tipo: Annotated[TipoVehiculo | None, Query()] = None,
) -> list[VehiculoRead]:
    return listar_vehiculos(db, tipo)


@router.get("/{vehiculo_id}", response_model=VehiculoRead)
def obtener(vehiculo_id: int, db: Database) -> VehiculoRead:
    vehiculo = obtener_vehiculo(db, vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado.")
    return vehiculo


@router.patch("/{vehiculo_id}", response_model=VehiculoRead)
def actualizar(vehiculo_id: int, data: VehiculoUpdate, db: Database) -> VehiculoRead:
    vehiculo = obtener_vehiculo(db, vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado.")
    try:
        return actualizar_vehiculo(db, vehiculo, data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

