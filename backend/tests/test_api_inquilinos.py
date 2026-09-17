import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, CuentaCobro, Inquilino


class InquilinosApiTests(unittest.TestCase):
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

    def crear_responsable(self, nombre: str = "Billy") -> dict:
        response = self.client.post("/api/responsables", json={"nombre": nombre})
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_crea_responsable_e_inquilino_con_cuenta(self) -> None:
        responsable = self.crear_responsable()

        response = self.client.post(
            "/api/inquilinos",
            json={
                "responsable_id": responsable["id"],
                "nombre": "Baltazar",
                "telefono": "5555-0000",
                "plan_actual": "V",
                "dia_pago_actual": 15,
                "cuota_actual": "1050.00",
            },
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nombre"], "Baltazar")
        self.assertEqual(data["plan_actual"], "V")
        self.assertIsInstance(data["cuenta_cobro_id"], int)

        with self.Session() as database:
            self.assertEqual(len(database.scalars(select(CuentaCobro)).all()), 1)
            self.assertEqual(len(database.scalars(select(Inquilino)).all()), 1)

    def test_filtra_inquilinos_por_responsable_y_activo(self) -> None:
        billy = self.crear_responsable("Billy")
        lino = self.crear_responsable("Lino")

        for responsable, nombre in ((billy, "Baltazar"), (lino, "Edgar")):
            response = self.client.post(
                "/api/inquilinos",
                json={
                    "responsable_id": responsable["id"],
                    "nombre": nombre,
                    "plan_actual": "A",
                    "dia_pago_actual": 10,
                    "cuota_actual": "500.00",
                },
            )
            self.assertEqual(response.status_code, 201)

        response = self.client.get(f"/api/inquilinos?responsable_id={billy['id']}&activo=true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["nombre"] for item in response.json()], ["Baltazar"])

    def test_actualiza_y_desactiva_inquilino(self) -> None:
        responsable = self.crear_responsable()
        created = self.client.post(
            "/api/inquilinos",
            json={
                "responsable_id": responsable["id"],
                "nombre": "Pedro",
                "plan_actual": "A",
                "dia_pago_actual": 5,
                "cuota_actual": "700.00",
            },
        ).json()

        response = self.client.patch(
            f"/api/inquilinos/{created['id']}",
            json={"cuota_actual": "750.00", "activo": False},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cuota_actual"], "750.00")
        self.assertFalse(response.json()["activo"])

    def test_rechaza_responsable_duplicado(self) -> None:
        self.crear_responsable("Billy")
        response = self.client.post("/api/responsables", json={"nombre": "billy"})
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()

