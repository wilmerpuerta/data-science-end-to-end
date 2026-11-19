# Resultados de reproducción limpia

Generado por `python3 pset-02/scripts/resumir_reproduccion.py` desde informes reales.

**SUCCESS** en el proyecto aislado `pset2repro_849681d33298`, ejecución `5Q6X4LdUa2UgmMlZAkoifn`. Fecha de comprobación UTC: 2026-11-13T16:03:58.461688+00:00.

## Entorno comprobado

Se exportaron 214 archivos versionables a otra carpeta. No se copiaron entornos, .local, secretos ni salidas de ejecución del PSet 2. Se generaron contraseñas locales nuevas y se usaron puertos 18080/18081, volúmenes PostgreSQL/Kestra nuevos y estado de flujos nuevo.

Las tres imágenes propias se reconstruyeron con --no-cache. Se conservaron las capas base Docker fijadas por digest. Los cinco CSV y los archivos privados Snowflake se referenciaron externamente; las claves y la frase no se copiaron al árbol exportado. La cuenta, rol, warehouse y esquemas Snowflake existentes se reutilizaron.

## Resultado de la cadena

| Etapa | Evidencia |
|---|---|
| Raw | Cinco fuentes LOADED: 10.726.852 filas reconciliadas; recarga real, no NOOP |
| dbt | 23 modelos y 168 pruebas aprobadas |
| Spark/OBT | 108.277 filas y 35 columnas publicadas |
| Tiempo y joins | Cuatro cortes, 4 perturbaciones futuras y lectura de vuelta completa aprobadas |
| Comparación | Las cuatro huellas de contenido coinciden con la ejecución anterior |
| Cierre local | Reproducción detenida y stack principal restaurado con espera de salud |

| Corte | Filas OBT | Sin actividad registrada |
|---|---:|---:|
| 14 | 27.881 | 1.582 |
| 28 | 27.307 | 881 |
| 42 | 26.795 | 684 |
| 56 | 26.294 | 576 |

No se inyectaron fallos en esta reproducción: se ejecutó el camino normal con force_reload=true. Las pruebas de detención y retry permanecen documentadas en la ejecución integral anterior. Los datos de la instancia original de Kestra se conservaron en sus volúmenes.

## Huellas y alcance

Exportación: `34b0580f953837e27336ed47783804cae6a551a727b210dd24bcc885482f124c`. Código de la instantánea: `04a762962f70b7e1e2100c81889cb4ecff6e7b8cad506c89e89c12e3ce7e4928`.

La prueba es una exportación limpia desde el árbol de trabajo, no un clon remoto. No se inició una cuenta Snowflake vacía ni un daemon Docker sin imágenes base. Las huellas identifican la instantánea probada; los informes y documentación de cierre se agregan después. No se afirma compatibilidad ARM, exactitud externa del dataset ni costo monetario medido.

Evidencia: [resumen JSON](reproduccion-limpia.json), [manifiesto de exportación](../output/reproduction/849681d33298/export-manifest.json), [ejecución](../output/reproduction/849681d33298/execution.json), [Raw](../output/reproduction/849681d33298/raw.json), [verificación](../output/reproduction/849681d33298/verification.json), [dbt](../output/reproduction/849681d33298/dbt.json), [Spark](../output/reproduction/849681d33298/spark.json), [procedimiento](reproduccion-limpia.md).

Memo técnico generado: [fuente y exportación](memo-tecnico.md), posterior a la instantánea probada. Revisión local del paquete completada: [informe](revision-paquete.md). Publicación GitHub pendiente de indicación del autor. El consumo monetario continúa sin cuantificar. No hubo entrenamiento ni cambios de alcance metodológico del PSet 1.
