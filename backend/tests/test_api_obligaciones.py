import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


class ObligacionesApiTests(unittest.TestCase):
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

    def crear_inquilino(self, responsable: str, nombre: str, plan: str, dia: int) -> dict:
        responsable_response = self.client.post("/api/responsables", json={"nombre": responsable})
        self.assertEqual(responsable_response.status_code, 201)
        responsable_id = responsable_response.json()["id"]

        inquilino_response = self.client.post(
            "/api/inquilinos",
            json={
                "responsable_id": responsable_id,
                "nombre": nombre,
                "plan_actual": plan,
                "dia_pago_actual": dia,
                "cuota_actual": "1000.00",
            },
        )
        self.assertEqual(inquilino_response.status_code, 201)
        return {"responsable_id": responsable_id, "inquilino": inquilino_response.json()}

    def test_genera_obligaciones_con_fechas_historicas(self) -> None:
        self.crear_inquilino("Billy", "Anticipado", "A", 15)
        self.crear_inquilino("Lino", "Vencido", "V", 15)

        response = self.client.post(
            "/api/obligaciones/generar",
            json={"periodo": "2026-05-01"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["creadas"], 2)

        listado = self.client.get(
            "/api/obligaciones?periodo=2026-05-01&fecha_corte=2026-05-10"
        ).json()
        fechas = {item["inquilino"]: item["fecha_limite"] for item in listado}
        self.assertEqual(fechas["Anticipado"], "2026-05-15")
        self.assertEqual(fechas["Vencido"], "2026-06-14")

    def test_repetir_generacion_omite_duplicados(self) -> None:
        self.crear_inquilino("Billy", "Baltazar", "A", 5)
        payload = {"periodo": "2026-05-01"}

        primera = self.client.post("/api/obligaciones/generar", json=payload)
        segunda = self.client.post("/api/obligaciones/generar", json=payload)

        self.assertEqual(primera.json(), {"periodo": "2026-05-01", "creadas": 1, "omitidas": 0})
        self.assertEqual(segunda.json(), {"periodo": "2026-05-01", "creadas": 0, "omitidas": 1})

    def test_filtra_por_responsable_y_estado(self) -> None:
        billy = self.crear_inquilino("Billy", "Baltazar", "A", 15)
        self.crear_inquilino("Lino", "Edgar", "V", 15)
        self.client.post("/api/obligaciones/generar", json={"periodo": "2026-05-01"})

        response = self.client.get(
            "/api/obligaciones",
            params={
                "periodo": "2026-05-01",
                "responsable_id": billy["responsable_id"],
                "estado": "pendiente",
                "fecha_corte": "2026-05-10",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["inquilino"] for item in response.json()], ["Baltazar"])

    def test_rechaza_periodo_que_no_inicia_el_primer_dia(self) -> None:
        response = self.client.post(
            "/api/obligaciones/generar",
            json={"periodo": "2026-05-15"},
        )
        self.assertEqual(response.status_code, 422)

    def test_genera_obligacion_para_contrato_mensual_activo(self) -> None:
        responsable = self.client.post("/api/responsables", json={"nombre": "Billy"}).json()
        espacio = self.client.post(
            "/api/espacios",
            json={"codigo": "A-01", "tipo_vehiculo": "carro"},
        ).json()
        vehiculo = self.client.post(
            "/api/vehiculos",
            json={"placa": "P-123ABC", "tipo": "carro", "propietario": "Cliente fijo"},
        ).json()
        contrato = self.client.post(
            "/api/contratos-parqueo",
            json={
                "vehiculo_id": vehiculo["id"],
                "espacio_id": espacio["id"],
                "responsable_id": responsable["id"],
                "cuota_mensual": "600.00",
                "plan_actual": "V",
                "dia_pago": 15,
                "fecha_inicio": "2026-05-01",
            },
        ).json()

        generado = self.client.post(
            "/api/obligaciones/generar",
            json={"periodo": "2026-05-01"},
        )
        self.assertEqual(generado.status_code, 201)
        self.assertEqual(generado.json()["creadas"], 1)

        listado = self.client.get(
            "/api/obligaciones",
            params={"periodo": "2026-05-01", "fecha_corte": "2026-05-10"},
        ).json()
        self.assertEqual(len(listado), 1)
        self.assertEqual(listado[0]["tipo_cuenta"], "parqueo_mensual")
        self.assertEqual(listado[0]["contrato_parqueo_id"], contrato["id"])
        self.assertEqual(listado[0]["vehiculo_placa"], "P-123ABC")
        self.assertEqual(listado[0]["titular"], "Cliente fijo")
        self.assertEqual(listado[0]["fecha_limite"], "2026-06-14")


if __name__ == "__main__":
    unittest.main()
