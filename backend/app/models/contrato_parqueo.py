from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import PlanPago, enum_values

if TYPE_CHECKING:
    from app.models.cuenta_cobro import CuentaCobro
    from app.models.espacio import EspacioParqueo
    from app.models.responsable import Responsable
    from app.models.vehiculo import Vehiculo


class ContratoParqueoMensual(TimestampMixin, Base):
    __tablename__ = "contratos_parqueo_mensual"
    __table_args__ = (
        CheckConstraint("cuota_mensual >= 0", name="ck_contratos_cuota_no_negativa"),
        CheckConstraint("dia_pago BETWEEN 1 AND 31", name="ck_contratos_dia_pago"),
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_fin >= fecha_inicio",
            name="ck_contratos_fechas_validas",
        ),
        Index(
            "uq_contratos_espacio_activo",
            "espacio_id",
            unique=True,
            sqlite_where=text("activo = 1"),
            postgresql_where=text("activo = true"),
        ),
        Index(
            "uq_contratos_vehiculo_activo",
            "vehiculo_id",
            unique=True,
            sqlite_where=text("activo = 1"),
            postgresql_where=text("activo = true"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_cobro_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_cobro.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
    )
    vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey("vehiculos.id", ondelete="RESTRICT"),
        index=True,
    )
    espacio_id: Mapped[int] = mapped_column(
        ForeignKey("espacios_parqueo.id", ondelete="RESTRICT"),
        index=True,
    )
    responsable_id: Mapped[int] = mapped_column(
        ForeignKey("responsables.id", ondelete="RESTRICT"),
        index=True,
    )
    cuota_mensual: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    plan_actual: Mapped[PlanPago] = mapped_column(
        Enum(PlanPago, native_enum=False, length=1, values_callable=enum_values)
    )
    dia_pago: Mapped[int]
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    observaciones: Mapped[str | None] = mapped_column(Text)

    cuenta_cobro: Mapped["CuentaCobro"] = relationship(back_populates="contrato_parqueo")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="contratos")
    espacio: Mapped["EspacioParqueo"] = relationship(back_populates="contratos")
    responsable: Mapped["Responsable"] = relationship(back_populates="contratos_parqueo")

