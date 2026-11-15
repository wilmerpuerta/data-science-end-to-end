# Cobertura de los memos: rúbrica y tres gaps

Revisión final del 15-nov-2026. Este mapa documenta cobertura, no asigna una nota ni acredita resultados predictivos o intervenciones no ejecutados.

## Dos variantes vigentes

Por solicitud final del usuario, el [memo breve](../output/pdf/PSet1_memo_Puerta_Wilmer.pdf) tiene dos páginas y conserva el nombre original. La [versión extendida](../output/pdf/PSet1_memo_Puerta_Wilmer_version_extendida.pdf) tiene cinco páginas y añade _version_extendida al nombre en el mismo directorio. Ambas mantienen cuatro secciones: problema/métrica, viabilidad técnica, viabilidad de negocio y riesgos. La [rúbrica histórica](../rubrica.md) y el prompt no se modifican; el cambio previo de extensión a cinco páginas queda como antecedente, ahora conservado en la variante extendida.

## Criterios de la rúbrica

| Criterio | Memo breve | Memo extendido | Contenido común |
|---|---|---|---|
| Problema y métrica de éxito | Página 1, sección 1 | Página 1, sección 1 | Decisión, actores, matrícula, tres clases, cortes; cobertura y anticipación; K, umbral y error prioritario; meta relativa y baseline cero. El ejemplo numérico hipotético se desarrolla en la extendida |
| Viabilidad técnica | Página 1, sección 2 | Páginas 2-3, sección 2 | Cinco fuentes y acceso, datos no disponibles, preparación comprobada, algoritmos, validación temporal, estudiantes separados y transformaciones aprendidas solo en entrenamiento |
| Viabilidad de negocio | Página 2, sección 3 | Página 4, sección 3 | Reactiva/estática/longitudinal a igual cohorte/capacidad; presupuesto B, repeticiones, juicio humano, resultados validables y apoyo solicitado |
| Riesgos | Página 2, sección 4 | Página 5, sección 4 | R1-R4 con tipo, supuesto, gravedad, verificación y respuesta; correspondencia con el documento ampliado |
| Calidad profesional | Páginas 1-2 | Páginas 1-5 | Texto autónomo, referencias, cifras observadas separadas de metas, evaluación y MVP explícitos; diferencias de detalle sin contradicción metodológica |

## Tres gaps y síntesis de tutorías

| Punto | Memo breve | Memo extendido | Límite preservado |
|---|---|---|---|
| 1. Objetivo de negocio calculable | Secciones 1 y 3 | Secciones 1 y 3 | Cobertura con mismos cupos, anticipación potencial y omisiones; no tutorías realizadas ni reprobaciones evitadas |
| 2. Proceso de comparación | Sección 3 | Sección 3 | Igual cohorte/K y presupuesto total común; reactiva con cobertura posterior separada y sin capacidad ilimitada |
| 3. Viabilidad, evaluación y MVP | Secciones 1-3 | Secciones 1-3 | Problema cuantificado, preparación real, MVP, métricas y apoyo solicitado; efecto educativo no demostrado |
| Evaluación posterior de tutorías | Página 2, sección 3 | Página 4, sección 3 | Aleatorización por estudiante, oferta/atención habitual, aprobación al cierre, intención de tratar e intervalo de confianza. Ejecución fuera del MVP |

La síntesis del piloto mantiene apoyo habitual en ambos grupos, asignación coherente en matrículas múltiples, seguimiento de participación y otras ayudas y cálculo posterior de muestra. El documento completo conserva el protocolo íntegro, incluido posible agrupamiento y límites de inferencia. No se atribuyen efectos individuales ni superioridad causal de la selección longitudinal a ese ensayo.

## Fuentes y verificación

La [fuente breve](../propuesta-pset1.md) resume la [fuente extendida](../propuesta-pset1_version_extendida.md). Cada PDF conserva íntegro su propio Markdown y registra su SHA-256. El [verificador](../scripts/verificar_entregables.py) exige dos/cinco páginas, texto completo, geometría y coherencia de cifras, riesgos, MVP y protocolo. El [informe visual](revision-visual.json) identifica las salidas inspeccionadas.

Entrenamiento, simulación, demostración predictiva y efecto de tutorías siguen pendientes; OULAD es la única fuente del MVP. D2L/WiFi institucionales quedan para una fase posterior con aprobación formal y revisión LOPDP. Colab continúa pendiente de sincronización. Estos ajustes son posteriores a la publicación f9c9932; el usuario autorizó su publicación en el mismo destino. El historial del repositorio y GitHub Actions registran el resultado de esa actualización.
