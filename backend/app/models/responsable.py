from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contrato_parqueo import ContratoParqueoMensual
    from app.models.inquilino import Inquilino


class Responsable(TimestampMixin, Base):
    __tablename__ = "responsables"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    inquilinos: Mapped[list["Inquilino"]] = relationship(back_populates="responsable")
    contratos_parqueo: Mapped[list["ContratoParqueoMensual"]] = relationship(
        back_populates="responsable"
    )
