# F01-WEB - Acceso y estados globales

Estado: frontend implementado con contrato provisional. F01-AUTH en Fastify
debe implementar y validar la autorizacion real; esta tarea no esta cerrada
como integracion de produccion.

## Configuracion

El modo predeterminado es API. Configurar `.env.local` en la raiz del frontend:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_MODE=api
```

Para probar perfiles sin backend, usar `VITE_AUTH_MODE=demo` y reiniciar
`npm run dev`. El acceso ofrece Gerencia, Administracion, Billy, Lino y Consulta.
El modo demo solo funciona en desarrollo y no valida credenciales. La sesion
de prueba dura 15 minutos y se guarda en sessionStorage; no guarda tokens reales.
La compilacion de produccion siempre usa API.

## Contrato propuesto para F01-AUTH

- `POST /auth/login`: recibe `{ email, password }`; 401 por credenciales invalidas.
- `GET /auth/me`: devuelve sesion vigente; 401 si no hay sesion.
- `POST /auth/logout`: invalida sesion en servidor y cookie; devuelve 204.
- Login y me devuelven `{ user, expiresAt }`.

```json
{
  "user": {
    "id": "uuid-del-usuario",
    "name": "Billy",
    "role": "encargado",
    "responsable": "Billy",
    "sections": ["inquilinos", "pagos", "parqueo"]
  },
  "expiresAt": "2026-09-18T23:00:00Z"
}
```

Roles: gerente, encargada, encargado, consulta. Responsable: Billy, Lino o null.
El servidor determina permisos y alcance; no recibe el rol del formulario.
Cookie de sesion HttpOnly, Secure en HTTPS, SameSite apropiado. Fastify puede
usar Supabase Auth internamente, pero la cookie y este contrato deben acordarse
con el responsable de F01-AUTH. CORS permite origen concreto con credenciales;
validar Origin/CSRF en operaciones mutantes. Las peticiones usan credentials
include; ninguna clave Supabase privilegiada va al frontend.

## Comportamiento

- Restauracion de sesion con estado de carga, error recuperable y reintento.
- Validacion de estructura de respuesta; fallo cerrado ante sesion invalida.
- Expiracion local, comprobacion al recuperar foco y 401 de API protegida.
- Logout espera confirmacion; si falla, muestra error y mantiene sesion.
- Navegacion limitada a sections. Sin secciones muestra estado vacio.
- Consulta oculta escritura. Billy/Lino solo muestran su grupo en inquilinos
  y pagos; vistas consolidadas sin filtro muestran estado vacio para ese alcance.
- Se conservan datos de prototipo de los modulos: conectar sus APIs corresponde
  a tareas posteriores. No confundir estas restricciones visuales con seguridad.

## Verificacion

`npm run build`, `npm run lint` y `npm run test:e2e`.
Instalar navegador de pruebas una vez con `npx playwright install chromium`.
Las pruebas usan respuestas API simuladas: no prueban autenticacion de Fastify,
RLS, cookies reales ni revocacion de sesiones en servidor.
Screenshots de acceso desktop/mobile quedan en test-results, excluido de Git.

Verificacion local realizada: build y lint correctos; 9 pruebas de navegador
pasaron con API simulada. Login capturado a 1440x900 y 390x844 sin overflow
horizontal. `npm run dev:review` abre puerto fijo 5176 para revision local.

Para cerrar F01-WEB: probar con F01-AUTH real login/logout/expiracion y rechazo
de escritura/lectura no autorizadas en servidor, incluso llamando API directamente.
