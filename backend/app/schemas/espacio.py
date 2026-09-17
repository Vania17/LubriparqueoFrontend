from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TipoVehiculo


class EspacioCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    tipo_vehiculo: TipoVehiculo
    observaciones: str | None = None


class EspacioUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)
    tipo_vehiculo: TipoVehiculo | None = None
    activo: bool | None = None
    observaciones: str | None = None


class EspacioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    tipo_vehiculo: TipoVehiculo
    activo: bool
    observaciones: str | None

