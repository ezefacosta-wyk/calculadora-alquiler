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

## Proyección

Para los ajustes que todavía no tienen datos publicados, la página puede estimarlos con:

- **REM del BCRA** (por defecto): mediana de la inflación esperada para los próximos 12 meses (variable 29), convertida a tasa mensual. Si no está disponible, se usa la tendencia.
- **Tendencia de 3 meses:** el ritmo promedio del propio índice (ICL o IPC) en los últimos 3 meses.
- **Tasa mensual propia:** el porcentaje que cargue el usuario.

Las filas proyectadas aparecen en cursiva con la etiqueta *Proyectado* y la cantidad de meses estimados.

## Exportar

- **Excel (.xlsx):** una hoja con los parámetros del contrato, la tabla de ajustes y un gráfico de columnas nativo de Excel (las columnas claras son ajustes proyectados). Cada alquiler es una fórmula (`alquiler anterior × (1 + variación)`) que parte de la celda del alquiler inicial: si la cambiás, se recalcula toda la tabla y el gráfico. Se imprime en una página apaisada.
- **CSV:** los mismos datos de la tabla, separados por `;` y con coma decimal, para que Excel en español los abra directamente en columnas.

El archivo se arma en el navegador, sin librerías externas.

## Uso

1. Elegí el índice (ICL o IPC).
2. Cargá el alquiler inicial, la fecha de inicio, la frecuencia de ajuste y la duración.
3. Para IPC, elegí si el contrato usa los meses del período o un desfase de 1 o 2 meses.

La página muestra el alquiler vigente, el próximo ajuste y el detalle de cada período.

## Cálculo

- **ICL:** valor del índice el día del ajuste ÷ valor el día de inicio del período.
- **IPC:** índice del último mes del período ÷ índice del mes anterior al primero.

El resultado es orientativo; lo que vale es lo pactado en el contrato.
