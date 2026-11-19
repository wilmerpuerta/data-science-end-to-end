# Alcance de negocio acordado

Registro: 18-nov-2026. Fuente: conversación con el autor y rúbrica del PSet 04. La Universidad es un escenario de aplicación; no se han confirmado un socio institucional, presupuestos, costos ni disponibilidad docente.

## Objetivo

Lograr al menos 10 % de mejora relativa en cobertura de Fail frente al modelo estático, con los mismos cupos, durante el período en curso. El autor confirmó este objetivo al retomar PSet 04. La mejora es `cobertura_longitudinal / cobertura_estatica - 1`, con la misma cohorte base y capacidad; no equivale a diez puntos porcentuales. Si la cobertura estática es cero, la razón no se define.

El adelanto de hasta el 30 % de cupos reactivos futuros es un escenario presupuestario separado, sin aprobación institucional. No transforma detecciones adicionales en Fail evitados ni en tutorías efectivamente realizadas.

Las tutorías preventivas se prestan durante el período en curso. La detección tiene dos puntos funcionales, semanas 2 y 4. El reparto de cupos y la política de una o dos rondas siguen por definir. El target conserva el resultado Fail al cierre del período de la matrícula. El margen entre predicción, contacto e intervención se documentará como supuesto hasta que una Universidad lo valide.

## Presupuestos y capacidad

| Bolsa | Uso | Tratamiento |
|---|---|---|
| Reactiva vigente | Atención a reprobaciones de períodos anteriores | Se conserva separada y protegida. |
| Preventiva vigente | Apoyo temprano a riesgo detectado durante este período | Propuesta de financiamiento mediante un adelanto del presupuesto reactivo futuro. |
| Reactiva futura | Atención posterior a reprobaciones que efectivamente ocurran | Se registra el saldo tras la transferencia; no se presupone que desaparece su demanda. |

La transferencia se contabiliza una sola vez. Un porcentaje de presupuesto monetario no equivale al mismo porcentaje de estudiantes: deben definirse el costo por atención y las horas docentes disponibles en la ventana de intervención.

La capacidad preventiva operativa debe respetar tanto el presupuesto como la disponibilidad actual de tutores. El adelanto de dinero futuro no acredita por sí mismo disponibilidad de atención en el presente.

Como escenario presupuestario, se propone solicitar el adelanto de hasta el 30 % de los cupos reactivos previstos para el período posterior. Es un escenario de solicitud, pendiente de validación institucional y conversión a presupuesto y horas; no acredita un nivel bajo de FP. No se ha autorizado gasto nuevo. El 10 % del PSet 03 es una capacidad de referencia experimental, no una fracción presupuestaria aprobada para este programa.

## Dos evaluaciones distintas

1. **Aporte predictivo:** comparar longitudinal, control estático y otras reglas admisibles usando la misma cohorte, corte y capacidad preventiva. Así se mide el aporte de la información y del modelo.
2. **Política presupuestaria:** comparar mantener recursos para atención reactiva con anticipar una parte. La comparación debe cubrir ambos períodos, preservar la bolsa reactiva vigente y registrar el saldo de la bolsa futura.

Se mantienen separadas las matrículas detectadas, las personas únicas, las tutorías propuestas, las aceptadas y las efectivamente realizadas. La unidad del prototipo es matrícula-asignatura, con personas únicas aparte; su conversión a sesiones u horas y su validación institucional siguen pendientes. Una política por persona requerirá una regla explícita para consolidar varias matrículas y recalcular las métricas; no se reutilizarán directamente los resultados por matrícula del PSet 03.

## Hipótesis de valor y límites de la evidencia

Cada atención preventiva representa una oportunidad de reducir atención reactiva posterior. No se establece una equivalencia uno a uno ni se transforma el número de casos detectados en ahorro observado.

La simulación reportará focalización, margen de actuación y uso de capacidad. La efectividad causal de la tutoría, la aceptación de la oferta, los costos institucionales y la proporción de Fail que habría recibido atención reactiva necesitan datos adicionales o un piloto.

Los escenarios económicos incluirán efectividad cero. Si se presenta una estimación como `K * r * e * q`, se declarará que `K` son atenciones comparables, `r` es una proporción histórica de Fail entre seleccionados, `e` es efectividad hipotética y `q` es probabilidad hipotética de atención reactiva posterior. La expresión es un escenario, no un estimador causal obtenido de OULAD. Una transferencia de presupuesto no se contabiliza además como un beneficio.

## Ranking y API batch

- Kestra prepara la cohorte elegible completa y una identidad de lote con período, grupo y fecha de corte.
- El lote usa una sola versión de modelo y una sola versión de política. Se define qué constituye un lote completo antes de asignar cupos.
- El modelo produce probabilidades. La política aplica capacidad, elegibilidad y desempate determinista, sin utilizar el target de las consultas.
- No se asigna un 10 % nuevo por cada fragmento o llamada HTTP de una misma cohorte. Las repeticiones de un lote deben ser idempotentes.
- La respuesta incluye identificador, riesgo, posición, decisión, acción propuesta, versiones de modelo y política y estado de respaldo. Las propuestas se someten a revisión humana.
- La API no cambia el ranking por el orden de llegada de las consultas. La regla del último cupo puede generar un umbral distinto por lote; no se sustituye silenciosamente por 0,5.

## Continuidad del modelado

El champion del PSet 03 es HGB al día 56. Existen ensayos exploratorios de desarrollo para días 14 y 28, con parámetros de los finalistas, que sirven como antecedente. La selección de un corte temprano no significa que esos ensayos sean ya un modelo operativo registrado ni evidencia prospectiva independiente.

Cada versión que produzca asignaciones deberá prepararse y validarse para su corte, conservar la preparación correspondiente y registrar datos, ventana, corte, código y parámetros. Se reutilizará el trabajo válido anterior sin repetir el tuning por defecto. Se preservarán los resultados y versiones históricos del PSet 03.

El proceso reactivo basado en reprobaciones anteriores solo podrá reconstruirse con resultados previos disponibles en el momento de decidir. `num_of_prev_attempts` no demuestra por sí mismo una reprobación previa. Una historia no observable se informará como desconocida.

## Decisiones operativas pendientes

| Decisión | Estado |
|---|---|
| Batch y apoyo durante el período actual | Acordados. |
| Bolsas reactiva vigente y preventiva diferenciadas | Acordadas como diseño. |
| Adelanto desde bolsa reactiva futura | Solicitud propuesta: hasta 30 % de cupos futuros; base y autorización institucional pendientes. |
| Cortes funcionales | Semanas 2 y 4; reparto de cupos y política de asignación pendientes. |
| Unidad, costo y capacidad de atención | Prototipo: matrícula-asignatura y referencia experimental del 10 %; costos, horas y capacidad institucional pendientes. |
| Márgenes de contacto y tutoría | Pendientes; los 21 días del PSet 03 eran ilustrativos. |
| Disponibilidad temporal de etiquetas y datos | Por verificar; no inventar fechas de publicación. |
| Umbrales de monitoreo, promoción y retirada | Por predeclarar antes de observar la simulación final. |

El análisis de FP, la interpretación del 30 % y las condiciones para elegir el reparto se detallan en [cortes y presupuesto](cortes-y-presupuesto.md).
