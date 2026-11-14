# Resultados de Gold

Generado por `python3 pset-02/scripts/resumir_gold.py`; las cifras proceden de informes agregados.

Build: 2026-11-13T15:02:31.785947+00:00; exportación: 2026-11-13T15:02:42.198945+00:00 (UTC).

**168 tests aprobados, cero fallos**: 67 de Gold y 101 de Bronze/Silver. Se construyeron diez tablas Gold y se validaron/reconstruyeron las capas anteriores. Tiempo dbt: 96.33 s, sin arranque ni exportación.

| Tabla Gold | Filas | Grano |
|---|---:|---|
| DIM_STUDENT | 28.785 | Persona |
| DIM_EDITION | 22 | Módulo–edición |
| DIM_RESOURCE | 6.364 | Recurso por módulo–edición |
| DIM_ENROLLMENT | 32.593 | Matrícula |
| DIM_RELATIVE_DAY | 295 | Día relativo |
| FACT_ENROLLMENT | 32.593 | Matrícula |
| FACT_ACTIVITY_DAILY | 8.459.320 | Matrícula–recurso–día |
| ENROLLMENT_WITHDRAWAL | 32.593 | Matrícula |
| OUTCOME_ENROLLMENT | 32.593 | Matrícula |
| DQ_GOLD_PROFILE | 26 | Dataset–métrica |

La actividad representa 10.655.280 filas originales y conserva **39.605.099 clics**. El join con las cinco dimensiones devuelve 8.459.320 filas y los mismos 39.605.099 clics. Los tests comprobaron conservación también por edición y claves completas.

FACT_ENROLLMENT conserva 32.593 matrículas, incluidas **3.365 sin actividad**. DIM_STUDENT contiene 28.785 personas, sin mezclar sus atributos entre matrículas. Los antecedentes variables se mantienen en DIM_ENROLLMENT.

DIM_RELATIVE_DAY contiene 295 días continuos, de -25 a 269, y los 4 cortes de observación. No es un calendario real ni evidencia de cobertura de logs.

## Población de referencia para la futura OBT

Registro conocido <= 0 y sin retiro registrado <= corte. El cálculo no consulta etiquetas y se contrastó con la auditoría independiente del PSet 1.

| Corte | Elegibles Gold | PSet 1 | Coinciden |
|---|---:|---:|---|
| 14 | 27.881 | 27.881 | Sí |
| 28 | 27.307 | 27.307 | Sí |
| 42 | 26.795 | 26.795 | Sí |
| 56 | 26.294 | 26.294 | Sí |

Estos conteos son referencias agregadas. La OBT matrícula–corte se implementó después con Spark y pruebas de perturbación: [guía](obt-spark.md), [resultados](obt-resultados.md).

Resultados retrospectivos separados: Fail=7.052, Withdrawn=10.156, Approved=15.385. Las listas permitidas de columnas protegen hechos y antecedentes de añadir resultados o retiro; el rol del pipeline puede acceder a todas las tablas.

## Decisiones y límites

| Decisión | Evidencia / efecto | Límite |
|---|---|---|
| Dos hechos con granos distintos | Matrículas y actividad diaria se reconcilian por separado | Agregar actividad antes de combinar hechos; no sumar matrículas o créditos repetidos por eventos. |
| Atributos por matrícula | DIM_STUDENT identifica; DIM_ENROLLMENT conserva contexto | No se inventa un historial de vigencia ni se elige la matrícula más reciente para todas las personas. |
| Retiro y resultados separados | Elegibilidad usa fechas registradas; evaluación usa OUTCOME_ENROLLMENT | Persisten 93 Withdrawn sin fecha de retiro y la incertidumbre histórica documentada en Silver. |
| Suma de todas las contribuciones | Clics y filas fuente conservados desde Silver | Persisten dudas sobre filas idénticas; Gold no cambia la política ni la sensibilidad de 3,19 %. |
| Sin actividad preservada | La población no parte de los clics | Ausencia de registros no prueba cero actividad real ni cobertura completa. |

**Repetición comprobada:** dos builds aprobaron 168 tests cada uno y mantuvieron las mismas 26 métricas agregadas. Se verifican esos invariantes y las reglas de claves; no es una comparación física de todos los bytes.

[Evidencia de repetición correspondiente](repeticion-gold.json).

Evidencia: [build](dbt-build-gold.json), [métricas](calidad-gold.json), [guía y diagrama](gold.md), [SQL de revisión](../snowflake/07_verificar_gold.sql).

Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Publicación GitHub pendiente. La orquestación está verificada según orquestacion-integral.md. Spark y OBT están verificados según obt-spark.md. No hay entrenamiento ni costo monetario cuantificado.
