# Matriz de cobertura planificada

Fuente: [rúbrica original](../CD-PSet-4.pdf), 12 páginas. Los pesos son los del profesor. Esta matriz no asigna nota ni certifica ejecución; la API tiene 84 pruebas completas aprobadas y verificación en Docker. Controles y escenario sintético con 32 eventos, 28 alertas y tablero; integración final pendiente.

| Criterio | Peso | Evidencia que deberá existir | Estado |
|---|---:|---|---|
| Patrón de despliegue y servicio | 15 % | Batch justificado; alternativa online explicada; FastAPI Docker; tres endpoints; validación 422; decisión y acción; carga por alias; PREDICCIONES con entradas, salida, versión y latencia. | API Docker, contrato, alias y outbox verificados; 18.323 predicciones conciliadas en Snowflake. |
| Pruebas automáticas y CI/CD | 10 % | pytest de contrato, fixture del modelo y muestra fija, dos comportamientos y fallback; `ci.yml` en push/PR construye imagen y ejecuta pruebas; `cd.yml` publica en GHCR por merge a main con tag de commit. | 84 pruebas, CI y CD aprobados; imagen por commit publicada en GHCR y desplegada por digest. |
| Reentrenamiento, promoción y rollback | 10 % | Disparador y ventana; datos etiquetados; preparación/hiperparámetros conservados; challenger; comparación no contaminada; pausa humana; aprobación o rechazo; rollback y actualización sin rebuild. | Alerta → entrenamiento real → versión challenger → comparación y pausa real verificados; rechazo humano registrado (4 TP adicionales, exige 7), Kestra SUCCESS y champion intacto. Recarga/rollback técnico 1→2→1 verificado en servicio aislado con la imagen publicada; producción sin cambios de alias. |
| Simulación y métricas de monitoreo | 10 % | Ocho lotes, orden temporal y target diferido; Kestra; p50/p95, errores y volumen; métricas técnicas/de negocio por lote; datos faltantes, rangos y categorías; tablero. | Ocho controles y ocho lotes sintéticos, métricas por fase, etiquetas diferidas, tres CSV y tablero verificados. |
| Deriva y alertas | 10 % | PSI por feature, KS y chi-cuadrado; referencia CV para desempeño; tabla diagnóstico/acción; alertas con umbral, ventana, severidad, receptor y acción; lote alterado y controles. | 32 revisiones, 28 alertas y escenario inducido verificados; controles con avisos y caída histórica documentados. |
| Ética, retirada y respaldo | 10 % | Subgrupo con métrica técnica y tasas de decisión; responsables de errores; tres criterios observables de retirada; interruptor y fallback demostrados; supervisión humana. | Auditoría por discapacidad y revisión de L06, responsables FP/FN, cinco criterios y supervisión documentados; interruptor HTTP 0→1→0 demostrado con la imagen publicada, 160 predicciones aisladas y contrato/persistencia conservados. |
| Resultado y presentación ejecutiva | 15 % | Negocio por lote frente a proceso actual y no actuar cuando aplique; cambios por reentrenamiento; respuesta al objetivo; 10-12 diapositivas comprensibles para patrocinador. | Negocio por lote y comparadores calculados: +33,76 % en control, limitaciones, rechazo sin cambio de scores y escenarios del 30 % documentados. Presentación ejecutiva pendiente. |
| Integración, correcciones, reproducibilidad y documento | 20 % | `proyecto_final/`, Compose único, README completo, `docs/cambios.md`, trazabilidad Gold-OBT-run-versión-predicción, notebooks con salidas, cinco CSV, memo hasta 12 páginas y anexos, video hasta siete minutos. | Compose único y fuente→Raw→dbt→Spark OBT verificados; Registry propio íntegro, OBT idéntica y 84 pruebas. Notebooks, memo, presentación y video pendientes. |
| **Total** | **100 %** | | |

## Detalles que no deben omitirse

- La API es obligatoria aunque el patrón elegido sea batch.
- El umbral del PSet 03 deriva del cupo y el ranking; debe trasladarse como política de cohorte completa, no como 0,5 arbitrario.
- Las etiquetas de un lote llegan después del horizonte y no participan prematuramente del monitoreo o reentrenamiento.
- La deriva de entradas sin deterioro no basta para disparar reentrenamiento.
- El último lote etiquetado de comparación queda fuera del entrenamiento de ambos modelos.
- Si el challenger no supera al champion, se conserva el rechazo y su evidencia.
- CI usa un modelo exportado en `tests/fixtures/`; no puede depender del MLflow local.
- El código se publica automáticamente; el modelo requiere la decisión humana documentada.
- Los CSV requeridos son `corridas.csv`, `predicciones.csv`, `monitoreo.csv`, `alertas.csv` y `reentrenamientos.csv`.
- El video debe mostrar infraestructura, ingesta hasta OBT, solicitud válida e inválida, rollback, alerta por deriva, reentrenamiento con pausa y el interruptor.
- El memo incluye el enlace del video; anexos: memos anteriores y `docs/cambios.md`.
- La rúbrica pide dos apellidos en los nombres finales. El PSet 03 usó primer apellido y nombre por indicación del autor; no se supone una excepción docente para el PSet 04.
