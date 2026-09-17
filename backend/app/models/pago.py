from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.aplicacion_pago import AplicacionPago
    from app.models.cuenta_cobro import CuentaCobro


class Pago(TimestampMixin, Base):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint("monto_total > 0", name="ck_pagos_monto_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_cobro_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_cobro.id", ondelete="RESTRICT"),
        index=True,
    )
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fecha_pago: Mapped[date] = mapped_column(Date, index=True)
    observaciones: Mapped[str | None] = mapped_column(Text)
    anulado: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    motivo_anulacion: Mapped[str | None] = mapped_column(Text)

    cuenta_cobro: Mapped["CuentaCobro"] = relationship(back_populates="pagos")
    aplicaciones: Mapped[list["AplicacionPago"]] = relationship(back_populates="pago")

