# Calculadora de ajuste de alquiler (ICL / IPC)

Página web estática que calcula los ajustes de un contrato de alquiler en Argentina según el índice pactado:

- **ICL** (Índice para Contratos de Locación): API oficial del BCRA, variable 40.
- **IPC** (nivel general nacional, INDEC): API de series de datos.gob.ar.

Los datos se consultan en vivo desde el navegador cada vez que se abre la página. No necesita backend ni claves.

## Fuentes de respaldo

Si una fuente no responde (después de 3 intentos), la página pasa a la siguiente:

| Índice | Orden de fuentes |
|---|---|
| ICL | API del BCRA → copia diaria (`data/icl.json`) |
| IPC | datos.gob.ar (INDEC) → BCRA variable 27 → ArgentinaDatos → copia diaria (`data/ipc.json`) |

La copia diaria la genera `scripts/actualizar_datos.py`, que corre con GitHub Actions dos veces por día (workflow *Actualizar copia de ICL e IPC*). Si en una corrida fallan todas las fuentes, se conserva la copia anterior. También se puede correr a mano desde la pestaña *Actions*.

## Uso

1. Elegí el índice (ICL o IPC).
2. Cargá el alquiler inicial, la fecha de inicio, la frecuencia de ajuste y la duración.
3. Para IPC, elegí si el contrato usa los meses del período o un desfase de 1 o 2 meses.

La página muestra el alquiler vigente, el próximo ajuste y el detalle de cada período.

## Cálculo

- **ICL:** valor del índice el día del ajuste ÷ valor el día de inicio del período.
- **IPC:** índice del último mes del período ÷ índice del mes anterior al primero.

El resultado es orientativo; lo que vale es lo pactado en el contrato.
