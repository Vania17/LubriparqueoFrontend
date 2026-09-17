from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import EstadoPago
from app.schemas.obligacion import (
    GenerarObligacionesRequest,
    GenerarObligacionesResponse,
    ObligacionRead,
)
from app.services.obligaciones import generar_obligaciones, listar_obligaciones, obtener_obligacion


router = APIRouter(prefix="/obligaciones", tags=["obligaciones"])
Database = Annotated[Session, Depends(get_db)]


@router.post(
    "/generar",
    response_model=GenerarObligacionesResponse,
    status_code=status.HTTP_201_CREATED,
)
def generar(
    data: GenerarObligacionesRequest,
    db: Database,
) -> GenerarObligacionesResponse:
    creadas, omitidas = generar_obligaciones(db, data)
    return GenerarObligacionesResponse(
        periodo=data.periodo,
        creadas=creadas,
        omitidas=omitidas,
    )


@router.get("", response_model=list[ObligacionRead])
def listar(
    db: Database,
    periodo: Annotated[date | None, Query()] = None,
    responsable_id: Annotated[int | None, Query(gt=0)] = None,
    estado: Annotated[EstadoPago | None, Query()] = None,
    fecha_corte: Annotated[date | None, Query()] = None,
) -> list[ObligacionRead]:
    return listar_obligaciones(db, periodo, responsable_id, estado, fecha_corte)


@router.get("/{obligacion_id}", response_model=ObligacionRead)
def obtener(
    obligacion_id: int,
    db: Database,
    fecha_corte: Annotated[date | None, Query()] = None,
) -> ObligacionRead:
    obligacion = obtener_obligacion(db, obligacion_id, fecha_corte)
    if obligacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligacion no encontrada.")
    return obligacion

