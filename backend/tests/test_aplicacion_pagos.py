import unittest
from datetime import date
from decimal import Decimal

from app.services.aplicacion_pagos import ObligacionParaAplicar, proponer_distribucion_pago


def obligacion(
    identificador: int,
    periodo: date,
    cuota: str = "1000.00",
    aplicado: str = "0.00",
    cuenta: int = 1,
    anulada: bool = False,
) -> ObligacionParaAplicar:
    return ObligacionParaAplicar(
        id=identificador,
        cuenta_cobro_id=cuenta,
        periodo=periodo,
        monto_cuota=Decimal(cuota),
        total_aplicado=Decimal(aplicado),
        anulada=anulada,
    )


class DistribucionPagoTests(unittest.TestCase):
    def test_aplica_primero_a_la_obligacion_mas_antigua(self) -> None:
        resultado = proponer_distribucion_pago(
            1,
            Decimal("1000.00"),
            [
                obligacion(2, date(2026, 5, 1)),
                obligacion(1, date(2026, 4, 1)),
            ],
        )

        self.assertEqual(resultado.aplicaciones[0].obligacion_id, 1)
        self.assertEqual(resultado.aplicaciones[0].monto, Decimal("1000.00"))

    def test_distribuye_un_pago_entre_varios_meses(self) -> None:
        resultado = proponer_distribucion_pago(
            1,
            Decimal("1500.00"),
            [
                obligacion(1, date(2026, 4, 1)),
                obligacion(2, date(2026, 5, 1)),
            ],
        )

        self.assertEqual(
            [(item.obligacion_id, item.monto) for item in resultado.aplicaciones],
            [(1, Decimal("1000.00")), (2, Decimal("500.00"))],
        )
        self.assertEqual(resultado.saldo_a_favor, Decimal("0.00"))

    def test_respeta_abonos_anteriores(self) -> None:
        resultado = proponer_distribucion_pago(
            1,
            Decimal("900.00"),
            [
                obligacion(1, date(2026, 4, 1), aplicado="400.00"),
                obligacion(2, date(2026, 5, 1)),
            ],
        )

        self.assertEqual(
            [(item.obligacion_id, item.monto) for item in resultado.aplicaciones],
            [(1, Decimal("600.00")), (2, Decimal("300.00"))],
        )

    def test_omite_obligaciones_completas_y_anuladas(self) -> None:
        resultado = proponer_distribucion_pago(
            1,
            Decimal("500.00"),
            [
                obligacion(1, date(2026, 3, 1), aplicado="1000.00"),
                obligacion(2, date(2026, 4, 1), anulada=True),
                obligacion(3, date(2026, 5, 1)),
            ],
        )

        self.assertEqual(len(resultado.aplicaciones), 1)
        self.assertEqual(resultado.aplicaciones[0].obligacion_id, 3)

    def test_deja_el_sobrante_como_saldo_a_favor(self) -> None:
        resultado = proponer_distribucion_pago(
            1,
            Decimal("1300.00"),
            [obligacion(1, date(2026, 5, 1))],
        )

        self.assertEqual(resultado.aplicaciones[0].monto, Decimal("1000.00"))
        self.assertEqual(resultado.saldo_a_favor, Decimal("300.00"))

    def test_saldo_completo_si_no_hay_obligaciones(self) -> None:
        resultado = proponer_distribucion_pago(1, Decimal("300.00"), [])
        self.assertEqual(resultado.aplicaciones, ())
        self.assertEqual(resultado.saldo_a_favor, Decimal("300.00"))

    def test_rechaza_obligaciones_de_otra_cuenta(self) -> None:
        with self.assertRaises(ValueError):
            proponer_distribucion_pago(
                1,
                Decimal("500.00"),
                [obligacion(1, date(2026, 5, 1), cuenta=2)],
            )

    def test_rechaza_pago_no_positivo(self) -> None:
        with self.assertRaises(ValueError):
            proponer_distribucion_pago(1, Decimal("0.00"), [])


if __name__ == "__main__":
    unittest.main()

