from calendar import monthrange
from datetime import date
from decimal import Decimal

from app.models.enums import EstadoPago, PlanPago


def _ultimo_dia_del_mes(year: int, month: int) -> int:
    return monthrange(year, month)[1]


def _mes_siguiente(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def calcular_fecha_limite(periodo: date, dia_pago: int, plan: PlanPago) -> date:
    if not 1 <= dia_pago <= 31:
        raise ValueError("El dia de pago debe estar entre 1 y 31.")

    if plan == PlanPago.ANTICIPADO:
        ultimo_dia = _ultimo_dia_del_mes(periodo.year, periodo.month)
        return date(periodo.year, periodo.month, min(dia_pago, ultimo_dia))

    if plan == PlanPago.VENCIDO:
        if dia_pago == 1:
            ultimo_dia = _ultimo_dia_del_mes(periodo.year, periodo.month)
            return date(periodo.year, periodo.month, ultimo_dia)

        year, month = _mes_siguiente(periodo.year, periodo.month)
        ultimo_dia = _ultimo_dia_del_mes(year, month)
        return date(year, month, min(dia_pago - 1, ultimo_dia))

    raise ValueError("El plan de pago no es valido.")


def calcular_saldo(monto_cuota: Decimal, total_pagado: Decimal) -> Decimal:
    if monto_cuota < 0 or total_pagado < 0:
        raise ValueError("Los montos no pueden ser negativos.")

    return max(monto_cuota - total_pagado, Decimal("0.00"))


def determinar_estado_pago(
    monto_cuota: Decimal,
    total_pagado: Decimal,
    fecha_limite: date,
    fecha_corte: date,
) -> EstadoPago:
    saldo = calcular_saldo(monto_cuota, total_pagado)

    if saldo == 0:
        return EstadoPago.COMPLETO
    if fecha_corte > fecha_limite:
        return EstadoPago.MOROSO
    if total_pagado > 0:
        return EstadoPago.PARCIAL
    return EstadoPago.PENDIENTE

