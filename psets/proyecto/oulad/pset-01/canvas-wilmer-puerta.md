# Canvas de viabilidad y riesgos

Wilmer Puerta · PSet 1 · 12-nov-2026

## Problema y decisión

Universidad hipotética, sin socio comprometido. Focalizar revisión preventiva con capacidad limitada; el resultado inmediato es una lista para el tutor. El coordinador valida cupos, el tutor revisa siempre contexto y decide apoyo. El sistema calcula y ordena, sin sanciones ni contactos reales en el MVP.

## Predicción y éxito

Unidad: matrícula estudiante–módulo–edición. Probabilidades de Fail, Withdrawn y aprobación (Pass + Distinction) al cierre. Cortes: 14, 28, 42 y 56. Población registrada hasta día 0, excluyendo únicamente retiros ya ocurridos al corte. Orden por P(Fail). Regresión logística multinomial y Random Forest, cada uno estático frente al mismo algoritmo enriquecido con actividad longitudinal. Sin notas de evaluaciones.

PR-AUC para Fail (implementación por fijar antes de entrenar), calibración e incertidumbre. Meta provisional: +10 % relativo de TP@K en día 56 frente al baseline estático con igual población y K. K = floor(0.10 × N) por edición y corte, sensibilidad 5 % y 20 %. Umbral: última puntuación admitida, desempate estable por clave sin target. Si TP estático es cero, informar diferencia absoluta. Omitir una futura reprobación se considera el error más costoso por oportunidad perdida; falsas alertas consumen cupos. Costos y capacidad reales por validar.

Comparador adicional: días desde la última actividad hasta corte, descendente. Nunca activos con cobertura comprobada: contar desde día 0; cobertura desconocida: marcar información insuficiente y aplicar política común documentada antes de evaluar. Actividad previa al inicio se conserva y se audita. Las repeticiones consumen cupos y los TP acumulados cuentan una vez por matrícula; informar personas únicas y anticipación al cierre.

## Datos y acceso

| Dato | Fuente | Estado real |
|---|---|---|
| Antecedentes y etiquetas | studentInfo.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Registro y retiro | studentRegistration.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Edición y duración | courses.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Recursos | vle.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Actividad fechada | studentVle.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Capacidad y costos institucionales | Institución participante | No disponibles ni acceso confirmado |
| Oferta, participación y efectos del programa propuesto | Futuro piloto | No existen todavía para esta intervención |

Auditoría local del 12 de noviembre de 2026: 7.052 Fail (21.64 %). 10.156 Withdrawn (31.16 %) y 15.385 aprobaciones (47.20 %). sobre 32.593 matrículas. En la población inicialmente registrada hasta el día 0, 6.980 Fail (21.60 %). 10.068 Withdrawn (31.16 %) y 15.266 aprobaciones (47.24 %). sobre 32.314 matrículas. Son matrículas, no personas únicas ni una tasa institucional actual.

La auditoría descriptiva no prueba cobertura completa ni disponibilidad inicial de todos los antecedentes. Validación con ediciones posteriores compatibles, estudiantes separados y etiquetas históricas maduras antes del corte simulado. Transformaciones aprendidas solo con entrenamiento. No usar target ni fecha futura de retiro como predictor.

## Resultado de negocio y seguimiento

Focalización: TP@K, precisión, recobrado, omisiones, primeras detecciones, anticipación y revisiones repetidas con el mismo presupuesto. Impacto posterior: asignación aleatoria por persona a oferta definida de acompañamiento o atención habitual, estratificada según diseño. Intención de tratar, diferencia absoluta de aprobación e intervalo de confianza. Registrar también Fail, Withdrawn, oferta, contacto, participación, otras ayudas, tiempos y costos. Resolver matrículas múltiples y contaminación; calcular muestra posteriormente según tasa inicial, efecto mínimo, potencia y agrupamiento. No estima efectos individuales ni demuestra superioridad causal de selección longitudinal.

## Riesgos, supuestos, verificación y gravedad



**R1. Mejora insuficiente o poco transferible; alta.** Se rompe el supuesto de aporte longitudinal consistente. Comparar a igual K por edición, con incertidumbre; conservar el baseline o limitar el alcance si no se sostiene.

**R2. Información futura o actividad mal representada; crítica.** Se rompe la disponibilidad y comparabilidad al corte. Auditar fechas, etiquetas, cobertura, claves y transformaciones; reconstruir cualquier evaluación afectada. Medir factibilidad de procesamiento y acotar módulos con criterios previos si hace falta.

**R3. Capacidad inviable o apoyo sin efecto; alta.** Se rompe la viabilidad de revisión e intervención útil. Simular cupos del 5 %, 10 % y 20 %, repeticiones y carga; medir participación y resultados solo en el piloto posterior. No afirmar eficiencia monetaria sin costos.

**R4. Errores desiguales o pérdida de confianza; alta.** Se rompe una priorización aceptable entre grupos. Revisar errores por subgrupos con volumen suficiente y el lenguaje de alertas; ajustar reglas y preservar juicio humano y vías habituales de apoyo.



Referencias: Kuzilek et al. (2017), doi:10.1038/sdata.2017.171; documentación oficial de OULAD; auditoría local en docs/auditoria-datos.md y datasets/manifest.json.
