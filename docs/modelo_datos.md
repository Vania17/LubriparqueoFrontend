# Modelo de datos - Lubriparqueo

Este documento propone el modelo inicial para la aplicacion. No representa todavia tablas implementadas ni migraciones de base de datos.

## Principios

- Billy y Lino se mantienen separados como responsables.
- Cada inquilino pertenece a un responsable.
- Una cuota mensual genera una obligacion independiente.
- Una obligacion puede recibir uno o varios pagos o abonos.
- Los montos se guardan como valores decimales, nunca como texto.
- Las fechas se guardan completas, incluyendo el anio.
- La mora se calcula usando la fecha limite, los pagos acumulados y la fecha actual.
- Los registros financieros no se eliminan fisicamente; se anulan o desactivan para conservar historial.

## Relaciones principales

```text
Responsable 1 ---- N Inquilinos
Inquilino   1 ---- 1 Cuenta de cobro
Contrato    1 ---- 1 Cuenta de cobro
Cuenta      1 ---- N Obligaciones mensuales
Cuenta      1 ---- N Pagos
Pago        1 ---- N Aplicaciones de pago
Obligacion  1 ---- N Aplicaciones de pago
Usuario     1 ---- N Pagos registrados
Espacio     1 ---- N Ocupaciones temporales
Vehiculo    1 ---- N Contratos mensuales
Vehiculo    1 ---- N Ocupaciones temporales
Contrato    1 ---- N Liberaciones temporales
```

## 1. Usuarios

Representa a las personas que pueden iniciar sesion en la aplicacion.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| nombre | Texto | Nombre completo |
| correo | Texto unico | Correo para iniciar sesion |
| contrasena_hash | Texto | Contrasena protegida, nunca texto plano |
| rol | Opcion | Gerente, encargada o consulta |
| responsable_id | Relacion opcional | Limita un usuario de consulta a Billy o Lino |
| activo | Booleano | Permite o bloquea el acceso |
| creado_en | Fecha y hora | Fecha de creacion |
| actualizado_en | Fecha y hora | Ultima modificacion |

### Roles iniciales

| Rol | Alcance previsto |
|---|---|
| gerente | Consulta y modifica toda la informacion |
| encargada | Gestiona inquilinos, pagos y buses |
| consulta | Solo observa la informacion autorizada |

Los permisos exactos se definiran cuando se implemente autenticacion.

## 2. Responsables

Permite separar los grupos administrados por Billy y Lino sin depender del nombre escrito manualmente.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| nombre | Texto unico | Billy o Lino |
| activo | Booleano | Indica si sigue operando |
| creado_en | Fecha y hora | Fecha de creacion |

Datos iniciales:

```text
Billy
Lino
```

## Cuenta de cobro

Unifica el control financiero de inquilinos y vehiculos con contrato mensual.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| tipo | Opcion | Inquilino o parqueo mensual |
| activo | Booleano | Permite o detiene nuevos cobros |
| creado_en | Fecha y hora | Fecha de creacion |

Cada inquilino y cada contrato de parqueo mensual tiene una cuenta de cobro. Las obligaciones, pagos, abonos y saldos a favor pertenecen a esta cuenta.

## 3. Inquilinos

Contiene la informacion permanente de cada inquilino.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| cuenta_cobro_id | Relacion unica | Cuenta usada para obligaciones y pagos |
| responsable_id | Relacion | Billy o Lino |
| nombre | Texto | Nombre del inquilino |
| telefono | Texto opcional | Contacto para cobros |
| plan_actual | Opcion | A anticipado o V vencido, definido por la encargada |
| dia_pago_actual | Entero | Dia base de pago definido por la encargada, entre 1 y 31 |
| cuota_actual | Decimal | Cuota mensual vigente en Quetzales |
| referencia_carta_legacy | Texto opcional | Valor historico trasladado desde `Segun carta` |
| observaciones | Texto opcional | Informacion administrativa |
| activo | Booleano | Permite conservar inquilinos anteriores |
| creado_en | Fecha y hora | Fecha de creacion |
| actualizado_en | Fecha y hora | Ultima modificacion |

La cuota, el plan y el dia de pago actuales sirven para crear nuevas obligaciones. Las obligaciones anteriores conservan los valores historicos correspondientes.

La encargada define una vez si el inquilino trabaja con mes anticipado o vencido y establece su dia de pago. Esta configuracion se mantiene como regla habitual del inquilino, pero la encargada puede modificarla cuando sea necesario.

Los cambios de plan o dia de pago se aplican a las obligaciones futuras. No deben modificar el plan, dia ni fecha limite guardados en obligaciones anteriores.

## 4. Obligaciones mensuales

Representa lo que un inquilino debe pagar por un periodo especifico.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| cuenta_cobro_id | Relacion | Cuenta del inquilino o contrato mensual |
| periodo | Mes y anio | Periodo cobrado, por ejemplo 2026-05 |
| plan_aplicado | Opcion | Copia historica del plan A o V |
| dia_pago_aplicado | Entero | Copia historica del dia de pago |
| monto_cuota | Decimal | Cuota que correspondia a ese periodo |
| fecha_limite | Fecha | Fecha limite calculada al crear la obligacion |
| anulada | Booleano | Indica si la obligacion fue anulada |
| motivo_anulacion | Texto opcional | Explicacion de la anulacion |
| creado_en | Fecha y hora | Fecha de creacion |

Debe existir como maximo una obligacion activa por cuenta de cobro y periodo. El plan y la fecha limite se guardan en cada obligacion para que un cambio posterior realizado por la encargada no altere deudas anteriores.

### Calculo de fecha limite

Plan `A` anticipado:

```text
dia_pago 15 + periodo mayo 2026 = 15 de mayo de 2026
```

Plan `V` vencido:

```text
dia_pago 15 + periodo mayo 2026 = 14 de junio de 2026
```

El dia configurado se conserva siempre que exista en el mes correspondiente. Solo cuando el mes no tenga ese dia, se usa su ultimo dia valido.

Ejemplos:

```text
Dia configurado 31 en abril = 30 de abril
Dia configurado 30 en febrero de 2026 = 28 de febrero
Dia configurado 29 en febrero de un anio bisiesto = 29 de febrero
```

## 5. Pagos y abonos

Cada fila representa el dinero total recibido en una operacion. Un pago puede cubrir uno o varios meses pendientes.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| cuenta_cobro_id | Relacion | Cuenta que realizo el pago |
| monto_total | Decimal | Cantidad total recibida en Quetzales |
| fecha_pago | Fecha | Dia en que se recibio el dinero |
| observaciones | Texto opcional | Nota del movimiento |
| registrado_por | Relacion | Usuario que ingreso el pago |
| anulado | Booleano | Permite corregir sin borrar historial |
| motivo_anulacion | Texto opcional | Explicacion de la anulacion |
| creado_en | Fecha y hora | Fecha de registro |

## 6. Aplicaciones de pago

Indica cuanto dinero de un pago se asigna a cada obligacion mensual.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| pago_id | Relacion | Pago total recibido |
| obligacion_id | Relacion | Mes o periodo al que se aplica |
| monto_aplicado | Decimal | Parte del pago asignada a esa obligacion |
| creado_en | Fecha y hora | Fecha de registro |

Ejemplo:

```text
Pago total: Q2,000
Aplicacion 1: Q1,000 a abril
Aplicacion 2: Q1,000 a mayo
```

### Regla de distribucion

- El sistema propone aplicar primero el dinero a la obligacion pendiente mas antigua.
- La encargada puede cambiar la distribucion antes de guardar el pago.
- Una obligacion puede recibir varios abonos.
- Un pago puede aplicarse a varias obligaciones.
- La suma de las aplicaciones no puede superar el monto total del pago.
- Si queda dinero sin aplicar, se conserva como saldo a favor del inquilino.
- Cuando se genere una nueva obligacion, el sistema propone aplicar primero el saldo a favor disponible.
- La encargada confirma o modifica la aplicacion del saldo a favor antes de guardarla.

### Valores calculados

Estos valores no necesitan guardarse como columnas permanentes:

```text
total_pagado = suma de aplicaciones asociadas a pagos no anulados
saldo = monto_cuota - total_pagado
saldo_a_favor_del_pago = monto_total - suma de aplicaciones del pago
saldo_a_favor_de_la_cuenta = suma del saldo no aplicado de sus pagos
```

El saldo a favor no se registra como un pago nuevo cuando se utiliza. Se crea una nueva aplicacion desde el pago original hacia la obligacion siguiente, conservando asi el origen del dinero.

Estado calculado:

| Condicion | Estado |
|---|---|
| saldo <= 0 | completo |
| saldo > 0, existe pago y no vencio | parcial |
| saldo > 0, no existe pago y no vencio | pendiente |
| saldo > 0 y ya paso fecha_limite | moroso |

## 7. Espacios de parqueo

Representa cada espacio que puede estar libre, reservado u ocupado.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| codigo | Texto unico | Nombre o numero visible del espacio |
| tipo_vehiculo | Opcion | Carro, bus, camion u otro |
| activo | Booleano | Indica si el espacio esta disponible para operar |
| observaciones | Texto opcional | Restricciones o informacion del espacio |
| creado_en | Fecha y hora | Fecha de creacion |

Los espacios fuera de servicio no forman parte de la capacidad disponible del dia.

## 8. Vehiculos

Permite identificar vehiculos fijos y temporales.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| placa | Texto opcional | Placa o identificacion del vehiculo |
| tipo | Opcion | Carro, bus, camion u otro |
| propietario | Texto opcional | Nombre del cliente o propietario |
| telefono | Texto opcional | Contacto del propietario |
| observaciones | Texto opcional | Informacion adicional |
| creado_en | Fecha y hora | Fecha de creacion |

La placa puede ser opcional para casos extraordinarios, pero debe registrarse siempre que este disponible.

## 9. Contratos de parqueo mensual

Representa los vehiculos fijos que tienen un espacio asignado y pagan mensualmente.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| cuenta_cobro_id | Relacion unica | Cuenta usada para obligaciones y pagos |
| vehiculo_id | Relacion | Vehiculo fijo |
| espacio_id | Relacion | Espacio reservado |
| responsable_id | Relacion | Responsable del cobro |
| cuota_mensual | Decimal | Cuota vigente en Quetzales |
| fecha_inicio | Fecha | Inicio del contrato |
| fecha_fin | Fecha opcional | Fin del contrato |
| activo | Booleano | Indica si el espacio sigue reservado |
| observaciones | Texto opcional | Condiciones particulares |
| creado_en | Fecha y hora | Fecha de creacion |

Un contrato mensual activo reserva su espacio y cuenta como ocupado durante su vigencia.

Los contratos mensuales usan las mismas reglas financieras que los inquilinos:

- Plan `A` anticipado o `V` vencido.
- Dia de pago definido por la encargada.
- Obligaciones mensuales.
- Pagos completos y abonos.
- Pagos aplicados a varios meses.
- Mora y saldo pendiente.
- Saldo a favor reutilizable.

## 10. Liberaciones temporales de espacios reservados

Cuando el vehiculo mensual no esta presente, la encargada puede habilitar temporalmente su espacio para otro vehiculo.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| contrato_mensual_id | Relacion | Contrato que conserva la reserva |
| disponible_desde | Fecha y hora | Inicio de la disponibilidad temporal |
| disponible_hasta | Fecha y hora | Fin previsto de la disponibilidad |
| registrado_por | Relacion | Usuario que autorizo el uso |
| observaciones | Texto opcional | Motivo o detalle |
| creado_en | Fecha y hora | Fecha de registro |

La reserva mensual no se cancela. Esta liberacion solo permite usar fisicamente el espacio durante el periodo autorizado.

## 11. Ocupaciones temporales

Registra individualmente camiones, buses, carros u otros vehiculos que permanecen por tiempo limitado.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| vehiculo_id | Relacion | Vehiculo registrado |
| espacio_id | Relacion | Espacio utilizado |
| liberacion_temporal_id | Relacion opcional | Autorizacion si usa un espacio mensual reservado |
| fecha_hora_entrada | Fecha y hora | Inicio de la estadia |
| fecha_hora_salida | Fecha y hora opcional | Fin de la estadia |
| tipo_tarifa | Opcion | Por hora, diaria o acordada por encargado |
| tarifa | Decimal | Tarifa aplicada en Quetzales |
| monto_cobrado | Decimal | Total efectivamente cobrado |
| responsable_id | Relacion | Encargado que atendio el ingreso |
| registrado_por | Relacion | Usuario que registro la operacion |
| observaciones | Texto opcional | Justificacion o detalle especial |
| anulado | Booleano | Permite corregir sin borrar historial |
| creado_en | Fecha y hora | Fecha de registro |
| actualizado_en | Fecha y hora | Ultima modificacion |

Tipos de tarifa:

- `por_hora`: calcula el cobro segun el tiempo utilizado.
- `diaria`: usa la tarifa diaria establecida.
- `acordada`: el encargado define el monto para un caso especial.

El ingreso diario se calcula sumando los cobros individuales. No se registra un segundo total manual que pueda duplicar el dinero.

## 12. Cierre diario de ocupacion

Conserva la capacidad y ocupacion del parqueo al momento del cierre diario.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| fecha | Fecha unica | Dia del cierre |
| espacios_totales | Entero | Espacios activos ese dia |
| espacios_ocupados | Entero | Espacios reservados u ocupados |
| espacios_libres | Entero calculado | Total menos ocupados |
| diferencia | Entero calculado | Espacios libres menos ocupados |
| porcentaje_ocupacion | Decimal calculado | Porcentaje ocupado |
| ingresos_vehiculos_00_06 | Entero calculado | Vehiculos ingresados entre 12:00 a. m. y 6:00 a. m. |
| monto_recaudado_00_06 | Decimal calculado | Cobros registrados en ese periodo |
| creado_en | Fecha y hora | Momento del cierre |

Formulas:

```text
espacios_libres = espacios_totales - espacios_ocupados
diferencia = espacios_libres - espacios_ocupados
porcentaje_ocupacion = espacios_ocupados / espacios_totales * 100
```

La ocupacion incluye:

- Espacios reservados por contratos mensuales activos.
- Espacios con una ocupacion temporal abierta al momento del cierre.

Un espacio mensual reservado cuenta una sola vez como ocupado. Si el vehiculo fijo esta ausente y un temporal usa el espacio con autorizacion, ese uso no aumenta la cantidad total de espacios ocupados.

### Horarios de control

```text
6:00 a. m. = conteo preliminar de vehiculos ingresados y cobros desde las 12:00 a. m.
3:00 p. m. = cierre final de espacios ocupados, libres y porcentaje de ocupacion
```

El cierre diario se genera a las 3:00 p. m.

## Comparacion por dia de la semana

Los reportes mensuales comparan cada dia con los dias equivalentes del mismo mes:

```text
lunes contra los otros lunes
martes contra los otros martes
...
domingo contra los otros domingos
```

Para cada grupo se muestran:

- Espacios ocupados.
- Espacios libres.
- Diferencia entre libres y ocupados.
- Porcentaje de ocupacion.
- Cambio de espacios ocupados contra el mismo dia de la semana anterior.
- Cambio del porcentaje de ocupacion contra el mismo dia de la semana anterior.

## 13. Auditoria

Para saber quien modifico informacion importante, se preve un historial de cambios.

| Campo | Tipo conceptual | Descripcion |
|---|---|---|
| id | Identificador | Identificador interno |
| usuario_id | Relacion | Usuario que realizo la accion |
| entidad | Texto | Tipo de registro afectado |
| entidad_id | Identificador | Registro afectado |
| accion | Opcion | Crear, actualizar, anular o reactivar |
| datos_anteriores | JSON opcional | Valores antes del cambio |
| datos_nuevos | JSON opcional | Valores despues del cambio |
| creado_en | Fecha y hora | Momento de la accion |

La auditoria puede implementarse despues del flujo principal, pero el modelo debe permitir agregarla.

## Indices y restricciones previstos

- El correo de usuario debe ser unico.
- El nombre de responsable debe ser unico.
- Los nombres de inquilinos pueden repetirse; cada registro se identifica por su ID interno.
- Un inquilino debe pertenecer a un responsable.
- No puede repetirse una obligacion activa para la misma cuenta de cobro y periodo.
- Los montos de cuotas, pagos, tarifas y cobros no pueden ser negativos.
- El monto aplicado a una obligacion debe ser mayor que cero.
- La suma aplicada no puede superar el monto total del pago.
- Un saldo a favor solo puede aplicarse a obligaciones de la misma cuenta de cobro.
- El dia de pago debe estar entre 1 y 31.
- Un espacio no puede tener dos ocupaciones temporales abiertas al mismo tiempo.
- Un espacio reservado por contrato solo puede asignarse temporalmente a otro vehiculo si existe una liberacion autorizada vigente.
- Los espacios ocupados no pueden superar los espacios totales.
- El porcentaje de ocupacion debe estar entre 0 y 100.
- Un usuario de consulta asociado a Billy no debe consultar datos privados de Lino, y viceversa.

## Criterios iniciales confirmados

- Los nombres de inquilinos pueden repetirse.
- El campo historico `Segun carta` se conserva como referencia y no determina automaticamente la deuda.
- El telefono es opcional.
- Este modelo es una base inicial y puede evolucionar durante la implementacion.
