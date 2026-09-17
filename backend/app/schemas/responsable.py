from pydantic import BaseModel, ConfigDict, Field


class ResponsableCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


class ResponsableUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    activo: bool | None = None


class ResponsableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    activo: bool

