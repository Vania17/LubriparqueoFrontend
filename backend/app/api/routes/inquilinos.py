from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inquilino import InquilinoCreate, InquilinoRead, InquilinoUpdate
from app.services.inquilinos import (
    actualizar_inquilino,
    crear_inquilino,
    listar_inquilinos,
    obtener_inquilino,
)


router = APIRouter(prefix="/inquilinos", tags=["inquilinos"])
Database = Annotated[Session, Depends(get_db)]


@router.post("", response_model=InquilinoRead, status_code=status.HTTP_201_CREATED)
def crear(data: InquilinoCreate, db: Database) -> InquilinoRead:
    try:
        return crear_inquilino(db, data)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error


@router.get("", response_model=list[InquilinoRead])
def listar(
    db: Database,
    responsable_id: Annotated[int | None, Query(gt=0)] = None,
    activo: Annotated[bool | None, Query()] = None,
) -> list[InquilinoRead]:
    return listar_inquilinos(db, responsable_id, activo)


@router.get("/{inquilino_id}", response_model=InquilinoRead)
def obtener(inquilino_id: int, db: Database) -> InquilinoRead:
    inquilino = obtener_inquilino(db, inquilino_id)
    if inquilino is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquilino no encontrado.")
    return inquilino


@router.patch("/{inquilino_id}", response_model=InquilinoRead)
def actualizar(
    inquilino_id: int,
    data: InquilinoUpdate,
    db: Database,
) -> InquilinoRead:
    inquilino = obtener_inquilino(db, inquilino_id)
    if inquilino is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquilino no encontrado.")
    try:
        return actualizar_inquilino(db, inquilino, data)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
