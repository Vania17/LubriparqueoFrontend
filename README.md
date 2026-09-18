# Lubriparqueo Frontend

Interfaz web para el control administrativo de Lubriparqueo, un negocio de
parqueo y alquiler de espacios en Guatemala. Permite explorar ingresos, pagos,
inquilinos y ocupacion desde una misma interfaz, con montos en quetzales (Q).

Este repositorio contiene exclusivamente el frontend. El proyecto esta en etapa
de desarrollo y ajuste visual: utiliza datos de prueba y todavia no esta
conectado a un backend ni a una base de datos.

## Tecnologias

- React 19 y TypeScript para la interfaz.
- Vite 6 para desarrollo y compilacion.
- Recharts para las graficas.
- Lucide React para los iconos.
- CSS para los estilos y ESLint para revisar el codigo.

## Requisitos

- Node.js y npm instalados, con una version compatible con Vite 6.
- Git para clonar el repositorio.

Puedes comprobar las herramientas desde una terminal:

```powershell
node --version
npm --version
git --version
```

## Instalacion y ejecucion

Para descargar el proyecto en otra computadora:

```powershell
git clone https://github.com/Vania17/LubriparqueoFrontend.git
cd LubriparqueoFrontend
npm ci
npm run dev
```

Si ya tienes el proyecto en tu computadora, abre la terminal en la carpeta que
contiene `package.json` y ejecuta `npm run dev`. La carpeta local de trabajo
actual es:

```powershell
cd D:\VaniaLopez\Documents\parqueo-automatizacion\frontend
npm run dev
```

Abre la direccion que muestra Vite en la terminal, normalmente
`http://localhost:5173/`. Si el puerto esta ocupado, puede utilizar otro.
Manten la terminal abierta mientras uses la aplicacion. Para detenerla,
presiona `Ctrl+C`.

## Secciones disponibles

| Seccion | Contenido actual |
| --- | --- |
| Dashboard | Resumen de indicadores y graficas de ingresos con datos de prueba. |
| Inquilinos | Listados separados de Billy y Lino, selector de mes, resumen de pagos y acciones por inquilino. |
| Pagos | Formulario y vista previa del registro de pagos y abonos. |
| Parqueo | Resumen de espacios fijos y vehiculos temporales. |
| Reportes | Selector de mes y presentacion de un resumen ejecutivo. |

### Control de inquilinos

La tabla muestra fecha acordada, mes, fecha de pago, nombre, pago, saldo
pendiente, plan, mensualidad, alerta, estado y acciones.

- Crear y editar inquilinos mediante un modal.
- Ver detalle, incluida la observacion completa.
- Eliminar un registro con confirmacion.
- Mostrar notificaciones de resultado que desaparecen automaticamente.
- Diferenciar una alerta corta en la tabla de una observacion en el detalle.

Los planes se identifican como **A (anticipado)** y **V (vencido)**. Los estados
disponibles son **Al dia**, **Parcial** y **Moroso**.

## Limitaciones actuales

- El acceso, logout, expiracion y controles visuales por rol estan implementados.
  La integracion real depende de F01-AUTH en Fastify. Configuracion y contrato:
  [Acceso del frontend](docs/acceso_frontend.md). Para probar sin backend, usar
  `VITE_AUTH_MODE=demo` en `.env.local` y reiniciar Vite; solo disponible en desarrollo.

- Los cambios de inquilinos se guardan solo en memoria y se pierden al recargar
  la pagina o salir de esa seccion.
- El selector de mes cambia el contexto mostrado, pero todavia no administra
  registros independientes por mes: utiliza el mismo listado de prueba.
- Los estados se seleccionan manualmente; aun no se calcula la mora a partir
  del historial de obligaciones y pagos.
- Pagos, parqueo, reportes y graficas son vistas de demostracion; no deben
  utilizarse como registros contables reales.
- La proteccion real de datos y acciones debe validarse en API; los controles
  visuales del frontend no sustituyen la autorizacion del servidor.

## Comandos disponibles

Ejecuta los comandos desde la raiz de este repositorio:

| Comando | Funcion |
| --- | --- |
| `npm ci` | Instala las dependencias segun `package-lock.json`. |
| `npm run dev` | Inicia el servidor de desarrollo. |
| `npm run build` | Comprueba TypeScript y genera la version compilada en `dist/`. |
| `npm run preview` | Sirve localmente la version compilada, despues de ejecutar el build. |
| `npm run lint` | Revisa el codigo con ESLint. |

`npm run preview` sirve para revisar la compilacion local; no configura un
alojamiento de produccion.

## Estructura del proyecto

```text
src/
  components/   Componentes compartidos, tarjetas, graficas y navegacion
  layouts/      Estructura principal de la interfaz
  pages/        Dashboard, Inquilinos, Pagos, Parqueo y Reportes
  services/     Utilidades para la futura conexion con la API
  types/        Tipos compartidos
  App.tsx       Seleccion de la seccion activa
  main.tsx      Punto de entrada de React
  styles.css    Estilos de la aplicacion
index.html
package.json
package-lock.json
vite.config.ts
```

La navegacion actual cambia de seccion mediante estado de React; no utiliza
rutas de URL independientes.

## Futura conexion con la API

`src/services/api.ts` contiene un helper de solicitudes HTTP. Su direccion
predeterminada es `http://localhost:8000`, y puede configurarse mediante un
archivo `.env` en la raiz:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Actualmente las vistas no necesitan esa conexion para funcionar. Reinicia Vite
si cambias las variables de entorno. Las variables con prefijo `VITE_` son
visibles en el navegador: no guardes contrasenas ni tokens en ellas.

## Trabajo pendiente

- Terminar los ajustes visuales y revisar la interfaz en distintos tamanos de pantalla.
- Completar los flujos de pagos y parqueo.
- Implementar registros e historial por mes.
- Conectar la API para persistir los datos y calcular saldos y mora.
- Incorporar acceso y permisos para encargada, gerente y usuarios de consulta.
- Pulir las graficas del dashboard y los reportes con datos reales.

## Control de versiones

La rama de trabajo es `main`. Para revisar y subir cambios desde este
repositorio:

```powershell
git status
git add README.md
git commit -m "Actualizar documentacion"
git push
```

Selecciona en `git add` los archivos que quieras incluir en cada commit.
`node_modules/`, `dist/` y los archivos `.env` estan excluidos mediante
`.gitignore`.
