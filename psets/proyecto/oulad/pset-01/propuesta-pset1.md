# Apoyo académico a tiempo

Wilmer Puerta · PSet 1 · 12 de noviembre de 2026

## 1. El problema de negocio y la métrica de éxito

Una universidad hipotética con tutorías limitadas necesita decidir a quién revisar antes del cierre de cada módulo. Una lista inicial puede omitir estudiantes cuya situación cambia. El proyecto evaluará si la evolución de la actividad digital mejora la focalización preventiva con los mismos cupos; no promete reducir reprobaciones sin evaluar posteriormente el apoyo.

Para cada matrícula estudiante–módulo–edición se estimarán probabilidades de reprobación, retiro y aprobación al cierre, usando información hasta los días 14, 28, 42 y 56. Se compararán regresión logística multinomial y Random Forest con antecedentes estáticos frente a los mismos algoritmos enriquecidos con actividad longitudinal. PR-AUC para reprobación será la métrica técnica principal. La meta provisional es identificar en el día 56 al menos un 10 % relativo más de futuras reprobaciones que el baseline estático, a igual población y capacidad. Se seleccionarán las K puntuaciones más altas, con K = floor(0.10 × N) de matrículas elegibles por edición; el umbral será la última puntuación que cabe en esos cupos. Se considera prioritario reducir omisiones de estudiantes que posteriormente reprueban, sin ignorar que las falsas alertas consumen recursos. Capacidad y costos relativos son supuestos por validar.

## 2. Viabilidad técnica

OULAD es público y los cinco archivos se auditaron localmente [1], [2]. `studentInfo.csv` aporta antecedentes y resultado; `studentVle.csv`, actividad fechada; `vle.csv`, recursos; `courses.csv`, edición y duración; y `studentRegistration.csv`, registro y retiro. Los cinco tienen acceso confirmado. Auditoría local del 12 de noviembre de 2026: 7.052 Fail (21.64 %). 10.156 Withdrawn (31.16 %) y 15.385 aprobaciones (47.20 %). sobre 32.593 matrículas. En la población inicialmente registrada hasta el día 0, 6.980 Fail (21.60 %). 10.068 Withdrawn (31.16 %) y 15.266 aprobaciones (47.24 %). sobre 32.314 matrículas. Son matrículas, no personas únicas ni una tasa institucional actual.

Se construirán características de nivel, recencia y cambio quincenal, distinguiendo inactividad de falta de cobertura y sin usar información futura. La prueba utilizará ediciones posteriores compatibles y estudiantes no usados para ajustar el modelo; las etiquetas históricas deberán estar disponibles antes de cada predicción simulada. Se comparará también una regla operativa de recencia a igual capacidad. El MVP ofrecerá preparación reproducible, inferencia por corte, listas, evolución del riesgo y reporte comparativo. La infraestructura de datos se desarrollará progresivamente en la siguiente etapa con Kestra, dbt, Spark y Snowflake. No hay acceso confirmado a registros institucionales de capacidad, costos o intervenciones.

## 3. Viabilidad de negocio

La propuesta cambia la asignación de revisión preventiva: una lista quincenal sustituye la selección fija o reactiva del escenario hipotético. El coordinador define cupos; el tutor revisa contexto y decide apoyo. El sistema ordena prioridades y no ejecuta sanciones. La simulación comparará regla de recencia, baseline estático y modelos longitudinales con igual población y presupuesto, midiendo detecciones, omisiones, anticipación y revisiones repetidas. El 10 % de capacidad corresponde a un presupuesto preventivo simulado; preservar otros servicios no demuestra disponibilidad de personal adicional.

El impacto académico se evaluaría en un piloto posterior: asignar aleatoriamente estudiantes elegibles a oferta de acompañamiento definido o atención habitual y comparar la proporción que aprueba al cierre, por grupo asignado, con intervalo de confianza. Se observarán también retiro, reprobación, participación, tiempos y costos. La muestra dependerá de la tasa inicial y del efecto mínimo relevante. El PSet actual diseña este protocolo; OULAD permite evaluar focalización retrospectiva, no el efecto causal de nuestra intervención ni ahorros.

## 4. Riesgos principales

**R1. Mejora insuficiente o poco transferible; alta.** Se rompe el supuesto de aporte longitudinal consistente. Comparar a igual K por edición, con incertidumbre; conservar el baseline o limitar el alcance si no se sostiene.

**R2. Información futura o actividad mal representada; crítica.** Se rompe la disponibilidad y comparabilidad al corte. Auditar fechas, etiquetas, cobertura, claves y transformaciones; reconstruir cualquier evaluación afectada. Medir factibilidad de procesamiento y acotar módulos con criterios previos si hace falta.

**R3. Capacidad inviable o apoyo sin efecto; alta.** Se rompe la viabilidad de revisión e intervención útil. Simular cupos del 5 %, 10 % y 20 %, repeticiones y carga; medir participación y resultados solo en el piloto posterior. No afirmar eficiencia monetaria sin costos.

**R4. Errores desiguales o pérdida de confianza; alta.** Se rompe una priorización aceptable entre grupos. Revisar errores por subgrupos con volumen suficiente y el lenguaje de alertas; ajustar reglas y preservar juicio humano y vías habituales de apoyo.

Referencias: [1] J. Kuzilek, M. Hlosta y Z. Zdrahal, “Open University learning analytics dataset,” Scientific Data, 4, 170171, 2017. https://doi.org/10.1038/sdata.2017.171. [2] The Open University, “Open dataset”, https://research.stem.open.ac.uk/ouanalyse/dataset/. Evidencia local: datasets/manifest.json y docs/auditoria-datos.md (12-nov-2026).
