# Predicción temprana del riesgo de reprobación

Actividad digital longitudinal para priorizar el acompañamiento académico

Wilmer Puerta · PSet 1 · Versión extendida · 15 de noviembre de 2026

## 1. Problema de negocio y métrica de éxito

### Problema, decisión y población

Una universidad hipotética con capacidad limitada necesita decidir a quién revisar y cuándo ofrecer apoyo. El proceso de referencia simulado espera a conocer la reprobación; la propuesta prioriza la revisión antes del cierre del módulo. No se atribuye ese proceso como práctica comprobada de la USFQ, The Open University o la mayoría de universidades. Los afectados son estudiantes, tutores y responsables de acompañamiento.

En la copia local de OULAD hay **7.052 Fail entre 32.593 matrículas: 21,64 %**. El conjunto contiene 28.785 personas únicas. Son resultados históricos de 2013-2014, no una tasa institucional actual. Reprobar o retirarse de un módulo no demuestra deserción institucional [1, E1]. La unidad analítica es una matrícula estudiante-módulo-edición. La población inicial incluye registros conocidos hasta el día 0; en cada corte se excluyen solo retiros ya ocurridos. Los retiros posteriores permanecen como resultados futuros.

**Objetivo de negocio:** cubrir más futuras reprobaciones con los mismos cupos y cuantificar las semanas de anticipación potencial respecto al cierre. **Pregunta analítica:** ¿añadir actividad longitudinal mejora esa cobertura frente a los mismos algoritmos con antecedentes estáticos? Se estiman probabilidades de Fail, Withdrawn y aprobación (Pass + Distinction), ordenando por P(Fail). Los cortes son días 14, 28, 42 y 56; ocho semanas es observación temprana, no duración total del módulo.

### Métricas, umbral y beneficio esperado

**Cobertura preventiva (%) = 100 × TP seleccionados antes del cierre / Fail elegibles.** TP cuenta matrículas seleccionadas que finalmente reprueban. Se reportarán casos cubiertos, casos por cada 100 revisiones, omisiones, carga repetida y personas únicas. La etiqueta se consulta al evaluar, nunca como predictor temprano.

El caso principal fija la cohorte elegible del día 56 y **K = floor(0.10 × N) por edición**. El umbral será la última puntuación dentro de K, con desempate estable independiente del resultado. Se priorizan omisiones por la oportunidad de apoyo perdida; las falsas alertas consumen cupos. Capacidad y costos relativos son supuestos por validar, con sensibilidad al 5 % y 20 %.

La meta provisional es **+10 % relativo de TP longitudinal frente a TP estático**, con idéntica población y K: 100 × (TP longitudinal - TP estático) / TP estático. Si TP estático = 0 se informa diferencia absoluta. Ejemplo exclusivamente ilustrativo: pasar de 40 a 44 casos con 100 revisiones representa cuatro casos adicionales y 10 % relativo; no cuatro reprobaciones evitadas. No es rendimiento obtenido.

**Anticipación potencial = (duración de la edición - día de primera selección) / 7.** Al día 56 quedan 25,4-30,4 semanas en esta copia. Se resumirá mediana y dispersión para los TP; los casos omitidos permanecen en la cobertura. El cierre aproxima la referencia reactiva: OULAD no aporta fechas reales de tutoría o comunicación de notas. Ese margen disponible no es una anticipación lograda por un modelo [E2]. El beneficio esperado para el patrocinador es una asignación preventiva mejor evaluada, no una reducción demostrada de reprobación.

## 2. Viabilidad técnica, evaluación y alcance del MVP

### 2.1. Fuentes, acceso y preparación comprobada

OULAD es público, anonimizado y publicado con licencia CC BY 4.0; se mantendrá su atribución [1, 2]. Los cinco CSV están disponibles en datasets/, identificados por bytes y SHA-256 y auditados descriptivamente. La publicación describe siete módulos y 22 ediciones. Los identificadores sirven para unir y separar estudiantes, no para memorizarlos como predictores.

| Fuente y grano | Acceso y contenido | Control o límite relevante |
|---|---|---|
| studentInfo.csv, matrícula | Local confirmado; antecedentes y resultado final | Claves y categorías auditadas; verificar disponibilidad inicial de cada atributo; final_result solo como etiqueta |
| studentVle.csv, actividad diaria por recurso | Local confirmado; 10.655.280 aportes | Filtrar al corte, consolidar repeticiones y revisar cobertura; clics no acreditan intención |
| vle.csv, recurso-edición | Local confirmado; tipo y contexto | Claves, recursos y diferencias entre ediciones; contexto no necesariamente disponible por igual |
| courses.csv, módulo-edición | Local confirmado; duración | Permite horizonte de cierre aproximado; verificar compatibilidad temporal de ediciones |
| studentRegistration.csv, matrícula | Local confirmado; registro y retiro | Elegibilidad con fechas conocidas al corte; retiro futuro no es predictor |
| Capacidad, costos e intervenciones | No disponibles ni acceso confirmado | Cupos simulados; no hay registros de tutorías ni efectos educativos para validar |

assessments y studentAssessment no son necesarios: las notas quedan fuera para aislar el aporte de interacción digital. D2L y WiFi institucionales tampoco forman parte de los datos del MVP. La calidad de la copia no demuestra representatividad ni exactitud respecto de la realidad externa.

### 2.2. Factibilidad y características del modelo

El PSet 2 ya implementó Fuente → Kestra → Snowflake Raw → dbt Bronze/Silver/Gold → Spark OBT. La OBT tiene **108.277 filas y 35 columnas**, con grano matrícula-corte; **168 pruebas dbt** aprobaron. La reproducción limpia mantuvo cuatro huellas por corte. Es evidencia de preparación reproducible, no de un modelo entrenado ni de utilidad predictiva [E3].

Se compararán regresión logística multinomial y Random Forest, cada uno estático frente al mismo algoritmo enriquecido con actividad. Antecedentes candidatos: educación previa, intentos, créditos y contexto de matrícula, previa verificación de disponibilidad. Actividad: clics acumulados y quincenales, días activos, recencia, variedad y cambios. El primer corte no tiene dos quincenas completas para comparar; recencia sin registros permanece desconocida. Se preservan matrículas sin clics, distinguiendo ausencia de registros de inactividad real. Se medirán tiempos y recursos de entrenamiento e inferencia; aún no están cuantificados.

### 2.3. Validación temporal y alcance del MVP

La evaluación reservará ediciones posteriores compatibles y estudiantes no utilizados para ajustar. Cada etiqueta histórica de entrenamiento deberá haber madurado antes de la predicción simulada; el año de inicio por sí solo no lo garantiza. Se auditarán duración y disponibilidad del resultado, se mantendrán todos los cortes de una matrícula en la misma partición y se contabilizarán estudiantes repetidos excluidos de la prueba principal. Si no existen pares suficientes, se acotarán módulos y conclusiones antes de consultar resultados finales.

Imputación, escalado, codificación, selección y parámetros aprendidos se ajustarán únicamente con entrenamiento/validación; el test permanecerá reservado. La disponibilidad histórica de todos los atributos y la cobertura semántica de logs siguen pendientes. Cambiar eventos futuros no debe alterar características de un corte anterior. La regla de recencia queda como sensibilidad adicional, sin reemplazar las tres políticas principales.

PR-AUC para Fail frente al resto, precisión/recobrado, matriz de confusión y calibración respaldarán la evaluación técnica. Se fijará la implementación de PR-AUC antes de comparar. Se reportarán ambos algoritmos por edición y corte, con diferencias absolutas/relativas e incertidumbre mediante remuestreo agrupado por estudiante cuando sea viable. La métrica de negocio seguirá siendo cobertura con igual capacidad y anticipación potencial; se admitirán resultados negativos.

### 2.4. Producto, etapas y criterios de aceptación

**MVP previsto:** demostración con OULAD y selector de edición, corte y capacidad para consultar listas priorizadas y evolución del riesgo y reproducir un reporte de las tres políticas. Incluirá modelo y transformaciones versionados e instrucciones de ejecución. La demostración se ejecutará en un entorno controlado separado del ajuste. El resultado final solo aparecerá en una vista de evaluación retrospectiva. Una entrada inválida impedirá emitir una predicción normal.

| Etapa | Evidencia para completar el MVP |
|---|---|
| Datos y exploración | Inventario, diccionario, atribución, claves, elegibilidad, exclusiones y análisis de clases/cobertura; preparación ya implementada, límites documentados |
| Características | Versiones estática y longitudinal reproducibles; cortes correctos y prueba de que el futuro no altera el pasado |
| Modelo y políticas | Validación temporal, prueba reservada, comparación de dos algoritmos y tres políticas con igual presupuesto y métricas con incertidumbre |
| Despliegue | Modelo más transformaciones coherentes, entradas validadas y demostración ejecutable con instrucciones |
| Monitoreo | Versión, faltantes, volúmenes, distribución de puntuaciones y tamaño de listas; desempeño solo cuando existan etiquetas |

El monitoreo se probará mediante reproducción histórica y rangos definidos en entrenamiento/validación. Un cambio relevante generará revisión, no reentrenamiento automático ni una afirmación de caída de precisión sin etiquetas. **Aceptar el MVP** exige reproducción, control temporal, presupuestos comparables y resultados trazables; alcanzar +10 % es una hipótesis separada. Preparación está implementada; entrenamiento, evaluación, simulación y demostración predictiva siguen pendientes.

## 3. Viabilidad de negocio y comparación del seguimiento

### Tres políticas con la misma capacidad

El escenario de referencia espera a conocer Fail; las alternativas anticipan la revisión. Se mantienen fijos los resultados históricos. La comparación principal usa la misma cohorte del día 56 y K por edición, sin capacidad ilimitada para la reactiva.

| Política simulada | Información y selección | Momento y lectura del resultado |
|---|---|---|
| Reactiva | Hasta K Fail conocidos de la cohorte, con desempate prefijado | Después del cierre; cobertura preventiva cero y cobertura posterior informada aparte |
| Estática | Top K por P(Fail) con antecedentes iniciales | Día 56, para comparar el aporte de variables sobre la misma población |
| Longitudinal | Top K con esos antecedentes y actividad hasta el corte | Mismo día 56 y capacidad; cobertura y anticipación antes del cierre |

El estático puede utilizarse antes; evaluarlo al mismo corte aísla el aporte longitudinal. La reactiva conoce el resultado: su precisión posterior no mide superioridad predictiva. Compararla con las alternativas mide oportunidad preventiva; estática frente a longitudinal mide focalización.

El histórico del día 56 contiene **26.294 elegibles, 6.972 Fail y 2.619 cupos**, suma de floor(0.10 × N) por edición. Una selección perfecta cubriría como máximo **37,6 %** de esos Fail: cota de capacidad, no desempeño. Se recalculará sobre la prueba reservada [E2].

### Carga, responsables y valor validable

Para cuatro listas se fijará presupuesto total B común por edición y reparto/reserva previos. Cada revisión repetida consume un cupo; la suma no excederá B. Cada matrícula cuenta una vez en cobertura acumulada; se informan personas únicas y reservas no usadas. La reactiva puede gastar su presupuesto tras el cierre.

El coordinador valida cupos; el tutor revisa contexto y contactos previos y decide orientación, tutoría o derivación; el responsable analítico controla calidad y evaluación. El sistema solo calcula y ordena, sin contacto ni sanciones. Quienes no figuren conservarían vías habituales de apoyo. Son roles propuestos, sin institución comprometida.

Sin institución se validan preparación, predicción y focalización simulada, no aceptación, capacidad real, costos, eficacia educativa, ahorro o transferencia. **Apoyo solicitado:** respaldar la prueba de concepto y aportar referentes para revisar utilidad y cupos. Se entregará una comparación trazable con incertidumbre; si no aporta valor, se conservará el baseline o acotará el alcance.

### Evaluación posterior de las tutorías, fuera del MVP

El piloto contrastaría si ofrecer acompañamiento mejora la aprobación al cierre. Entre elegibles en riesgo según una regla previa, se haría asignación aleatoria por estudiante a oferta de tutoría o atención habitual, estratificada por módulo/riesgo; las matrículas múltiples conservarían una asignación coherente. Ambos grupos mantendrían el apoyo habitual. La oferta incluiría contacto, evaluación de necesidades, tutoría y seguimiento definidos.

Resultado principal: proporción de aprobación (Pass + Distinction), diferencia absoluta entre grupos e intervalo de confianza, por intención de tratar; informar también Fail y Withdrawn, participación, otras ayudas, tiempos y costos. La muestra se calcularía según tasa inicial, efecto mínimo, potencia, pérdidas y agrupamiento cuando corresponda, controlando contaminación. Estima el efecto de ofrecer ese programa, no efectos individuales ni superioridad causal de la selección longitudinal. El piloto, fuera del MVP, requiere institución, aprobación formal, capacidad y datos nuevos.

## 4. Riesgos, respuestas y límites institucionales

**R1. Aporte insuficiente o transferencia limitada. Técnico/negocio; gravedad alta.** Supuesto: la actividad aporta información útil y consistente fuera del ajuste. Verificación: comparación emparejada por algoritmo, corte y edición, incertidumbre y subgrupos con volumen suficiente. Respuesta: reportar resultados negativos, conservar el estático, recalibrar o restringir población; exigir validación externa antes de adopción. No se presenta la meta del 10 % como un resultado.

**R2. Fuga, cobertura o procesamiento inadecuados. Técnico; gravedad crítica.** Supuesto: datos y etiquetas eran conocidos al corte y la actividad es comparable. Verificación: fechas, claves, maduración, particiones, transformaciones y cobertura por edición; pruebas temporales y medición de recursos. Respuesta: reconstruir toda evaluación afectada, marcar datos desconocidos y acotar módulos antes de la prueba final. Ausencia de clics no acredita desinterés; los registros digitales no demuestran intencionalidad.

**R3. Capacidad inviable, baja adopción o apoyo sin efecto. Negocio/adopción; gravedad alta.** Supuesto: las listas podrían utilizarse con los recursos disponibles y un apoyo posterior sería útil. Verificación actual: sensibilidad de cupos, repeticiones y carga; revisión de utilidad con referentes si se consigue participación. Costos, tiempos reales, aceptación y efecto académico se medirían en otra fase. Respuesta: ajustar frecuencia y reglas, mantener vías de apoyo y limitar la conclusión a focalización; no afirmar ahorro ni aprobación ganada.

**R4. Errores desiguales o pérdida de confianza. Adopción; gravedad alta.** Supuesto: la priorización no perjudica desproporcionadamente a grupos y las alertas son comprensibles. Verificación: omisiones y falsas alertas por subgrupos con tamaño suficiente, revisión de atributos demográficos y lenguaje con usuarios en una fase posterior. Respuesta: ajustar variables o reglas, declarar incertidumbre, preservar juicio humano y evitar etiquetas sancionatorias. Los cuatro grupos conservan la correspondencia con los ocho riesgos del documento ampliado.

**Fuera de alcance:** integración universitaria, captura en tiempo real, tutorías efectivas, sanciones, predicción de deserción institucional, inferencia de intencionalidad, demostración causal y ahorro monetario. El MVP utiliza exclusivamente OULAD. D2L y WiFi de la USFQ quedan para una fase posterior, con aprobación formal y revisión de cumplimiento LOPDP por los responsables institucionales. Los registros vinculables de WiFi pueden revelar ubicación; deberán justificarse legitimación, finalidad, minimización y seguridad, y evaluar impacto cuando corresponda. Una autorización académica por sí sola no sustituye esa revisión [3]. Los modelos complejos de secuencias no son requisito.

### Referencias y evidencia local

[1] J. Kuzilek, M. Hlosta y Z. Zdrahal, “Open University learning analytics dataset”, Scientific Data, vol. 4, art. 170171, 2017, doi:10.1038/sdata.2017.171.

[2] The Open University, documentación de OULAD: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/.

[3] SPDP, oficio SPDP-IGRD-2026-514-O. Orientación general sobre legitimación, principios, riesgos y evaluación de impacto; no autorización específica para WiFi universitario. https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-igrd-2026-514-o/. Consultado: 15-nov-2026.

[E1] datasets/manifest.json; pset-01/docs/auditoria-resultados.json y poblaciones-por-edicion.csv. [E2] pset-01/docs/metricas-negocio.json: descriptivos, margen temporal y cota de capacidad, sin modelo. [E3] pset-02/docs/reproduccion-limpia.json: preparación y reproducción verificadas, sin entrenamiento ni simulación de políticas.
