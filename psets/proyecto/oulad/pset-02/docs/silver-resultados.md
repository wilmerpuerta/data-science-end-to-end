# Resultados de Silver

Generado por `python3 pset-02/scripts/resumir_silver.py`; las cifras proceden de los JSON enlazados.

Build: 2026-11-13T00:55:30.065855+00:00; exportación: 2026-11-13T15:02:39.603836+00:00 (UTC).

**101 tests aprobados, cero fallos**: 56 de Silver y 45 de Bronze. Se construyeron siete tablas Silver y se renovaron cinco vistas y una tabla de calidad Bronze. Tiempo dbt del último build: 52.69 s, sin arranque/exportación.

| Tabla Silver | Filas |
|---|---:|
| SLV_EDITIONS | 22 |
| SLV_RESOURCES | 6.364 |
| SLV_ENROLLMENTS | 32.593 |
| SLV_REGISTRATION | 32.593 |
| SLV_OUTCOMES | 32.593 |
| SLV_ACTIVITY_DAILY | 8.459.320 |

La consolidación representa las **10.655.280 filas fuente** mediante **8.459.320 claves diarias únicas**, conservando **39.605.099 clics**. La diferencia de 2.195.960 filas queda explicada por multiplicidad; los tests reconciliaron claves completas, filas representadas y clics por edición.

| Problema o condición | Evidencia | Acción | Justificación |
|---|---|---|---|
| Varias contribuciones por clave diaria | 1.614.505 grupos con más de una fila fuente | Sumar clics, conservar multiplicidad y linaje | Grano diario único sin pérdida de contribuciones registradas; no acredita ausencia de duplicación semántica. |
| Filas fuente idénticas | 787.170 filas adicionales | Mantenerlas en la suma principal; cuantificar sensibilidad | Eliminarlas produciría 38.343.063 clics: 1.262.036 menos (3,19 %). No hay evidencia externa para seleccionar esa corrección. |
| Matrículas sin actividad en todo el archivo | 3.365 | Preservarlas en antecedentes | La OBT deberá partir de matrículas elegibles y usar left joins; ausencia de logs no garantiza cobertura. |
| IMD ausente | 1.111 | NULL e IS_IMD_MISSING | No aprender imputaciones globalmente durante ELT. |
| Semanas de recurso desconocidas | 5.243 | NULL e IS_SCHEDULE_UNKNOWN | No inventar semanas ni deducir cobertura completa. |
| Registro desconocido / tardío | 45 / 234 | Conservar; clasificar explícitamente | Se excluyen de población inicial más adelante conforme al contrato, con conteo. |
| Conflictos entre resultado y retiro | Withdrawn sin fecha: 93; otro resultado con fecha: 9 | Banderas solo en SLV_OUTCOMES | No convertir etiqueta futura en fecha de retiro ni predictor. |
| Actividad anterior al inicio | 600.241 grupos, 2.147.947 clics | Conservar días negativos | Antecedentes separados de ventanas quincenales. |

**Registro inicial:** 32.314 matrículas tienen registro conocido <= 0, consistente con el PSet 1. De ellas, 3.309 no tienen actividad en el archivo y 3.062 tienen retiro conocido <= 0. Todavía no es una tabla de elegibles por corte; no sumar ni restar subgrupos como si fueran disjuntos.

**Etiquetas retrospectivas:** Fail=7.052, Withdrawn=10.156, Approved=15.385. Se conservan las clases originales y sus conteos por edición; no se incluyen en SLV_ENROLLMENTS.

**Repetición comprobada:** dos builds distintos aprobaron 101 pruebas cada uno y produjeron las mismas 27 métricas agregadas. La comprobación cubre conteos, clics y condiciones de calidad junto con los tests de claves; no es una comparación física de todos los bytes almacenados.

Gold se implementó después: [guía y diagrama](gold.md), [resultados](gold-resultados.md). Spark y OBT se implementaron después: [guía](obt-spark.md), [resultados](obt-resultados.md). La orquestación se verificó después: [guía](orquestacion-integral.md), [resultados](pipeline-resultados.md). La reproducción desde exportación limpia se verificó: [resultados](reproduccion-resultados.md). La incertidumbre sobre repetición semántica y retiro sin fecha permanece documentada.

Evidencia: [build](dbt-build-silver.json), [calidad](calidad-silver.json), [guía de ejecución y decisiones](silver.md), [SQL de revisión](../snowflake/06_verificar_silver.sql).
[Informe de repetición correspondiente](repeticion-silver.json).

