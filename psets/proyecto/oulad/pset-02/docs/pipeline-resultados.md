# Resultados de orquestación integral

Generado por `python3 pset-02/scripts/resumir_pipeline.py` desde informes de ejecuciones reales.

**Kestra SUCCESS:** `6X7mzEdM0yvoBSbp8MnALv`. Raw → gate → dbt → Spark → verificación, sin intervención manual entre etapas.

| Tarea | Estado | Intentos |
|---|---|---:|
| raw | SUCCESS | 1 |
| gate | SUCCESS | 2 |
| dbt | SUCCESS | 1 |
| spark | SUCCESS | 1 |
| verificar | SUCCESS | 1 |

Raw, subflujo `1tO0m3BdzY1gz3ZRkkR8sQ`: cinco fuentes reconciliadas, 10.726.852 filas (todas NOOP en esta ejecución). dbt construyó/revalidó 23 modelos y aprobó **168 pruebas**. Spark publicó **108.277 filas y 35 columnas**, con población, perturbaciones y lectura completa de vuelta aprobadas.

**Recuperación controlada:** gate falló una vez antes de dbt/Spark y pasó al segundo intento. La ejecución completa terminó correctamente. La prueba no representa una caída real de Snowflake.

**Detención controlada:** `rO8O8wCISIAhJx4fYSR2K` terminó FAILED después de Raw y gate; dbt, Spark y verificación no se iniciaron. Raw produjo cinco NOOP y no hubo publicación OBT desde ese flujo. No se presenta ese FAILED deliberado como una ejecución productiva exitosa.

**API interna:** ambos ejecutores rechazaron campos de comando libre con HTTP 400 sin crear trabajos. Repetir POST con la misma ejecución reutilizó el mismo job_id/intento para dbt y Spark; cada uno se ejecutó una vez en la cadena exitosa.

Los calendarios padre y Raw permanecen desactivados. Un único flujo padre puede ejecutar a la vez; las operaciones manuales también deben respetar el escritor único. La atomicidad es por carga/modelo/publicación OBT, no una transacción de toda la cadena.

Evidencia: [resumen JSON](pipeline-pruebas.json), [cierre canónico](pipeline-verificacion.json), [ejecución exitosa](../output/pipeline/6X7mzEdM0yvoBSbp8MnALv/execution.json), [verificación](../output/pipeline/6X7mzEdM0yvoBSbp8MnALv/verification.json), [prueba API](../output/pipeline/6X7mzEdM0yvoBSbp8MnALv/api-probe.json), [fallo controlado](../output/pipeline/rO8O8wCISIAhJx4fYSR2K/execution.json), [guía](orquestacion-integral.md).

Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Pendientes: cuantificación de costo monetario y publicación GitHub. No se ha publicado el repositorio ni activado el calendario.
