# Contexto de Lubriparqueo

Lubriparqueo es un negocio de parqueo y alquiler de espacios en Guatemala.

El asistente debe ayudar al dueno a entender como va el negocio de forma clara, sencilla y practica, sin tecnicismos financieros.

## Fuentes de ingreso

1. Inquilinos administrados por Billy.
2. Inquilinos administrados por Lino.
3. Ingresos por buses.

## Gastos principales

1. Electricidad EEGSA.
2. Otros gastos pendientes de documentar.

## Inquilinos

Billy y Lino se manejan por separado.

Cada encargado tiene su propio Google Sheet:

```text
BillyInquilinos
LinoInquilinos
```

Cada archivo usa pestanas por mes, por ejemplo:

```text
May2026
Jun2026
Jul2026
```

## Columnas de inquilinos

Las pestanas mensuales de Billy y Lino usan estas columnas:

```text
No. | FECHA AL | MES | FECHA DE PAGO | INQUILINO | PAGO O ABONO | RESTA | Plan | Segun carta | Mes Q. | Alerta | Cuaderno
```

## Significado de columnas clave

- `FECHA AL`: dia en que le toca pagar al inquilino.
- `MES`: mes relacionado con la fecha de pago.
- `FECHA DE PAGO`: dia y mes en que realmente pago.
- `INQUILINO`: nombre de la persona.
- `PAGO O ABONO`: cantidad pagada.
- `RESTA`: cantidad que aun debe.
- `Plan`: tipo de plan del inquilino.
- `Segun carta`: meses pendientes segun el cartapacio fisico.
- `Mes Q.`: cuota mensual que debe pagar.

## Planes de pago

Plan `A` significa anticipado.

- El inquilino debe pagar antes o el mismo dia indicado por `FECHA AL` + `MES`.
- Ejemplo: `15 may` vence el `15 may`.

Plan `V` significa vencido.

- El inquilino paga despues de usar el mes o periodo.
- La fecha limite real es el dia anterior del mismo dia del mes siguiente.
- Ejemplo: `15 may` vence el `14 jun`.

## Regla de mora

Un inquilino esta moroso cuando:

```text
RESTA tiene monto pendiente
y
ya paso la fecha limite real segun su plan
```

## Indicadores importantes

- Total cobrado por Billy.
- Total pendiente por cobrar de Billy.
- Morosos de Billy.
- Total cobrado por Lino.
- Total pendiente por cobrar de Lino.
- Morosos de Lino.
- Total de ingresos por buses.
- Total general del negocio.
- Gastos registrados.
- Resultado neto estimado.

