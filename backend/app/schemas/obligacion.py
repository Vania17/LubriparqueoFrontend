from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.enums import EstadoPago, PlanPago, TipoCuentaCobro


class GenerarObligacionesRequest(BaseModel):
    periodo: date
    responsable_id: int | None = Field(default=None, gt=0)

    @field_validator("periodo")
    @classmethod
    def validar_primer_dia(cls, value: date) -> date:
        if value.day != 1:
            raise ValueError("El periodo debe usar el primer dia del mes.")
        return value


class GenerarObligacionesResponse(BaseModel):
    periodo: date
    creadas: int
    omitidas: int


class ObligacionRead(BaseModel):
    id: int
    cuenta_cobro_id: int
    tipo_cuenta: TipoCuentaCobro
    titular: str
    inquilino_id: int | None
    inquilino: str | None
    contrato_parqueo_id: int | None
    vehiculo_id: int | None
    vehiculo_placa: str | None
    responsable_id: int
    periodo: date
    plan_aplicado: PlanPago
    dia_pago_aplicado: int
    monto_cuota: Decimal
    fecha_limite: date
    total_pagado: Decimal
    saldo: Decimal
    estado: EstadoPago
    anulada: bool
