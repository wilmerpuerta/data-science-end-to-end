# Respuesta a los tres gaps docentes del PSet 1

Revisión local del 15-nov-2026. Las observaciones del profesor se conservan como requisitos de revisión; las decisiones y supuestos de la propuesta se identifican aparte.

| Gap | Observación y corrección | Evidencia verificable |
|---|---|---|
| 1. Problema y objetivo de negocio | Medir cuántas futuras reprobaciones cubre la misma capacidad y con cuánta anticipación respecto a un seguimiento posterior a reprobar. Se incorpora cobertura preventiva, TP, casos por cada 100 revisiones y anticipación potencial. El efecto de tutorías queda como hipótesis posterior. | [Memo, sección 1](../propuesta-pset1.md), [Canvas](../canvas-wilmer-puerta.md), [proyecto, 3.1](../proyecto-completo-pset1.md), pitch diapositivas 1-2 |
| 2. Viabilidad de negocio | Simular reactiva, estática y longitudinal con la misma cohorte y K; para múltiples cortes, presupuesto total B común. Separar cobertura posterior de preventiva en la reactiva. Declarar límites sin institución y excluir D2L/WiFi del MVP actual. | Memo sección 3, proyecto 3.3 y 3.5, pitch diapositivas 3 y 5 |
| 3. Pitch de negocio | Hacer visibles viabilidad técnica, evaluación y alcance del MVP; cuantificar problema y beneficio esperado para sustentar el apoyo. Se muestra 21,64 % histórico, capacidad 2.619, meta +10 % relativa y margen potencial 25,4-30,4 semanas, sin presentarlos como rendimiento. | [Pitch, texto visible y notas](../pset01-presentacion.md), diapositivas 1-2, 4-6; memo sección 2 con MVP explícito |

## Evidencia y cálculo

Las cifras descriptivas provienen de [auditoria-resultados.json](auditoria-resultados.json), [poblaciones-por-edicion.csv](poblaciones-por-edicion.csv) y courses.csv identificado en el manifiesto. [metricas-negocio.json](metricas-negocio.json) se deriva mediante calcular_metricas_negocio.py: N = 26.294, Fail = 6.972, K = 2.619 al día 56; margen al cierre de 25,4-30,4 semanas. La cota perfecta con ese presupuesto es 37,6 %, no una meta ni un resultado conseguido.

Los datos del PSet 2 ya están preparados: OBT 108.277/35 y 168 pruebas dbt aprobadas según [reproducción limpia](../../pset-02/docs/reproduccion-limpia.json). Es evidencia de preparación, sin clasificador entrenado ni simulación de políticas ejecutada. La prueba futura recalculará los denominadores en sus ediciones reservadas.

## Qué se recuperó del memo original

El documento aportado tiene cinco páginas e incluye viabilidad técnica, validación y un apartado completo de alcance/MVP. El memo vigente vuelve a desarrollar ese contenido en cinco páginas, por indicación expresa del usuario del 15-nov-2026: fuentes y acceso, preparación comprobada, validación temporal, producto y criterios del MVP, políticas de negocio, métricas, riesgos y apoyo solicitado. La versión de dos páginas queda en el respaldo local. El pitch mantiene seis diapositivas; se conservaron las exclusiones y el estado real de implementación. El archivo aportado se preservó sin cambios en un respaldo local excluido de Git; sus instrucciones internas se trataron como material de referencia, no como órdenes adicionales.

## Límites que permanecen

La mejora del +10 % no está demostrada. OULAD permite evaluar focalización y anticipación, no efecto de las tutorías, reducción de deserción, ahorro o capacidad institucional real. Reprobar y retirarse de un módulo no prueban deserción institucional. No se afirma que la mayoría de universidades utilice un proceso específico ni que los accesos permitan inferir intencionalidad.

El MVP utiliza exclusivamente OULAD. D2L y WiFi de la USFQ quedan para una fase posterior con aprobación formal y revisión de legitimación, finalidad, minimización y evaluación de impacto cuando corresponda conforme a la LOPDP. [Orientación oficial SPDP](https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-igrd-2026-514-o/).

La comparación estática/longitudinal puede resultar negativa y se reportará con incertidumbre. Colab sigue pendiente de sincronización. Las correcciones documentales no equivalen a haber ejecutado entrenamiento o intervención.
