# Reglas de negocio - Lubriparqueo

Este documento conserva las reglas confirmadas del control de inquilinos y buses. La nueva aplicacion guardara esta informacion en una base de datos propia.

## Responsables

Los inquilinos administrados por Billy y Lino se manejan por separado. Los reportes pueden consolidar ambos grupos, pero siempre deben mostrar el responsable.

## Datos de inquilinos

Cada inquilino necesita, como minimo:

- Nombre.
- Responsable: Billy o Lino.
- Dia de pago.
- Mes o periodo correspondiente.
- Tipo de plan.
- Cuota mensual en Quetzales.
- Pago o abono realizado.
- Saldo pendiente.
- Fecha real de pago.
- Meses pendientes segun el registro fisico.
- Observaciones y alertas.

## Planes de pago

### Plan A - Anticipado

El inquilino debe pagar antes o el mismo dia establecido para el mes correspondiente.

Ejemplo:

```text
Dia de pago: 15
Mes: mayo
Fecha limite: 15 de mayo
```

Si llega el 16 de mayo y no pago completo, esta moroso.

### Plan V - Vencido

El inquilino paga despues de usar el mes o periodo. La fecha limite es el dia anterior al mismo dia del mes siguiente.

Ejemplo:

```text
Dia de pago: 15
Mes: mayo
Fecha limite: 14 de junio
```

Si llega el 15 de junio y no pago completo, esta moroso.

## Estados de pago

- Completo: el pago cubre la cuota y no queda saldo.
- Parcial: existe un abono, pero todavia queda saldo.
- Pendiente: falta pago, pero la fecha limite aun no ha pasado.
- Moroso: queda saldo y la fecha limite ya paso.

## Buses

Cada registro diario de buses necesita:

- Fecha.
- Dia de la semana.
- Encargado.
- Monto total diario.
- Observaciones opcionales.

## Indicadores iniciales

- Total cobrado por Billy.
- Total pendiente y morosos de Billy.
- Total cobrado por Lino.
- Total pendiente y morosos de Lino.
- Total mensual de buses.
- Total de buses por encargado.
- Promedio diario de buses.
- Dia con mayor y menor ingreso de buses.
- Total general del negocio.

