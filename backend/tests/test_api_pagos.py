import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


class PagosApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.Session = sessionmaker(bind=cls.engine, expire_on_commit=False)

        def override_get_db():
            database = cls.Session()
            try:
                yield database
            finally:
                database.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.clear()
        cls.engine.dispose()

    def setUp(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        responsable = self.client.post("/api/responsables", json={"nombre": "Billy"}).json()
        self.inquilino = self.client.post(
            "/api/inquilinos",
            json={
                "responsable_id": responsable["id"],
                "nombre": "Baltazar",
                "plan_actual": "A",
                "dia_pago_actual": 5,
                "cuota_actual": "1000.00",
            },
        ).json()
        for periodo in ("2026-04-01", "2026-05-01"):
            response = self.client.post(
                "/api/obligaciones/generar",
                json={"periodo": periodo},
            )
            self.assertEqual(response.status_code, 201)

        self.obligaciones = self.client.get(
            "/api/obligaciones",
            params={"fecha_corte": "2026-04-01"},
        ).json()
        self.obligaciones.sort(key=lambda item: item["periodo"])

    def test_propone_aplicar_a_los_meses_mas_antiguos(self) -> None:
        response = self.client.post(
            "/api/pagos/proponer",
            json={
                "cuenta_cobro_id": self.inquilino["cuenta_cobro_id"],
                "monto_total": "1500.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            [(item["periodo"], item["monto"]) for item in data["aplicaciones"]],
            [("2026-04-01", "1000.00"), ("2026-05-01", "500.00")],
        )
        self.assertEqual(data["saldo_a_favor"], "0.00")

    def test_guarda_distribucion_confirmada_y_actualiza_saldos(self) -> None:
        response = self.client.post(
            "/api/pagos",
            json={
                "cuenta_cobro_id": self.inquilino["cuenta_cobro_id"],
                "monto_total": "1500.00",
                "fecha_pago": "2026-05-02",
                "aplicaciones": [
                    {"obligacion_id": self.obligaciones[0]["id"], "monto": "1000.00"},
                    {"obligacion_id": self.obligaciones[1]["id"], "monto": "500.00"},
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        listado = self.client.get(
            "/api/obligaciones",
            params={"fecha_corte": "2026-05-02"},
        ).json()
        listado.sort(key=lambda item: item["periodo"])
        self.assertEqual(listado[0]["estado"], "completo")
        self.assertEqual(listado[1]["total_pagado"], "500.00")
        self.assertEqual(listado[1]["saldo"], "500.00")

    def test_conserva_sobrante_como_saldo_a_favor(self) -> None:
        response = self.client.post(
            "/api/pagos",
            json={
                "cuenta_cobro_id": self.inquilino["cuenta_cobro_id"],
                "monto_total": "1300.00",
                "fecha_pago": "2026-04-03",
                "aplicaciones": [
                    {"obligacion_id": self.obligaciones[0]["id"], "monto": "1000.00"}
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["saldo_a_favor"], "300.00")

        saldo = self.client.get(
            f"/api/cuentas/{self.inquilino['cuenta_cobro_id']}/saldo-a-favor"
        )
        self.assertEqual(saldo.status_code, 200)
        self.assertEqual(saldo.json()["saldo_a_favor"], "300.00")

    def test_rechaza_aplicacion_superior_al_saldo(self) -> None:
        response = self.client.post(
            "/api/pagos",
            json={
                "cuenta_cobro_id": self.inquilino["cuenta_cobro_id"],
                "monto_total": "1200.00",
                "fecha_pago": "2026-04-03",
                "aplicaciones": [
                    {"obligacion_id": self.obligaciones[0]["id"], "monto": "1200.00"}
                ],
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

