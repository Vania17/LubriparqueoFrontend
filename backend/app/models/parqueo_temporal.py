from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TipoTarifa, enum_values

if TYPE_CHECKING:
    from app.models.contrato_parqueo import ContratoParqueoMensual
    from app.models.espacio import EspacioParqueo
    from app.models.responsable import Responsable
    from app.models.vehiculo import Vehiculo


class LiberacionTemporal(TimestampMixin, Base):
    __tablename__ = "liberaciones_temporales"
    __table_args__ = (
        CheckConstraint("disponible_hasta > disponible_desde", name="ck_liberaciones_horario"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_mensual_id: Mapped[int] = mapped_column(
        ForeignKey("contratos_parqueo_mensual.id", ondelete="RESTRICT"), index=True
    )
    disponible_desde: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    disponible_hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    observaciones: Mapped[str | None] = mapped_column(Text)

    contrato: Mapped["ContratoParqueoMensual"] = relationship()


class OcupacionTemporal(TimestampMixin, Base):
    __tablename__ = "ocupaciones_temporales"
    __table_args__ = (
        CheckConstraint(
            "fecha_hora_salida IS NULL OR fecha_hora_salida >= fecha_hora_entrada",
            name="ck_ocupaciones_horario",
        ),
        CheckConstraint("tarifa >= 0", name="ck_ocupaciones_tarifa_no_negativa"),
        CheckConstraint(
            "monto_cobrado IS NULL OR monto_cobrado >= 0",
            name="ck_ocupaciones_cobro_no_negativo",
        ),
        Index(
            "uq_ocupaciones_espacio_abierto",
            "espacio_id",
            unique=True,
            sqlite_where=text("fecha_hora_salida IS NULL AND anulado = 0"),
            postgresql_where=text("fecha_hora_salida IS NULL AND anulado = false"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id", ondelete="RESTRICT"), index=True)
    espacio_id: Mapped[int] = mapped_column(
        ForeignKey("espacios_parqueo.id", ondelete="RESTRICT"), index=True
    )
    liberacion_temporal_id: Mapped[int | None] = mapped_column(
        ForeignKey("liberaciones_temporales.id", ondelete="RESTRICT"), index=True
    )
    responsable_id: Mapped[int] = mapped_column(
        ForeignKey("responsables.id", ondelete="RESTRICT"), index=True
    )
    fecha_hora_entrada: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    fecha_hora_salida: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    tipo_tarifa: Mapped[TipoTarifa] = mapped_column(
        Enum(TipoTarifa, native_enum=False, length=20, values_callable=enum_values)
    )
    tarifa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    monto_cobrado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    observaciones: Mapped[str | None] = mapped_column(Text)
    anulado: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    vehiculo: Mapped["Vehiculo"] = relationship()
    espacio: Mapped["EspacioParqueo"] = relationship()
    liberacion: Mapped["LiberacionTemporal | None"] = relationship()
    responsable: Mapped["Responsable"] = relationship()
