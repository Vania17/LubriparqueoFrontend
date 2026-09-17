from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import PlanPago, enum_values

if TYPE_CHECKING:
    from app.models.cuenta_cobro import CuentaCobro
    from app.models.responsable import Responsable


class Inquilino(TimestampMixin, Base):
    __tablename__ = "inquilinos"
    __table_args__ = (
        CheckConstraint("dia_pago_actual BETWEEN 1 AND 31", name="ck_inquilinos_dia_pago"),
        CheckConstraint("cuota_actual >= 0", name="ck_inquilinos_cuota_no_negativa"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_cobro_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_cobro.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
    )
    responsable_id: Mapped[int] = mapped_column(
        ForeignKey("responsables.id", ondelete="RESTRICT"),
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(200), index=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    plan_actual: Mapped[PlanPago] = mapped_column(
        Enum(PlanPago, native_enum=False, length=1, values_callable=enum_values)
    )
    dia_pago_actual: Mapped[int]
    cuota_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    referencia_carta_legacy: Mapped[str | None] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    cuenta_cobro: Mapped["CuentaCobro"] = relationship(back_populates="inquilino")
    responsable: Mapped["Responsable"] = relationship(back_populates="inquilinos")
