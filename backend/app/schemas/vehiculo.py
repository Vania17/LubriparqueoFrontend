from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TipoVehiculo


class VehiculoCreate(BaseModel):
    placa: str | None = Field(default=None, max_length=30)
    tipo: TipoVehiculo
    propietario: str | None = Field(default=None, max_length=200)
    telefono: str | None = Field(default=None, max_length=30)
    observaciones: str | None = None


class VehiculoUpdate(BaseModel):
    placa: str | None = Field(default=None, max_length=30)
    tipo: TipoVehiculo | None = None
    propietario: str | None = Field(default=None, max_length=200)
    telefono: str | None = Field(default=None, max_length=30)
    observaciones: str | None = None


class VehiculoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str | None
    tipo: TipoVehiculo
    propietario: str | None
    telefono: str | None
    observaciones: str | None

