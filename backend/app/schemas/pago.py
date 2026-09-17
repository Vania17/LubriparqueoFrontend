from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PropuestaPagoRequest(BaseModel):
    cuenta_cobro_id: int = Field(gt=0)
    monto_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AplicacionPagoInput(BaseModel):
    obligacion_id: int = Field(gt=0)
    monto: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AplicacionPagoRead(BaseModel):
    obligacion_id: int
    periodo: date
    monto: Decimal


class PropuestaPagoResponse(BaseModel):
    cuenta_cobro_id: int
    monto_total: Decimal
    aplicaciones: list[AplicacionPagoRead]
    saldo_a_favor: Decimal


class PagoCreate(BaseModel):
    cuenta_cobro_id: int = Field(gt=0)
    monto_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    fecha_pago: date
    aplicaciones: list[AplicacionPagoInput] = Field(default_factory=list)
    observaciones: str | None = None


class PagoRead(BaseModel):
    id: int
    cuenta_cobro_id: int
    monto_total: Decimal
    fecha_pago: date
    aplicaciones: list[AplicacionPagoRead]
    saldo_a_favor: Decimal
    observaciones: str | None
    anulado: bool


class SaldoFavorRead(BaseModel):
    cuenta_cobro_id: int
    saldo_a_favor: Decimal

