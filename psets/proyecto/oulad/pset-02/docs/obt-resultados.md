# Resultados de la OBT con Spark

Generado por `python3 pset-02/scripts/resumir_obt.py`; no editar cifras manualmente.

Inicio de comprobación UTC: 2026-11-13T15:02:49.739211+00:00. Run: 6e944512032a677434f15a762defb3d2. Duración: 249.79 s.

**PSET2_OULAD.ANALYTICS.OBT_FEATURES publicada: 108.277 filas y 35 columnas; 108.277 claves matrícula–corte únicas.** Se leyeron 3.474.573 filas diarias Gold con día <= 56; las cinco versiones de fuente coinciden con el manifiesto.

| Corte | Filas OBT | Gold y PSet 1 | Sin actividad registrada al corte | Clics acumulados de elegibles | Clics ventana actual |
|---|---:|---:|---:|---:|---:|
| 14 | 27.881 | 27.881 | 1.582 | 6.040.639 | 3.701.848 |
| 28 | 27.307 | 27.307 | 881 | 9.796.266 | 3.817.443 |
| 42 | 26.795 | 26.795 | 684 | 12.357.596 | 2.674.353 |
| 56 | 26.294 | 26.294 | 576 | 14.773.890 | 2.571.891 |

Los clics acumulados incluyen preinicio, día cero y días 1..corte. Los totales de diferentes cortes no se suman: contienen historia repetida y poblaciones elegibles distintas. Las ventanas actuales son 1–14, 15–28, 29–42 y 43–56.

## Verificaciones ejecutadas

- Contexto real del usuario de servicio comprobado desde Spark; conector 3.2.3-spark_3.5/JDBC 4.4.1 y Spark 3.5.6/Scala 2.12.18/Java 17.
- Siete casos sintéticos aprobados antes de construir con OULAD.
- Población calculada antes de actividad; igualdad completa de claves con referencia SQL independiente por corte; conteos y ausencias coinciden con la auditoría PSet 1.
- Unicidad matrícula–corte, conservación en joins y ausencia de pérdida de matrículas sin actividad.
- Cuatro pruebas reales de perturbación: clics futuros modificados y evento futuro insertado para una matrícula elegible; ninguna feature pasada cambió.
- Recencia no negativa; recencia NULL cuando no hay actividad; primera comparación entre quincenas NULL; contadores temporales reconciliados.
- Lectura de vuelta desde Snowflake igual al DataFrame completo, en ambas direcciones, antes de publicar.
- Lista de columnas permitidas y exclusión de resultado final, target y fecha de retiro.

## Columnas y uso futuro

El contrato separa 6 identificadores, 11 predictores estáticos, 16 predictores de actividad y 2 campos de auditoría. Los identificadores y auditoría no se convierten automáticamente en variables del modelo.

| Rol | Columnas |
|---|---|
| Identificadores | `enrollment_key`, `cutoff_day`, `id_student`, `edition_key`, `code_module`, `code_presentation` |
| Estáticas | `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `num_of_prev_attempts`, `studied_credits`, `disability`, `is_imd_missing`, `module_presentation_length`, `registration_days_before_start` |
| Actividad | `clicks_through_cutoff`, `clicks_since_start`, `clicks_prestart`, `clicks_day_zero`, `active_days_through_cutoff`, `resources_through_cutoff`, `activity_types_through_cutoff`, `clicks_current_14d`, `active_days_current_14d`, `clicks_forum_current_14d`, `clicks_oucontent_current_14d`, `clicks_previous_14d`, `click_change_14d`, `click_ratio_14d`, `recency_days`, `has_recorded_activity` |
| Auditoría | `last_activity_day`, `log_coverage_known` |

Los ceros de contadores significan cero registros observados; no prueban ausencia real de actividad académica. LOG_COVERAGE_KNOWN permanece false y la recencia ausente se mantiene NULL. No hubo imputación aprendida, escalado, encoding ajustado ni entrenamiento. OUTCOME_ENROLLMENT permanece separado para evaluación retrospectiva.

**Repetición comprobada:** dos ejecuciones publicaron 108.277 filas cada una, con las mismas cuatro huellas SHA-256 canónicas, columnas, población y métricas. Cada ejecución verificó lectura de vuelta completa y perturbaciones futuras.

[Informe de repetición correspondiente](repeticion-obt.json).

Evidencia: [ejecución OBT](obt-verificacion.json), [conexión Spark](spark-conexion.json), [casos sintéticos](spark-pruebas.json), [contrato](../spark/feature-contract.json), [guía](obt-spark.md), [SQL de revisión](../snowflake/08_verificar_obt.sql).

Orquestación integral verificada: [guía](orquestacion-integral.md), [resultados](pipeline-resultados.md). Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Pendientes: costo monetario y publicación GitHub. Persisten limitaciones de cobertura de logs, exactitud externa y retiro sin fecha; no se declara validado un modelo predictivo.
