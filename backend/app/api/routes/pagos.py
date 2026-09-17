from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pago import (
    PagoCreate,
    PagoRead,
    PropuestaPagoRequest,
    PropuestaPagoResponse,
    SaldoFavorRead,
)
from app.services.pagos import (
    calcular_saldo_a_favor,
    crear_pago,
    listar_pagos,
    obtener_pago,
    proponer_pago,
)


router = APIRouter(tags=["pagos"])
Database = Annotated[Session, Depends(get_db)]


@router.post("/pagos/proponer", response_model=PropuestaPagoResponse)
def proponer(data: PropuestaPagoRequest, db: Database) -> PropuestaPagoResponse:
    try:
        return proponer_pago(db, data)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/pagos", response_model=PagoRead, status_code=status.HTTP_201_CREATED)
def crear(data: PagoCreate, db: Database) -> PagoRead:
    try:
        pago = crear_pago(db, data)
        resultado = obtener_pago(db, pago.id)
        assert resultado is not None
        return resultado
    except LookupError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error


@router.get("/pagos", response_model=list[PagoRead])
def listar(
    db: Database,
    cuenta_cobro_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[PagoRead]:
    return listar_pagos(db, cuenta_cobro_id)


@router.get("/pagos/{pago_id}", response_model=PagoRead)
def obtener(pago_id: int, db: Database) -> PagoRead:
    pago = obtener_pago(db, pago_id)
    if pago is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado.")
    return pago


@router.get("/cuentas/{cuenta_cobro_id}/saldo-a-favor", response_model=SaldoFavorRead)
def saldo_a_favor(cuenta_cobro_id: int, db: Database) -> SaldoFavorRead:
    try:
        saldo = calcular_saldo_a_favor(db, cuenta_cobro_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return SaldoFavorRead(cuenta_cobro_id=cuenta_cobro_id, saldo_a_favor=saldo)
