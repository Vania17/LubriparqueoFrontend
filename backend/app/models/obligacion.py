from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, Enum, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import PlanPago, enum_values

if TYPE_CHECKING:
    from app.models.aplicacion_pago import AplicacionPago
    from app.models.cuenta_cobro import CuentaCobro


class ObligacionMensual(TimestampMixin, Base):
    __tablename__ = "obligaciones_mensuales"
    __table_args__ = (
        UniqueConstraint("cuenta_cobro_id", "periodo", name="uq_obligacion_cuenta_periodo"),
        CheckConstraint("dia_pago_aplicado BETWEEN 1 AND 31", name="ck_obligaciones_dia_pago"),
        CheckConstraint("monto_cuota >= 0", name="ck_obligaciones_monto_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_cobro_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_cobro.id", ondelete="RESTRICT"),
        index=True,
    )
    periodo: Mapped[date] = mapped_column(Date, index=True)
    plan_aplicado: Mapped[PlanPago] = mapped_column(
        Enum(PlanPago, native_enum=False, length=1, values_callable=enum_values)
    )
    dia_pago_aplicado: Mapped[int]
    monto_cuota: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fecha_limite: Mapped[date] = mapped_column(Date, index=True)
    anulada: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    motivo_anulacion: Mapped[str | None] = mapped_column(Text)

    cuenta_cobro: Mapped["CuentaCobro"] = relationship(back_populates="obligaciones")
    aplicaciones: Mapped[list["AplicacionPago"]] = relationship(back_populates="obligacion")
