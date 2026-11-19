# Cambios y decisiones del proyecto final

## Estado de esta etapa

Estado actual: API batch y modelos tempranos verificados; dbt, Spark y tres memos incorporados. La operación integral, la carga a Snowflake y la simulación final siguen pendientes. Las secciones iniciales conservan el registro del primer paso; el estado del servicio se detalla al final. La estructura final sigue el árbol de la rúbrica; las carpetas de trabajo y los entregables anteriores se preservan.

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
- Los modelos completos de esos experimentos ya están guardados como artefactos `pipeline` en MLflow. Esos artefactos se reutilizan ahora como versiones experimentales por corte y fixtures; ver el bloque de servicio.

Se exploraron veinte escenarios de dos rondas con las predicciones OOF existentes. Sus rankings se evaluaron dentro de edición y fold y comparten un presupuesto calculado en día 14. Ese procedimiento usa otro redondeo que una edición completa en producción; no se transfieren sus cupos numéricos directamente a la API. No se ha seleccionado un reparto ni se ha vuelto a entrenar.

## Validación del primer paso

`PYTHONPATH=proyecto_final uv run --python 3.11 --no-project --with pytest==8.3.5 python -m pytest -q proyecto_final/tests/test_comportamiento.py`: **15 casos aprobados**.

Se verifican orden y empates, presupuesto compartido, no repetición, conservación de reservas ante cambios de elegibilidad, rechazo de lotes incompletos/duplicados, separación entre ediciones, personas frente a matrículas, probabilidades inválidas, cortes y estados inconsistentes, y definición exacta de la meta relativa. Las pruebas usan datos sintéticos. No son pruebas de HTTP, validación Pydantic, carga por alias, persistencia, concurrencia ni entrenamiento.

No se crearon nuevas corridas MLflow ni se hicieron llamadas a OpenAI o a Snowflake. No se promovió ni cambió ningún modelo.

## Pendientes antes de la simulación final

1. Integrar ingesta, dbt, Spark y los notebooks en sus ubicaciones definitivas, con trazabilidad de las fuentes.
2. Mantener las versiones por corte y las fixtures ya preparadas; extender la evaluación a la simulación temporal.
3. Integrar el registro durable de la API con Snowflake/Kestra. FastAPI, Pydantic, alias, persistencia local, transacciones, idempotencia y respaldo ya están implementados.
4. Seleccionar el reparto usando desarrollo y congelar política, comparadores, umbrales y escenarios antes de la simulación final.
5. Resolver ocho lotes sucesivos con la temporalidad disponible. Los datos contienen pocas presentaciones académicas; no se inventan ocho semestres ni se cuentan fragmentos de una cohorte como períodos independientes. La maduración y publicación de etiquetas requieren supuestos explícitos si no están documentadas.
6. Preparar Compose único, CI/CD efectivos en la raíz real del repositorio, monitoreo, alertas y ciclo de reentrenamiento con pausa de aprobación humana.
7. Completar evidencia CSV, subgrupos, rollback, interruptor, comunicación y video.

SHA-256 de la preparación reutilizada: `2e45d564d37ff34de666adaa09c5d440cd61f7c7c16378ea354cf9cbbd3e10be`.

## Criterios de implementación y prioridades

El autor aclaró el 19-nov-2026 que la referencia de los laboratorios es opcional. Se priorizarán sus patrones cuando encajen con la lógica del proyecto y ayuden a obtener el resultado buscado; en los demás casos se aplicará el criterio técnico y de negocio desarrollado para OULAD. No se modificará una solución válida solo para imitar un estilo.

Las decisiones se fundamentarán en los requisitos de la rúbrica, la evidencia, la prevención de fuga, la reproducibilidad y las necesidades operativas. Los parámetros, ventanas, alias y configuraciones se justificarán por su función y validación en este proyecto. La preparación, los cupos compartidos, la meta del 10 % y la supervisión humana conservan sus propios fundamentos de negocio y evaluación.

La prioridad es completar `proyecto_final/`. Resolver los `TODO` de las referencias queda para una solicitud posterior del autor, si el avance del proyecto lo permite. La carpeta local `laboratorios/` permanece excluida de Git y no es una dependencia del proyecto final.

## Servicio batch, modelos y CI: 19-nov-2026

### Implementación y alcance

- `api/main.py` expone `/salud`, `/modelo`, `/predecir` y `/metricas`. La entrada incluye cohorte, corte, identificadores y veinte features; el modelo recibe solo las features. `api/esquemas.py` valida tipos, rangos, categorías, coherencia y ausencia de campos extra. La validación devuelve 422 con campo/tipo/mensaje y omite valores inválidos de la respuesta, incluidos NaN.
- `src/datos.py` valida bundles y prepara muestras de desarrollo. Su almacén SQLite usa transacciones de escritura, un manifiesto confiable, una sola decisión por cohorte/corte y una reserva compartida. El mismo contenido con otro nombre no renueva el presupuesto. Los datos quedan en `.local/`, excluida de Git.
- El registro guarda timestamp, features sin target, resultado, ID, modelo, versión, run_id, snapshot, split, referencia Gold y latencia. Repetir una solicitud no inserta más filas ni repuntúa. Un cambio de contenido de un corte procesado devuelve 409. Las propuestas y conteos de una respuesta repetida describen la decisión ya guardada; no son un gasto nuevo.
- Los registros son un outbox durable. Todavía no se ha implementado su carga a Snowflake PREDICCIONES; no se presenta la demostración como una ejecución de producción ni como el flujo de ocho lotes.
- `dbt/` y `spark/` incorporan 92 archivos de la entrega PSet 02, conservados sin alteraciones. Los tres memos canónicos anteriores se copiaron a `docs/historial/`. El pitch en PDF, la ingesta integrada y los notebooks 01-07 siguen pendientes.
- `docker-compose.yml` levanta la API en `127.0.0.1:8004`, conectada al Registry existente. `.dockerignore` y las copias explícitas del Dockerfile excluyen datos, entornos y secretos. La unificación de los cinco servicios finales se realizará en el bloque de orquestación.

### Modelos y referencia de CI

Se registraron `oulad-apoyo-academico-semana2-modelo@champion` y `oulad-apoyo-academico-semana4-modelo@champion`, versión 1. Proceden de los runs tempranos longitudinales ya identificados arriba. No se modificó el champion histórico del día 56 ni se repitieron entrenamiento o tuning. Su uso experimental conserva la familia del champion anterior; las pequeñas diferencias entre familias tempranas no se presentan como una superioridad estable o una validación prospectiva.

Las fixtures se guardaron con `mlflow.sklearn.save_model`, firma y `predict_proba`. Se publican tres modelos pequeños —dos tempranos y el baseline— y dos muestras fijas de desarrollo, 60 observaciones por corte y sin identificadores originales. Los hashes, las métricas y la procedencia están en `tests/fixtures/referencia.json`. Solo esos `model.pkl` se permiten en Git; los modelos privados restantes siguen excluidos.

La AP de la muestra fija se registra en el experimento `oulad-apoyo-academico-operacion`, con `fase=preparacion_servicio`, fuente de código real y `new_training=false`. Es una referencia de reproducción sobre desarrollo estratificado, no la media CV ni la métrica de una prueba independiente. La tolerancia `1e-10` se aplica a probabilidades y AP calculadas sobre la misma muestra. La API consulta el alias al procesar un lote nuevo y fija esa versión para todo el lote; la respuesta repetida conserva la versión con que se procesó originalmente.

### Evidencia comprobada

| Comprobación | Resultado |
|---|---|
| Pruebas completas del proyecto | 35 casos aprobados: contrato, preparación/fixtures, respaldo y dominio |
| Pruebas dentro de la imagen | 35 casos aprobados sin servidor MLflow ni Snowflake |
| Carga real en Docker | Los dos modelos cargan desde el Registry; `/salud` informa `modelo_cargado=true` |
| Ejemplo de dos rondas | 40 matrículas sintéticas, 1 propuesta en semana 2 y 3 adicionales en semana 4 |
| Persistencia y repetición | 80 predicciones guardadas; la repetición conserva respuesta e IDs; una entrada incompleta recibe 422 |
| Versión y rollback | API observó 1→2→1 con la misma imagen y el mismo contenedor; alias final de semana 2 volvió a 1 |
| Alcance de versión 2 | Duplicado de los mismos pesos para probar la recarga; etiquetado `recarga_mismo_artefacto`, sin entrenamiento ni mejora atribuida |
| Interruptor | `PSET4_FORCE_FALLBACK=1` sirvió el Dummy en una cohorte sintética nueva; al quitarlo volvió la carga normal sin reconstruir la imagen |
| Respaldo trazable | Run original `dcb91965644a479baa7a0f08555df32e`, estrategia `most_frequent`, score de Fail 0 y selección por cupo/desempate; su split de entrenamiento se conserva |

Los avisos de deprecación observados proceden de dependencias fijadas; las comprobaciones funcionales pasan. Las latencias de la demostración se basan en pocas peticiones sintéticas y no constituyen un SLO ni una prueba de carga. No se enviaron datos a OpenAI ni se escribieron datos en Snowflake.

### CI y próximos bloques

El workflow canónico está en `.github/workflows/ci.yml` de `proyecto_final/`. Se mantiene idéntico en la raíz Git de trabajo y en la raíz del fork publicado para que GitHub lo ejecute en push/PR. Instala la resolución con hashes, ejecuta las pruebas offline, construye la imagen y prueba dentro de ella. La comprobación general del repositorio mantiene las pruebas portables; el job dedicado usa las versiones del modelo y `PSET4_FULL_TESTS=1`.

Pendientes: carga/orquestación Snowflake/Kestra, Compose único completo, lotes/etiquetas diferidas, monitoreo de datos/modelo, alertas, tablero, reentrenamiento y aprobación humana, CD/GHCR, subgrupos, CSV de simulación, documentos y video. El rollback mecánico no sustituye la comparación y decisión de un challenger reentrenado. El reparto 25/75 permanece provisional.
