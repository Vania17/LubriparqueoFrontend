from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TipoVehiculo, enum_values

if TYPE_CHECKING:
    from app.models.contrato_parqueo import ContratoParqueoMensual


class Vehiculo(TimestampMixin, Base):
    __tablename__ = "vehiculos"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)
    tipo: Mapped[TipoVehiculo] = mapped_column(
        Enum(TipoVehiculo, native_enum=False, length=20, values_callable=enum_values),
        index=True,
    )
    propietario: Mapped[str | None] = mapped_column(String(200), index=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    observaciones: Mapped[str | None] = mapped_column(Text)

    contratos: Mapped[list["ContratoParqueoMensual"]] = relationship(back_populates="vehiculo")

