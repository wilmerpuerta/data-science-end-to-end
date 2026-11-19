# Cambios y decisiones del proyecto final

## Estado de esta etapa

Primer paso: objetivo de negocio acordado y núcleo de priorización implementado. Las pruebas aquí descritas no certifican la API ni la operación integral. La estructura final sigue el árbol de la rúbrica; las carpetas de trabajo y los entregables anteriores se preservan.

## Registro de observaciones y ajustes

| Observación o acuerdo | Cambio y estado | Ubicación |
|---|---|---|
| El ganador debe aportar valor al negocio | La meta es al menos +10 % relativo en cobertura de Fail frente al estático, a igual capacidad. Acordado por el autor en esta continuación. | `README.md`, `api/main.py::evaluar_meta` |
| El estático se había confundido con Dummy o proceso reactivo | Se mantienen tres comparadores distintos: control estático, Dummy y política reactiva. | `README.md` |
| Detección preventiva en semanas 2 y 4 | Los cortes operativos admitidos son días 14 y 28. El modelo de día 56 conserva su papel histórico. | `api/main.py`, preparación de modelos pendiente |
| Adelantar presupuesto futuro | El 30 % queda como escenario; presupuesto reactivo vigente protegido y saldo futuro explícito. No se convierte directamente en cupos sin costos y capacidad docente. | `README.md` |
| No gastar un presupuesto distinto en cada llamada | El núcleo exige el manifiesto completo y aplica un cupo por edición compartido entre rondas. Persistencia e idempotencia concurrente pendientes. | `api/main.py::priorizar_cohorte` |
| Evitar doble conteo | Cada matrícula consume como máximo una reserva; personas únicas se informan aparte. Una propuesta previa no se cancela al cambiar su score. | `api/main.py`, `tests/test_comportamiento.py` |
| Estructura exacta de la entrega | Raíz `proyecto_final/`; reglas de priorización en `api/main.py`, tipos en `api/esquemas.py`; no se añaden carpetas auxiliares al árbol final. | Árbol del proyecto |
| Mantener la preparación del PSet 03 | `src/pipeline.py` se copia sin modificar su contenido. | `src/pipeline.py` |
| Afirmaciones de tutorías y Fail evitados | La simulación mide focalización y propuestas; la efectividad causal de tutorías y el ahorro real siguen sin observarse. | `README.md`, `api/main.py::evaluar_meta` |
| Memorias, entregables y rutas de PSet 02/03 | Se preservan `pset_2/` y `pset_3/` y sus versiones históricas; su integración en el árbol final es el siguiente paso. | Integración pendiente |

## Supuestos explícitos del prototipo

- Unidad: matrícula-asignatura. Personas únicas se reportan por separado; no se equiparan a sesiones u horas.
- Capacidad de referencia: `floor(0.10 × elegibles_día14)` por edición. Es experimental, no presupuesto aprobado.
- Reparto de prueba: 25 % en semana 2 y el resto en semana 4. La regla permite otros repartos; aún no hay uno seleccionado para producción.
- Reserva: una tutoría propuesta consume cupo hasta una revisión humana explícita. Este paso no implementa liberación de cupos por rechazo.
- Empates: riesgo descendente, matrícula ascendente. No se usa el target para priorizar.
- Elegibilidad: el manifiesto de cada corte debe ser un subconjunto coherente de la base y provenir del servidor. No se puede inventar una cohorte desde el cliente para aumentar cupos.
- La métrica comparativa usa un mismo denominador de Fail de la cohorte base y una misma capacidad para estático y longitudinal. La política de dos rondas se comparará como un todo.

## Evidencia de desarrollo reutilizada

La comparación siguiente procede de las predicciones fuera de fold ya obtenidas en PSet 03. Cada comparación estático/longitudinal usa su misma población de corte. No son datos futuros independientes ni resultados de una intervención. La media de cobertura se calcula sobre los cinco folds; no se confunde con la métrica agregada de las políticas.

| Modelo | Corte | Cobertura estática media | Cobertura longitudinal media | Mejora relativa |
|---|---:|---:|---:|---:|
| HGB | 14 | 15,3581 % | 18,6278 % | +21,2897 % |
| HGB | 28 | 15,4396 % | 20,1457 % | +30,4801 % |
| Logística | 14 | 15,9718 % | 18,6841 % | +16,9815 % |
| Logística | 28 | 15,8509 % | 20,2085 % | +27,4914 % |

Esta evidencia apoya la viabilidad de estudiar la meta del 10 %, pero no la garantiza en la simulación final. HGB y logística presentan diferencias pequeñas en cobertura; no se selecciona un modelo temprano por observar el resultado de la prueba reutilizada.

Identificadores para trazabilidad:

- Snapshot: `0a75615bd8ff6b166d366cf78c8303845852cbeb23387ac24a64fe4962f01027`.
- Plan temprano: `7deb66f98a2443a6406d48d4fe62ed8d7e219ec82a63ecce251327b2265e93f9`.
- HGB día 14: estático `096e4f590ff04551b5d8fa3d196713a7`; longitudinal `a6c0b65d4e354ceaabfc565c88bfa0c2`.
- HGB día 28: estático `6e0b3d2b12cf481eb45221c7349b3dcb`; longitudinal `048df6920ba747d28d957b052e685666`.
- La población de desarrollo contiene 17.246 matrículas en día 14 y 16.838 en día 28, con 15 ediciones. Se purgan los estudiantes presentes en 2014J; solo se usan etiquetas de desarrollo.
- Los modelos completos de esos experimentos ya están guardados como artefactos `pipeline` en MLflow. Aún no se han preparado versiones operativas ni fixtures del PSet 04.

Se exploraron veinte escenarios de dos rondas con las predicciones OOF existentes. Sus rankings se evaluaron dentro de edición y fold y comparten un presupuesto calculado en día 14. Ese procedimiento usa otro redondeo que una edición completa en producción; no se transfieren sus cupos numéricos directamente a la API. No se ha seleccionado un reparto ni se ha vuelto a entrenar.

## Validación del primer paso

`PYTHONPATH=proyecto_final uv run --python 3.11 --no-project --with pytest==8.3.5 python -m pytest -q proyecto_final/tests/test_comportamiento.py`: **15 casos aprobados**.

Se verifican orden y empates, presupuesto compartido, no repetición, conservación de reservas ante cambios de elegibilidad, rechazo de lotes incompletos/duplicados, separación entre ediciones, personas frente a matrículas, probabilidades inválidas, cortes y estados inconsistentes, y definición exacta de la meta relativa. Las pruebas usan datos sintéticos. No son pruebas de HTTP, validación Pydantic, carga por alias, persistencia, concurrencia ni entrenamiento.

No se crearon nuevas corridas MLflow ni se hicieron llamadas a OpenAI o a Snowflake. No se promovió ni cambió ningún modelo.

## Pendientes antes de la simulación final

1. Integrar ingesta, dbt, Spark y los notebooks en sus ubicaciones definitivas, con trazabilidad de las fuentes.
2. Verificar y preparar modelos por corte, la fixture exportada con `mlflow.sklearn.save_model` y la muestra de CI con una referencia compatible.
3. Implementar FastAPI, Pydantic, carga por alias, persistencia de predicciones y transacciones de cupos, idempotencia, respaldo y tres endpoints.
4. Seleccionar el reparto usando desarrollo y congelar política, comparadores, umbrales y escenarios antes de la simulación final.
5. Resolver ocho lotes sucesivos con la temporalidad disponible. Los datos contienen pocas presentaciones académicas; no se inventan ocho semestres ni se cuentan fragmentos de una cohorte como períodos independientes. La maduración y publicación de etiquetas requieren supuestos explícitos si no están documentadas.
6. Preparar Compose único, CI/CD efectivos en la raíz real del repositorio, monitoreo, alertas y ciclo de reentrenamiento con pausa de aprobación humana.
7. Completar evidencia CSV, subgrupos, rollback, interruptor, comunicación y video.

SHA-256 de la preparación reutilizada: `2e45d564d37ff34de666adaa09c5d440cd61f7c7c16378ea354cf9cbbd3e10be`.

## Criterios de implementación y prioridades

El autor aclaró el 19-nov-2026 que la referencia de los laboratorios es opcional. Se priorizarán sus patrones cuando encajen con la lógica del proyecto y ayuden a obtener el resultado buscado; en los demás casos se aplicará el criterio técnico y de negocio desarrollado para OULAD. No se modificará una solución válida solo para imitar un estilo.

Las decisiones se fundamentarán en los requisitos de la rúbrica, la evidencia, la prevención de fuga, la reproducibilidad y las necesidades operativas. Los parámetros, ventanas, alias y configuraciones se justificarán por su función y validación en este proyecto. La preparación, los cupos compartidos, la meta del 10 % y la supervisión humana conservan sus propios fundamentos de negocio y evaluación.

La prioridad es completar `proyecto_final/`. Resolver los `TODO` de las referencias queda para una solicitud posterior del autor, si el avance del proyecto lo permite. La carpeta local `laboratorios/` permanece excluida de Git y no es una dependencia del proyecto final.
