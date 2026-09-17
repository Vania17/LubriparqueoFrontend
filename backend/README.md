# Backend

API de Lubriparqueo construida con FastAPI.

## Estado actual

- Aplicacion FastAPI inicial.
- Configuracion mediante variables de entorno.
- CORS preparado para Vite en `http://localhost:5173`.
- Endpoint de salud `GET /health`.
- SQLAlchemy y Alembic preparados.
- SQLite configurado para desarrollo.
- Sin tablas ni reglas del negocio implementadas todavia.

## Ejecucion futura

Cuando las dependencias esten instaladas:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

La API estara disponible en:

```text
http://localhost:8000
```

La documentacion interactiva estara en:

```text
http://localhost:8000/docs
```

## Migraciones

Crear una migracion despues de agregar modelos:

```powershell
alembic revision --autogenerate -m "descripcion"
```

Aplicar migraciones:

```powershell
alembic upgrade head
```
