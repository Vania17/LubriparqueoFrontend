from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.contrato_parqueo import (
    ContratoParqueoCreate,
    ContratoParqueoRead,
    ContratoParqueoUpdate,
)
from app.services.contratos_parqueo import (
    actualizar_contrato,
    contrato_read,
    crear_contrato,
    listar_contratos,
    obtener_contrato,
)


router = APIRouter(prefix="/contratos-parqueo", tags=["contratos-parqueo"])
Database = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ContratoParqueoRead, status_code=status.HTTP_201_CREATED)
def crear(data: ContratoParqueoCreate, db: Database) -> ContratoParqueoRead:
    try:
        return contrato_read(crear_contrato(db, data))
    except LookupError as error:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[ContratoParqueoRead])
def listar(
    db: Database,
    activo: Annotated[bool | None, Query()] = None,
    responsable_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[ContratoParqueoRead]:
    return [contrato_read(item) for item in listar_contratos(db, activo, responsable_id)]


@router.get("/{contrato_id}", response_model=ContratoParqueoRead)
def obtener(contrato_id: int, db: Database) -> ContratoParqueoRead:
    contrato = obtener_contrato(db, contrato_id)
    if contrato is None:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    return contrato_read(contrato)


@router.patch("/{contrato_id}", response_model=ContratoParqueoRead)
def actualizar(
    contrato_id: int,
    data: ContratoParqueoUpdate,
    db: Database,
) -> ContratoParqueoRead:
    contrato = obtener_contrato(db, contrato_id)
    if contrato is None:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    try:
        return contrato_read(actualizar_contrato(db, contrato, data))
    except LookupError as error:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error

