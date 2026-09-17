from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.obligacion import ObligacionMensual
    from app.models.pago import Pago


class AplicacionPago(TimestampMixin, Base):
    __tablename__ = "aplicaciones_pago"
    __table_args__ = (
        UniqueConstraint("pago_id", "obligacion_id", name="uq_aplicacion_pago_obligacion"),
        CheckConstraint("monto_aplicado > 0", name="ck_aplicaciones_monto_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pago_id: Mapped[int] = mapped_column(
        ForeignKey("pagos.id", ondelete="RESTRICT"),
        index=True,
    )
    obligacion_id: Mapped[int] = mapped_column(
        ForeignKey("obligaciones_mensuales.id", ondelete="RESTRICT"),
        index=True,
    )
    monto_aplicado: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    pago: Mapped["Pago"] = relationship(back_populates="aplicaciones")
    obligacion: Mapped["ObligacionMensual"] = relationship(back_populates="aplicaciones")

