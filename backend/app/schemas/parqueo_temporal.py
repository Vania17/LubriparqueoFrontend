from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import TipoTarifa


class LiberacionCreate(BaseModel):
    contrato_mensual_id: int = Field(gt=0)
    disponible_desde: datetime
    disponible_hasta: datetime
    observaciones: str | None = None

    @model_validator(mode="after")
    def validar_horario(self):
        if self.disponible_hasta <= self.disponible_desde:
            raise ValueError("La liberacion debe terminar despues de iniciar.")
        return self


class LiberacionRead(LiberacionCreate):
    id: int


class OcupacionCreate(BaseModel):
    vehiculo_id: int = Field(gt=0)
    espacio_id: int = Field(gt=0)
    responsable_id: int = Field(gt=0)
    fecha_hora_entrada: datetime
    tipo_tarifa: TipoTarifa
    tarifa: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    liberacion_temporal_id: int | None = Field(default=None, gt=0)
    observaciones: str | None = None


class RegistrarSalida(BaseModel):
    fecha_hora_salida: datetime
    monto_acordado: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)


class OcupacionRead(BaseModel):
    id: int
    vehiculo_id: int
    placa: str | None
    espacio_id: int
    espacio: str
    responsable_id: int
    fecha_hora_entrada: datetime
    fecha_hora_salida: datetime | None
    tipo_tarifa: TipoTarifa
    tarifa: Decimal
    monto_cobrado: Decimal | None
    liberacion_temporal_id: int | None
    observaciones: str | None
    anulado: bool

