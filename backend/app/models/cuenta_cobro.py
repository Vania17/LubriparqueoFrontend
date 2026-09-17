from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TipoCuentaCobro, enum_values

if TYPE_CHECKING:
    from app.models.contrato_parqueo import ContratoParqueoMensual
    from app.models.inquilino import Inquilino
    from app.models.obligacion import ObligacionMensual
    from app.models.pago import Pago


class CuentaCobro(TimestampMixin, Base):
    __tablename__ = "cuentas_cobro"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoCuentaCobro] = mapped_column(
        Enum(
            TipoCuentaCobro,
            native_enum=False,
            length=30,
            values_callable=enum_values,
        ),
        index=True,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    inquilino: Mapped["Inquilino | None"] = relationship(back_populates="cuenta_cobro")
    contrato_parqueo: Mapped["ContratoParqueoMensual | None"] = relationship(
        back_populates="cuenta_cobro"
    )
    obligaciones: Mapped[list["ObligacionMensual"]] = relationship(back_populates="cuenta_cobro")
    pagos: Mapped[list["Pago"]] = relationship(back_populates="cuenta_cobro")
