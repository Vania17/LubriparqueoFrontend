from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TipoVehiculo, enum_values

if TYPE_CHECKING:
    from app.models.contrato_parqueo import ContratoParqueoMensual


class EspacioParqueo(TimestampMixin, Base):
    __tablename__ = "espacios_parqueo"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    tipo_vehiculo: Mapped[TipoVehiculo] = mapped_column(
        Enum(TipoVehiculo, native_enum=False, length=20, values_callable=enum_values),
        index=True,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    observaciones: Mapped[str | None] = mapped_column(Text)

    contratos: Mapped[list["ContratoParqueoMensual"]] = relationship(back_populates="espacio")

