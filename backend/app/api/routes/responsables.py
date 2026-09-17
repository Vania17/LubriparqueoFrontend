from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.responsable import ResponsableCreate, ResponsableRead, ResponsableUpdate
from app.services.responsables import (
    actualizar_responsable,
    crear_responsable,
    listar_responsables,
    obtener_responsable,
)


router = APIRouter(prefix="/responsables", tags=["responsables"])
Database = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ResponsableRead, status_code=status.HTTP_201_CREATED)
def crear(data: ResponsableCreate, db: Database) -> ResponsableRead:
    try:
        return crear_responsable(db, data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("", response_model=list[ResponsableRead])
def listar(db: Database, activo: Annotated[bool | None, Query()] = None) -> list[ResponsableRead]:
    return listar_responsables(db, activo)


@router.get("/{responsable_id}", response_model=ResponsableRead)
def obtener(responsable_id: int, db: Database) -> ResponsableRead:
    responsable = obtener_responsable(db, responsable_id)
    if responsable is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsable no encontrado.")
    return responsable


@router.patch("/{responsable_id}", response_model=ResponsableRead)
def actualizar(
    responsable_id: int,
    data: ResponsableUpdate,
    db: Database,
) -> ResponsableRead:
    responsable = obtener_responsable(db, responsable_id)
    if responsable is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsable no encontrado.")
    try:
        return actualizar_responsable(db, responsable, data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

