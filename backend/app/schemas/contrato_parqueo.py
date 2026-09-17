from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import PlanPago


class ContratoParqueoCreate(BaseModel):
    vehiculo_id: int = Field(gt=0)
    espacio_id: int = Field(gt=0)
    responsable_id: int = Field(gt=0)
    cuota_mensual: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    plan_actual: PlanPago
    dia_pago: int = Field(ge=1, le=31)
    fecha_inicio: date
    fecha_fin: date | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial.")
        return self


class ContratoParqueoUpdate(BaseModel):
    vehiculo_id: int | None = Field(default=None, gt=0)
    espacio_id: int | None = Field(default=None, gt=0)
    responsable_id: int | None = Field(default=None, gt=0)
    cuota_mensual: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    plan_actual: PlanPago | None = None
    dia_pago: int | None = Field(default=None, ge=1, le=31)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activo: bool | None = None
    observaciones: str | None = None


class ContratoParqueoRead(BaseModel):
    id: int
    cuenta_cobro_id: int
    vehiculo_id: int
    vehiculo_placa: str | None
    propietario: str | None
    espacio_id: int
    espacio_codigo: str
    responsable_id: int
    responsable: str
    cuota_mensual: Decimal
    plan_actual: PlanPago
    dia_pago: int
    fecha_inicio: date
    fecha_fin: date | None
    activo: bool
    observaciones: str | None

