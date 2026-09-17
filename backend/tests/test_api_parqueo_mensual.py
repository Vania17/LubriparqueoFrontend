import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, CuentaCobro


class ParqueoMensualApiTests(unittest.TestCase):
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
        self.responsable = self.client.post("/api/responsables", json={"nombre": "Billy"}).json()

    def crear_espacio(self, codigo: str = "A-01") -> dict:
        response = self.client.post(
            "/api/espacios",
            json={"codigo": codigo, "tipo_vehiculo": "carro"},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def crear_vehiculo(self, placa: str, propietario: str) -> dict:
        response = self.client.post(
            "/api/vehiculos",
            json={"placa": placa, "tipo": "carro", "propietario": propietario},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def crear_contrato(self, espacio: dict, vehiculo: dict) -> dict:
        response = self.client.post(
            "/api/contratos-parqueo",
            json={
                "vehiculo_id": vehiculo["id"],
                "espacio_id": espacio["id"],
                "responsable_id": self.responsable["id"],
                "cuota_mensual": "500.00",
                "plan_actual": "A",
                "dia_pago": 5,
                "fecha_inicio": "2026-06-01",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_crea_espacio_vehiculo_y_contrato_con_cuenta(self) -> None:
        espacio = self.crear_espacio()
        vehiculo = self.crear_vehiculo("P-123ABC", "Cliente fijo")
        contrato = self.crear_contrato(espacio, vehiculo)

        self.assertEqual(contrato["espacio_codigo"], "A-01")
        self.assertEqual(contrato["vehiculo_placa"], "P-123ABC")
        self.assertTrue(contrato["activo"])

        with self.Session() as database:
            cuenta = database.scalar(
                select(CuentaCobro).where(CuentaCobro.id == contrato["cuenta_cobro_id"])
            )
            self.assertEqual(cuenta.tipo.value, "parqueo_mensual")

    def test_rechaza_dos_contratos_activos_en_el_mismo_espacio(self) -> None:
        espacio = self.crear_espacio()
        primero = self.crear_vehiculo("P-111AAA", "Primero")
        segundo = self.crear_vehiculo("P-222BBB", "Segundo")
        self.crear_contrato(espacio, primero)

        response = self.client.post(
            "/api/contratos-parqueo",
            json={
                "vehiculo_id": segundo["id"],
                "espacio_id": espacio["id"],
                "responsable_id": self.responsable["id"],
                "cuota_mensual": "500.00",
                "plan_actual": "A",
                "dia_pago": 5,
                "fecha_inicio": "2026-06-01",
            },
        )

        self.assertEqual(response.status_code, 409)

    def test_desactivar_contrato_libera_espacio_y_cuenta(self) -> None:
        espacio = self.crear_espacio()
        primero = self.crear_vehiculo("P-111AAA", "Primero")
        segundo = self.crear_vehiculo("P-222BBB", "Segundo")
        contrato = self.crear_contrato(espacio, primero)

        desactivado = self.client.patch(
            f"/api/contratos-parqueo/{contrato['id']}",
            json={"activo": False, "fecha_fin": "2026-06-30"},
        )
        self.assertEqual(desactivado.status_code, 200)
        self.assertFalse(desactivado.json()["activo"])

        nuevo = self.crear_contrato(espacio, segundo)
        self.assertTrue(nuevo["activo"])

        with self.Session() as database:
            cuenta_anterior = database.get(CuentaCobro, contrato["cuenta_cobro_id"])
            self.assertFalse(cuenta_anterior.activo)

    def test_rechaza_placa_duplicada_sin_importar_mayusculas(self) -> None:
        self.crear_vehiculo("p-123abc", "Primero")
        response = self.client.post(
            "/api/vehiculos",
            json={"placa": "P-123ABC", "tipo": "carro", "propietario": "Segundo"},
        )
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()

