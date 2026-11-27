# Matriz de cobertura y pendientes

Fuente: [rúbrica original](../CD-PSet-4.pdf), 12 páginas. Los pesos son los del profesor. Esta matriz no asigna nota ni certifica ejecución; la API tiene 84 pruebas completas aprobadas y verificación en Docker. Controles y escenario sintético con 32 eventos, 28 alertas y tablero; integración verificada y documentos de comunicación preparados. Los siete notebooks tienen salidas verificadas; el video de 6:52 está publicado y enlazado en el memo; el pitch histórico está incluido en PDF.

| Criterio | Peso | Evidencia que deberá existir | Estado |
|---|---:|---|---|
| Patrón de despliegue y servicio | 15 % | Batch justificado; alternativa online explicada; FastAPI Docker; tres endpoints; validación 422; decisión y acción; carga por alias; PREDICCIONES con entradas, salida, versión y latencia. | API Docker, contrato, alias y outbox verificados; 18.323 predicciones conciliadas en Snowflake. |
| Pruebas automáticas y CI/CD | 10 % | pytest de contrato, fixture del modelo y muestra fija, dos comportamientos y fallback; `ci.yml` en push/PR construye imagen y ejecuta pruebas; `cd.yml` publica en GHCR por merge a main con tag de commit. | 84 pruebas, CI y CD aprobados; imagen por commit publicada en GHCR y desplegada por digest. |
| Reentrenamiento, promoción y rollback | 10 % | Disparador y ventana; datos etiquetados; preparación/hiperparámetros conservados; challenger; comparación no contaminada; pausa humana; aprobación o rechazo; rollback y actualización sin rebuild. | Alerta → entrenamiento real → versión challenger → comparación y pausa real verificados; rechazo humano registrado (4 TP adicionales, exige 7), Kestra SUCCESS y champion intacto. Recarga/rollback técnico 1→2→1 verificado en servicio aislado con la imagen publicada; producción sin cambios de alias. |
| Simulación y métricas de monitoreo | 10 % | Ocho lotes, orden temporal y target diferido; Kestra; p50/p95, errores y volumen; métricas técnicas/de negocio por lote; datos faltantes, rangos y categorías; tablero. | Ocho controles y ocho lotes sintéticos, métricas por fase, etiquetas diferidas, tres CSV y tablero verificados. |
| Deriva y alertas | 10 % | PSI por feature, KS y chi-cuadrado; referencia CV para desempeño; tabla diagnóstico/acción; alertas con umbral, ventana, severidad, receptor y acción; lote alterado y controles. | 32 revisiones, 28 alertas y escenario inducido verificados; controles con avisos y caída histórica documentados. |
| Ética, retirada y respaldo | 10 % | Subgrupo con métrica técnica y tasas de decisión; responsables de errores; tres criterios observables de retirada; interruptor y fallback demostrados; supervisión humana. | Auditoría por discapacidad y revisión de L06, responsables FP/FN, cinco criterios y supervisión documentados; interruptor HTTP 0→1→0 demostrado con la imagen publicada, 160 predicciones aisladas y contrato/persistencia conservados. |
| Resultado y presentación ejecutiva | 15 % | Negocio por lote frente a proceso actual y no actuar cuando aplique; cambios por reentrenamiento; respuesta al objetivo; 10-12 diapositivas comprensibles para patrocinador. | Negocio por lote y comparadores calculados: +33,76 % en control, limitaciones, rechazo sin cambio de scores y escenarios del 30 % documentados. Presentación ejecutiva de 12 diapositivas preparada y revisada visualmente; expone beneficio, riesgos, rechazo y recomendación de piloto. |
| Integración, correcciones, reproducibilidad y documento | 20 % | `proyecto_final/`, Compose único, README completo, `docs/cambios.md`, trazabilidad Gold-OBT-run-versión-predicción, notebooks con salidas, cinco CSV, memo hasta 12 páginas y anexos, video hasta siete minutos. | Compose único y fuente→Raw→dbt→Spark OBT verificados; Registry propio íntegro, OBT idéntica y 84 pruebas. Memo de 12 páginas, anexos y guion de 6:35 preparados y revisados; siete notebooks 01-07 ejecutados con salidas y auditoría PSet1 conciliada; pitch histórico en PDF, video publicado de 6:52 y URL accesible incorporada al memo. |
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
- La rúbrica pide dos apellidos en los nombres finales. Se mantiene `Puerta_Wilmer` por indicación del autor; no se supone una excepción docente.


## Documentación preparada y límites del cierre

El [memo](../../proyecto_final/docs/PSet4_memo_Puerta_Wilmer.pdf) tiene 12 páginas y los [anexos](../../proyecto_final/docs/PSet4_anexos_Puerta_Wilmer.pdf) reúnen los tres memos previos y cambios. La [presentación](../../proyecto_final/docs/PSet4_presentacion_Puerta_Wilmer.pdf) tiene 12 diapositivas; el [guion](../../proyecto_final/docs/guion_video.md), nueve escenas en 6:35. Memo páginas 8/11 muestran métricas por lote; página 11 marca el disparador y la reserva del reentrenamiento sin atribuir un cambio de scores inexistente. Página 7 contiene una captura real de Actions y el digest activo. Página 10 muestra AP, tasas de propuesta/seguimiento y cobertura/FPR por discapacidad.

El [video de demostración](https://drive.google.com/file/d/11P7KdS9zWTNWfUkhNJrOdMeW7uvE2NG6/view?usp=sharing) dura 6:52,34 y su acceso sin autenticación se verificó el 27-nov-2026. Su URL está incorporada al memo. Los siete notebooks finales conservan salidas verificadas; el pitch histórico original está exportado a PDF e incluido en el historial y los anexos. La independencia de 2014J no se recupera con la reconstrucción: sus cifras son retrospectivas y se requiere una cohorte futura sin consultar. La matriz acredita implementación y evidencia disponible; conserva los límites metodológicos y no asigna una calificación.


## Verificación de cierre (27-nov-2026)

Los 42 archivos exigidos y las carpetas dbt, Spark y fixtures están presentes. Memo: 12 páginas; presentación: 12 diapositivas; video: 6:52,34; historial: tres memos y pitch original de seis páginas; siete notebooks con salidas; cinco CSV. El memo tiene enlaces clicables a la demo. Se mantienen explícitos la prueba histórica reutilizada, el rechazo del candidato, el rollback mecánico aislado y el carácter hipotético del presupuesto y del efecto tutorial.
