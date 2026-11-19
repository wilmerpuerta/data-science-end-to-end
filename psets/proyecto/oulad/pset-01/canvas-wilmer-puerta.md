# Canvas de viabilidad y riesgos

Wilmer Puerta · PSet 1 · Revisión del 15-nov-2026

## Problema y decisión

Una universidad hipotética necesita priorizar revisión con cupos limitados. El proceso de referencia simulado espera a conocer la reprobación. Se comparará con priorización estática y longitudinal. El coordinador valida capacidad; el tutor revisa contexto y decide el apoyo. No hay institución participante confirmada ni contacto real en el MVP.

## Objetivo de negocio y métricas

Cubrir más futuras reprobaciones con los mismos cupos y cuantificar la anticipación potencial respecto al cierre. Cobertura preventiva (%) = 100 × TP antes del cierre / Fail elegibles. Reportar casos cubiertos, cobertura, casos por cada 100 revisiones, omisiones, carga repetida y personas únicas. La unidad de evaluación es matrícula estudiante-módulo-edición.

Meta provisional: +10 % relativo de TP longitudinal frente a TP estático al día 56, igual N y K. Mejora (%) = 100 × (TP longitudinal - TP estático) / TP estático; si el denominador es cero se informa diferencia absoluta. No es un resultado alcanzado ni reprobaciones evitadas.

Anticipación potencial = (duración de la edición - día de primera selección) / 7. Duraciones observadas: 234-269 días. Al día 56 quedan 25,4-30,4 semanas hasta el cierre. Es margen disponible; los casos detectados y su anticipación efectiva se medirán al evaluar las listas. No se conoce la fecha real de tutoría o de comunicación de notas.

## Predicción y evaluación

Probabilidades de Fail, Withdrawn y aprobación (Pass + Distinction), priorizando P(Fail). Registro conocido hasta día 0; excluir solo retiros ya ocurridos en cada corte. Días 14, 28, 42 y 56. Regresión logística multinomial y Random Forest, cada uno estático frente al mismo algoritmo enriquecido con actividad digital. Sin notas de evaluaciones, D2L o WiFi institucionales.

Prueba con ediciones posteriores compatibles y estudiantes separados entre ajuste y evaluación; verificar maduración de etiquetas antes de la fecha simulada. Aprender transformaciones únicamente con entrenamiento. PR-AUC, calibración e incertidumbre acompañan las métricas de negocio. La actividad describe registros observados, no intención o motivación. El aporte longitudinal puede ser pequeño o nulo.

## Tres políticas con la misma capacidad

| Política | Regla reproducible | Momento |
|---|---|---|
| Reactiva | Hasta K Fail conocidos, con desempate por clave estable | Tras el cierre; anticipación preventiva cero |
| Estática | Top K por P(Fail), con antecedentes iniciales | Día 56 en comparación principal |
| Longitudinal | Top K por P(Fail), con antecedentes y actividad <= corte | Mismo día 56 y población |

K = floor(0.10 × N) por edición, fijado desde la cohorte elegible al día 56 para las tres políticas. Sensibilidad 5 % y 20 %. El umbral predictivo es la última puntuación que cabe; los desempates no consultan etiquetas. La reactiva usa el resultado solo cuando ya se conoce. Los resultados académicos históricos permanecen fijos en la simulación.

Se consideran prioritarias las omisiones por la oportunidad de apoyo perdida; las falsas alertas consumen cupos. Esta prioridad y los costos relativos requieren validación institucional.

En el histórico completo: 26.294 elegibles, 6.972 Fail y 2.619 cupos al día 56; cobertura máxima teórica con ese presupuesto: 37,6 %. Recalcular sobre las ediciones de prueba. Una regla adicional de recencia puede servir de sensibilidad, sin sustituir ninguna de las tres políticas principales.

Para varios cortes se comparan presupuestos totales iguales. Cada revisión repetida consume un cupo; cada matrícula cuenta una vez en cobertura acumulada. Informar también personas únicas. Las capacidades por corte ya auditadas son descriptivas; no conceden a la política longitudinal contactos adicionales gratuitos frente a una lista única.

## Datos y acceso

| Dato | Fuente | Estado |
|---|---|---|
| Antecedentes y resultado final | studentInfo.csv | 32.593 matrículas; 7.052 Fail, 21,64 %; 28.785 personas únicas |
| Registro y retiro | studentRegistration.csv | Fechas relativas; faltantes y discrepancias documentados |
| Edición y duración | courses.csv | 22 ediciones; 234-269 días |
| Recursos | vle.csv | 6.364 recursos; calendario incompleto |
| Actividad digital fechada | studentVle.csv | 10.655.280 aportes; multiplicidad preservada en Raw |
| Capacidad, costos e intervenciones | Institución participante | Sin datos confirmados; presupuesto simulado |

Los originales son históricos de 2013-2014 y se mantienen intactos. No extrapolar tasas a la USFQ. Reprobar o retirarse de un módulo no acredita deserción institucional. [Auditoría](docs/auditoria-datos.md) y [métricas de negocio](docs/metricas-negocio.json).

## Viabilidad técnica y alcance del MVP

El PSet 2 ya construyó la cadena Kestra, Snowflake, dbt y Spark: OBT de 108.277 filas/35 columnas, 168 pruebas dbt y controles temporales aprobados. Esto acredita preparación reproducible; entrenamiento, evaluación predictiva y simulación de políticas siguen pendientes. La disponibilidad histórica de todos los atributos debe comprobarse antes del ajuste.

MVP previsto: selector de edición/corte/capacidad, modelo y transformaciones versionados, listas priorizadas con señales observadas, evolución del riesgo y reporte comparativo de las tres políticas con cobertura, anticipación y carga. Criterios: mismos presupuestos y poblaciones, separación temporal, reproducción de inferencia y reporte de incertidumbre. Completar el MVP no garantiza alcanzar la meta del 10 %.

## Resultado validable y fases posteriores

Con OULAD se pueden evaluar retrospectivamente cobertura, anticipación potencial, omisiones y carga simulada. La simulación no registra tutorías realizadas ni cambia los resultados históricos. Participación, tiempos, costos, capacidad real, reducción de Fail o de deserción y transferencia a la USFQ requieren una fase institucional posterior. Que ofrecer tutorías mejore la aprobación es una hipótesis para esa fase.

El MVP utiliza exclusivamente OULAD. D2L y WiFi de la USFQ quedan fuera. Un uso posterior de registros WiFi vinculables puede revelar ubicación y requiere aprobación formal y revisión de legitimación, finalidad, minimización y evaluación de impacto cuando corresponda conforme a la LOPDP. La autorización académica por sí sola no resuelve esos requisitos. [Orientación oficial SPDP](https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-igrd-2026-514-o/).

## Riesgos, supuestos, verificación y gravedad

**R1. Aporte insuficiente o poco transferible; alta.** Supone mejora longitudinal: comparar con incertidumbre y admitir resultados negativos; conservar el baseline cuando corresponda.

**R2. Fuga o actividad mal representada; crítica.** Supone disponibilidad temporal y comparabilidad: verificar fechas, maduración, cobertura, cardinalidad y perturbaciones futuras; reconstruir evaluaciones afectadas.

**R3. Capacidad o adopción inviables; alta.** Supone listas atendibles y apoyo útil: simular presupuestos y repeticiones; validar utilidad y recursos con referentes académicos en una fase posterior.

**R4. Errores desiguales o pérdida de confianza; alta.** Supone priorización aceptable: evaluar subgrupos con volumen suficiente, mantener juicio humano y acceso habitual al apoyo.
