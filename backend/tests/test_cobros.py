import unittest
from datetime import date
from decimal import Decimal

from app.models.enums import EstadoPago, PlanPago
from app.services.cobros import calcular_fecha_limite, calcular_saldo, determinar_estado_pago


class FechaLimiteTests(unittest.TestCase):
    def test_plan_anticipado_vence_en_el_mismo_mes(self) -> None:
        resultado = calcular_fecha_limite(date(2026, 5, 1), 15, PlanPago.ANTICIPADO)
        self.assertEqual(resultado, date(2026, 5, 15))

    def test_plan_vencido_vence_el_dia_anterior_del_mes_siguiente(self) -> None:
        resultado = calcular_fecha_limite(date(2026, 5, 1), 15, PlanPago.VENCIDO)
        self.assertEqual(resultado, date(2026, 6, 14))

    def test_anticipado_usa_el_ultimo_dia_valido(self) -> None:
        resultado = calcular_fecha_limite(date(2026, 4, 1), 31, PlanPago.ANTICIPADO)
        self.assertEqual(resultado, date(2026, 4, 30))

    def test_vencido_usa_el_ultimo_dia_valido(self) -> None:
        resultado = calcular_fecha_limite(date(2026, 1, 1), 31, PlanPago.VENCIDO)
        self.assertEqual(resultado, date(2026, 2, 28))

    def test_vencido_dia_uno_vence_al_final_del_periodo(self) -> None:
        resultado = calcular_fecha_limite(date(2026, 5, 1), 1, PlanPago.VENCIDO)
        self.assertEqual(resultado, date(2026, 5, 31))

    def test_rechaza_dia_fuera_de_rango(self) -> None:
        with self.assertRaises(ValueError):
            calcular_fecha_limite(date(2026, 5, 1), 32, PlanPago.ANTICIPADO)


class EstadoPagoTests(unittest.TestCase):
    def test_calcula_saldo_sin_permitir_valor_negativo(self) -> None:
        saldo = calcular_saldo(Decimal("1000.00"), Decimal("1200.00"))
        self.assertEqual(saldo, Decimal("0.00"))

    def test_completo(self) -> None:
        estado = determinar_estado_pago(
            Decimal("1000.00"), Decimal("1000.00"), date(2026, 5, 15), date(2026, 5, 20)
        )
        self.assertEqual(estado, EstadoPago.COMPLETO)

    def test_parcial_antes_del_vencimiento(self) -> None:
        estado = determinar_estado_pago(
            Decimal("1000.00"), Decimal("400.00"), date(2026, 5, 15), date(2026, 5, 10)
        )
        self.assertEqual(estado, EstadoPago.PARCIAL)

    def test_pendiente_antes_del_vencimiento(self) -> None:
        estado = determinar_estado_pago(
            Decimal("1000.00"), Decimal("0.00"), date(2026, 5, 15), date(2026, 5, 10)
        )
        self.assertEqual(estado, EstadoPago.PENDIENTE)

    def test_no_es_moroso_en_la_fecha_limite(self) -> None:
        estado = determinar_estado_pago(
            Decimal("1000.00"), Decimal("0.00"), date(2026, 5, 15), date(2026, 5, 15)
        )
        self.assertEqual(estado, EstadoPago.PENDIENTE)

    def test_moroso_despues_del_vencimiento(self) -> None:
        estado = determinar_estado_pago(
            Decimal("1000.00"), Decimal("400.00"), date(2026, 5, 15), date(2026, 5, 16)
        )
        self.assertEqual(estado, EstadoPago.MOROSO)

    def test_rechaza_montos_negativos(self) -> None:
        with self.assertRaises(ValueError):
            calcular_saldo(Decimal("1000.00"), Decimal("-1.00"))


if __name__ == "__main__":
    unittest.main()

