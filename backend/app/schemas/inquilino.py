from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PlanPago


class InquilinoCreate(BaseModel):
    responsable_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=200)
    telefono: str | None = Field(default=None, max_length=30)
    plan_actual: PlanPago
    dia_pago_actual: int = Field(ge=1, le=31)
    cuota_actual: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    referencia_carta_legacy: str | None = None
    observaciones: str | None = None


class InquilinoUpdate(BaseModel):
    responsable_id: int | None = Field(default=None, gt=0)
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    telefono: str | None = Field(default=None, max_length=30)
    plan_actual: PlanPago | None = None
    dia_pago_actual: int | None = Field(default=None, ge=1, le=31)
    cuota_actual: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    referencia_carta_legacy: str | None = None
    observaciones: str | None = None
    activo: bool | None = None


class InquilinoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cuenta_cobro_id: int
    responsable_id: int
    nombre: str
    telefono: str | None
    plan_actual: PlanPago
    dia_pago_actual: int
    cuota_actual: Decimal
    referencia_carta_legacy: str | None
    observaciones: str | None
    activo: bool

