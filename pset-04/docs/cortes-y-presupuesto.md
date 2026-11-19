# Semanas 2 y 4 y propuesta de adelanto del 30 %

Estado: meta principal confirmada de al menos +10 % relativo en cobertura de Fail frente al estático, a igual cupo. El adelanto del 30 % se conserva como escenario presupuestario. No acredita presupuesto institucional aprobado, capacidad docente ni un nivel de falsos positivos ya garantizado.

## Dos puntos funcionales

- **Semana 2, día 14:** mayor anticipación para contactar e intervenir. El cupo inicial puede ser más restringido si la evidencia de focalización y el costo de priorizar casos sin Fail así lo justifican.
- **Semana 4, día 28:** mayor información disponible y posibilidad de asignar el resto de los cupos, siempre que quede margen de intervención. El plazo debe validarse; los 21 días usados en PSet 03 eran ilustrativos.

Se compararán políticas de una ronda y de dos rondas antes de fijar el reparto. En una política de dos rondas, las asignaciones de semana 2 consumen parte del mismo presupuesto preventivo y no se vuelven a contabilizar en semana 4. Un puntaje actualizado no implica por sí mismo cancelar apoyo ya asignado.

Cada corte que produzca asignaciones necesita un modelo validado para la información disponible en ese momento. El champion histórico del día 56 no se reutiliza como si fuera un modelo temprano. Se deberá definir la carga y trazabilidad de las versiones por corte antes de implementar el servicio.

## Evidencia histórica disponible

Fuente: [políticas exploratorias del PSet 03](../../pset_3/docs/anticipacion/resultados.json), familia HGB. Son predicciones fuera de fold sobre desarrollo, con cohortes elegibles propias de cada corte y un mismo presupuesto basado en día 14; no son resultados de una intervención ni una nueva prueba independiente.

| Corte | Cupos de matrícula | TP: seleccionados con Fail observado | FP: seleccionados con otro resultado | Precisión entre seleccionados | Proporción FP entre seleccionados |
|---|---:|---:|---:|---:|---:|
| Semana 2 | 1.691 | 915 | 776 | 54,11 % | 45,89 % |
| Semana 4 | 1.691 | 1.011 | 680 | 59,79 % | 40,21 % |

En este ensayo, semana 4 tiene 96 FP menos a igual cupo, una reducción relativa del 12,37 % del conteo de FP. La diferencia en la proporción FP es de 5,68 puntos porcentuales. Es evidencia favorable al corte 4 en este desarrollo, sin demostrar que toda cohorte futura o todo aumento de información reducirá los errores. Las cohortes no son idénticas.

La última columna es `FP / (TP + FP)`, equivalente a `1 - precisión`; no es la tasa convencional `FP / (FP + TN)`. Se informarán ambas cuando corresponda, con sus denominadores.

## Qué significa solicitar el 30 %

Se interpreta la propuesta como **solicitar el adelanto de hasta el 30 % de los cupos reactivos previstos para el período posterior**, para apoyo preventivo en el período actual. Si la Universidad define la transferencia en dinero u horas, se registrará esa base y se convertirá explícitamente a capacidad de atención.

- No es 30 % de la matrícula actual ni una tasa máxima de error.
- Si la base futura fuera de 1.000 cupos comparables, el ejemplo de adelanto sería de hasta 300 y dejaría 700 en la reserva futura. El ejemplo no representa capacidad real confirmada.
- El presupuesto reactivo vigente para reprobaciones anteriores permanece separado y protegido.
- Si una atención preventiva requiere más sesiones o tiene otro costo que la reactiva, 300 cupos futuros no financian automáticamente 300 atenciones preventivas. El cálculo debe usar costos y horas disponibles.
- Se registra el saldo futuro incluso si la prevención no reduce la demanda posterior. La evaluación incluirá efectividad cero.

El 30 % limita la exposición de recursos del escenario, pero no garantiza que los FP sean pocos. Para estimarlos es necesario conocer el cupo preventivo resultante y reevaluar el ranking a ese cupo. No se extrapolan los 776 o 680 FP históricos de forma proporcional al 30 %.

## Regla para evaluar la política

Comparar los cortes y, si aplica, sus combinaciones con igual presupuesto total, elegibilidad y unidad de asignación. Reportar:

1. TP, FP y FN; precisión, proporción FP entre seleccionados y cobertura de Fail.
2. Cantidad de atenciones, personas únicas y horas utilizadas; tiempo disponible para intervenir.
3. Costo total preventivo y proporción atribuida a FP históricos como **proxy de focalización**. Ese componente ya forma parte del costo total y no se suma una segunda vez.
4. Saldo reactivo futuro y escenarios de demanda, incluyendo ausencia de efecto preventivo.

Reducir cupos en un ranking fijo puede reducir el número absoluto de FP y también el número de TP atendidos. La elección debe equilibrar focalización, cobertura, oportunidad y costo. El reparto entre semanas y una precisión mínima aceptable quedan por definir con estas comparaciones, antes de observar la simulación final.

La capacidad por persona, matrícula-asignatura u hora sigue pendiente de especificación. Cambiar la unidad exige recalcular los indicadores; los resultados por matrícula anteriores no se convierten directamente en resultados por estudiante.

## Cómo interpretar el recurso empleado

En la simulación retrospectiva, un FP identifica una selección cuyo target observado no es Fail. Permite analizar el costo de focalización, pero no demuestra que la persona careciera de toda necesidad de apoyo.

En un piloto real, una persona que recibe tutoría y aprueba puede ser un éxito de la intervención. Su aprobación no basta para concluir que la tutoría fue innecesaria ni para separar prevención efectiva de una alerta incorrecta. Esa atribución requiere una evaluación causal; se mantendrá separada del monitoreo predictivo y se registrará la exposición a la intervención.
