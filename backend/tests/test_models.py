import unittest

from sqlalchemy import create_engine, inspect

from app.models import Base


class ModelMetadataTests(unittest.TestCase):
    def test_creates_initial_financial_tables(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)

        table_names = set(inspect(engine).get_table_names())

        self.assertEqual(
            table_names,
            {
                "aplicaciones_pago",
                "contratos_parqueo_mensual",
                "cuentas_cobro",
                "espacios_parqueo",
                "inquilinos",
                "liberaciones_temporales",
                "obligaciones_mensuales",
                "ocupaciones_temporales",
                "pagos",
                "responsables",
                "vehiculos",
            },
        )


if __name__ == "__main__":
    unittest.main()
