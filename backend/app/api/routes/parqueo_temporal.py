from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OcupacionTemporal
from app.schemas.parqueo_temporal import (
    LiberacionCreate,
    LiberacionRead,
    OcupacionCreate,
    OcupacionRead,
    RegistrarSalida,
)
from app.services.parqueo_temporal import (
    crear_liberacion,
    crear_ocupacion,
    listar_liberaciones,
    listar_ocupaciones,
    ocupacion_read,
    registrar_salida,
)


router = APIRouter(tags=["parqueo-temporal"])
Database = Annotated[Session, Depends(get_db)]


@router.post("/liberaciones", response_model=LiberacionRead, status_code=201)
def liberar(data: LiberacionCreate, db: Database):
    try:
        return crear_liberacion(db, data)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/liberaciones", response_model=list[LiberacionRead])
def liberaciones(db: Database):
    return listar_liberaciones(db)


@router.post("/ocupaciones", response_model=OcupacionRead, status_code=201)
def entrada(data: OcupacionCreate, db: Database):
    try:
        return ocupacion_read(crear_ocupacion(db, data))
    except LookupError as error:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.patch("/ocupaciones/{ocupacion_id}/salida", response_model=OcupacionRead)
def salida(ocupacion_id: int, data: RegistrarSalida, db: Database):
    ocupacion = db.get(OcupacionTemporal, ocupacion_id)
    if ocupacion is None:
        raise HTTPException(status_code=404, detail="Ocupacion no encontrada.")
    try:
        return ocupacion_read(registrar_salida(db, ocupacion, data))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/ocupaciones", response_model=list[OcupacionRead])
def ocupaciones(db: Database, abiertas: Annotated[bool | None, Query()] = None):
    return [ocupacion_read(item) for item in listar_ocupaciones(db, abiertas)]
