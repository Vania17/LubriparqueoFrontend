from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class ObligacionParaAplicar:
    id: int
    cuenta_cobro_id: int
    periodo: date
    monto_cuota: Decimal
    total_aplicado: Decimal = Decimal("0.00")
    anulada: bool = False

    @property
    def saldo(self) -> Decimal:
        return max(self.monto_cuota - self.total_aplicado, Decimal("0.00"))


@dataclass(frozen=True)
class AplicacionPropuesta:
    obligacion_id: int
    monto: Decimal


@dataclass(frozen=True)
class DistribucionPropuesta:
    aplicaciones: tuple[AplicacionPropuesta, ...]
    saldo_a_favor: Decimal


def proponer_distribucion_pago(
    cuenta_cobro_id: int,
    monto_pago: Decimal,
    obligaciones: Iterable[ObligacionParaAplicar],
) -> DistribucionPropuesta:
    if monto_pago <= 0:
        raise ValueError("El monto del pago debe ser mayor que cero.")

    obligaciones_ordenadas = sorted(obligaciones, key=lambda item: (item.periodo, item.id))

    for obligacion in obligaciones_ordenadas:
        if obligacion.cuenta_cobro_id != cuenta_cobro_id:
            raise ValueError("Todas las obligaciones deben pertenecer a la misma cuenta de cobro.")
        if obligacion.monto_cuota < 0 or obligacion.total_aplicado < 0:
            raise ValueError("Los montos de las obligaciones no pueden ser negativos.")

    restante = monto_pago
    aplicaciones: list[AplicacionPropuesta] = []

    for obligacion in obligaciones_ordenadas:
        if restante == 0:
            break
        if obligacion.anulada or obligacion.saldo == 0:
            continue

        monto_aplicado = min(restante, obligacion.saldo)
        aplicaciones.append(
            AplicacionPropuesta(
                obligacion_id=obligacion.id,
                monto=monto_aplicado,
            )
        )
        restante -= monto_aplicado

    return DistribucionPropuesta(
        aplicaciones=tuple(aplicaciones),
        saldo_a_favor=restante,
    )

