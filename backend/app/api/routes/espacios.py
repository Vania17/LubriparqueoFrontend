from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import TipoVehiculo
from app.schemas.espacio import EspacioCreate, EspacioRead, EspacioUpdate
from app.services.espacios import actualizar_espacio, crear_espacio, listar_espacios, obtener_espacio


router = APIRouter(prefix="/espacios", tags=["espacios"])
Database = Annotated[Session, Depends(get_db)]


@router.post("", response_model=EspacioRead, status_code=status.HTTP_201_CREATED)
def crear(data: EspacioCreate, db: Database) -> EspacioRead:
    try:
        return crear_espacio(db, data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("", response_model=list[EspacioRead])
def listar(
    db: Database,
    activo: Annotated[bool | None, Query()] = None,
    tipo: Annotated[TipoVehiculo | None, Query()] = None,
) -> list[EspacioRead]:
    return listar_espacios(db, activo, tipo)


@router.get("/{espacio_id}", response_model=EspacioRead)
def obtener(espacio_id: int, db: Database) -> EspacioRead:
    espacio = obtener_espacio(db, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    return espacio


@router.patch("/{espacio_id}", response_model=EspacioRead)
def actualizar(espacio_id: int, data: EspacioUpdate, db: Database) -> EspacioRead:
    espacio = obtener_espacio(db, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    try:
        return actualizar_espacio(db, espacio, data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

