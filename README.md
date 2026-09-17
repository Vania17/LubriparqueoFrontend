# Lubriparqueo

Aplicacion web para administrar inquilinos, pagos, morosidad e ingresos diarios de buses.

## Arquitectura

```text
frontend/  React + Vite
backend/   FastAPI
database/  PostgreSQL (pendiente de diseno)
docs/      Reglas del negocio
```

Google Sheets y n8n ya no forman parte de la arquitectura nueva.

## Estado actual

El proyecto esta reorganizado en frontend y backend. Todavia no se han implementado pantallas, API, autenticacion ni base de datos.

## Roles previstos

- Gerente: acceso completo.
- Encargada: crear y modificar datos operativos.
- Billy/Lino: acceso de consulta limitado a la informacion autorizada.

## Siguiente etapa

1. Definir las primeras pantallas.
2. Disenar las entidades de la base de datos.
3. Crear el backend FastAPI.
4. Crear el frontend React con Vite.
5. Implementar autenticacion y permisos despues del flujo principal.

