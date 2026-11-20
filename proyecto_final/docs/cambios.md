# Cambios y decisiones del proyecto final

## Estado de esta etapa

Estado actual: API batch, Snowflake, ocho despachos por escenario, monitoreo y challenger comparado. El challenger fue rechazado por decisión humana y Kestra terminó en SUCCESS; la integración y la comunicación finales siguen pendientes. Las secciones iniciales conservan el registro histórico; el estado vigente se detalla al final. La estructura final sigue el árbol de la rúbrica; las carpetas de trabajo y los entregables anteriores se preservan.

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

## Integración operativa y lotes de control — 19-nov-2026

- Fuente de continuidad del PSet 02: `pset_2/`. `pset-02/` no se utiliza en el nuevo desarrollo ni como dependencia de ejecución. Las fuentes de dbt y Spark incorporadas se verificaron contra `pset_2/`; los servicios finales usan rutas de `proyecto_final/`.
- `src/datos.py` incorpora el contrato separado `PSET2_OULAD.ANALYTICS`, carga inmutable, conciliación de identificadores y contenido, plan de lotes y reloj monotónico. Las capas históricas permanecen como fuentes de lectura.
- Protocolo predeclarado `control-retrospectivo-1`: se reutiliza 2014J, el holdout ya examinado en PSet 03, sin afirmar validación prospectiva nueva. Siete módulos se ordenan y distribuyen circularmente en cuatro ondas de ediciones completas. Hay despachos en días relativos simulados 14, 15, 16, 17, 28, 29, 30 y 31. Las features se congelan en los cortes 14/28; la demora de 0..3 días representa una cola operativa supuesta. No son ocho semestres independientes ni ocho poblaciones independientes. Cada edición pertenece a una única onda y conserva un solo presupuesto entre cortes; no se fragmenta para aumentar cupos.
- El calendario absoluto y la fecha real de publicación de resultados no están disponibles. Se supone explícitamente disponibilidad del target al fin del módulo +14 días; se filtra en Snowflake antes de extraerlo. El reloj simulado se registra aparte del timestamp real de inferencia. No se incorporan etiquetas a las solicitudes de la API.
- Estos ocho lotes son controles originales. La deriva inducida, monitoreo, comparación con el estático, evaluación presupuestaria y ciclo de reentrenamiento se desarrollan en bloques posteriores; no se declara alcanzada la meta de +10 % ni ahorro o tutorías efectivamente realizadas.
- `kestra/produccion_lotes.yml` ejecuta los lotes secuencialmente con reintentos y carga periódica desde el registro durable. Las tablas y los volúmenes finales tienen identificación propia; se reutiliza ANALYTICS sin modificar OBT_FEATURES. La API no recibe credenciales Snowflake; solo Kestra las monta como archivos privados. El target se libera únicamente al solicitarlo en el flujo, tras las ocho predicciones.

Evidencia del bloque: ejecución Kestra `59E27va9JE8WDXxidPfqbp` en SUCCESS, ocho lotes y 18.323 predicciones únicas conciliadas. El primer lote necesitó un reintento tras ajustar el contrato a claves Gold con `|`; el resultado y sus intentos se conservan. El día simulado 31 no consulta etiquetas; se rechazó una modificación intencional de un registro publicado y se mantuvieron las 18.323 claves. `docs/predicciones.csv` exporta únicamente este plan, sin los ejemplos sintéticos. Las 43 pruebas completas pasaron localmente y dentro del contenedor.

| Lote | Día simulado | Corte | Matrículas | Propuestas nuevas |
|---|---:|---:|---:|---:|
| L01 | 14 | 14 | 1369 | 33 |
| L02 | 15 | 14 | 3637 | 90 |
| L03 | 16 | 14 | 2750 | 67 |
| L04 | 17 | 14 | 1475 | 36 |
| L05 | 28 | 28 | 1359 | 103 |
| L06 | 29 | 28 | 3590 | 273 |
| L07 | 30 | 28 | 2684 | 207 |
| L08 | 31 | 28 | 1459 | 111 |

La repetición integral `4zb5Bywcxv9fxfy8mWGFq1` terminó en SUCCESS sin repuntuar ni agregar claves. Tras verificar cero etiquetas en día 31, el avance explícito al día 283 materializó 9.231 resultados maduros. Hay 226 propuestas nuevas en semana 2 y 694 en semana 4, 920 en total; son propuestas bajo cupos experimentales, no tutorías realizadas. El CSV conserva 18.323 filas, sin target.


## Monitoreo, deriva y tablero — 19-nov-2026

El protocolo y la referencia se congelaron en `0e14162` antes de evaluar lotes; referencia `f37f5bbfd21227a448d68ab0dbaf8fb457bf5cc18798482874a67682bedfbf1b`. No hubo entrenamiento, tuning, llamadas LLM ni cambio de alias. Se conservó byte a byte `src/pipeline.py` y el control original.

- `monitoreo/deriva.py`: perfiles de entrenamiento por corte y módulos de la onda, CV histórica OOF, PSI, KS, chi-cuadrado, calidad, métricas de sistema y desempeño, escritura inmutable en Snowflake, exportación y tablero Streamlit. El tablero distingue escenarios, disponibilidad de etiquetas, AP/umbral, TP/FP, cobertura y personas, datos, errores, alertas y versiones; indica que todavía no hay reentrenamientos registrados.
- `monitoreo/alertas.py`: umbrales, ventanas, severidad, receptores y acciones; diagnóstico de cambios de datos y desempeño; propuesta de reentrenamiento solo por caída persistente, nunca por PSI solo. Media menos dos desviaciones es una regla operativa, no un intervalo estadístico.
- `kestra/monitoreo.yml` y `kestra/produccion_lotes.yml`: llamada después de cada lote y revisión posterior a la maduración, ordenada por llegada de etiquetas. Las alertas se muestran en logs; no se envían correos ni Slack.
- `src/datos.py` y `api/main.py`: escenario separado, cabeceras de atribución operativa y migración aditiva de telemetría, conservando registros previos; exportación de los dos planes. Los errores históricos no atribuibles se muestran como desconocidos. Las cabeceras no gobiernan cupos ni autorizaciones.
- `docker-compose.yml`, `api/Dockerfile`, `.env.example`, `requirements.txt`: API sintética separada, worker de monitoreo y tablero. Dependencias con hashes, mismas versiones científicas; Pillow se ajustó a la compatibilidad de Streamlit. Solo Kestra y el worker montan claves Snowflake. La API y el tablero no reciben esos archivos.

La inducción `permutacion-creditos-1` altera L06 y L07 del plan `oulad-2014j-deriva-v1`: permuta vectores completos de features dentro de edición con semilla `5041+orden` y suma 120 créditos. No utiliza ni cambia targets, IDs ni cupos; L01-L05 y L08 conservan entradas. El escenario usa otro SQLite y presupuestos separados. Sus demografías alteradas no se usan como datos reales de equidad.

Ejecución Kestra `2Zi1Y8NiKtYUv3BTtNLR7r` en SUCCESS: ocho lotes, sus revisiones inmediatas y revisión madura. Snowflake conserva 36.646 predicciones únicas, 32 eventos de monitoreo y 28 alertas: 12 en control y 16 en escenario sintético, contando avisos en cada fase. `docs/predicciones.csv`, `docs/monitoreo.csv` y `docs/alertas.csv` reproducen ese alcance. Los 16 eventos de predicción tienen AP vacía; las etiquetas se filtran por el día de revisión, aun si ya se materializaron resultados futuros.

| Lote, semana 4 | Cupos nuevos | TP control | TP sintético | AP control | AP sintética |
|---|---:|---:|---:|---:|---:|
| L06 | 273 | 122 | 55 | 0,3954 | 0,2126 |
| L07 | 207 | 79 | 43 | 0,3310 | 0,2310 |

Los controles L02/L03 y L06/L07 ya muestran caídas frente a la CV condicional; son señales de generalización histórica que requieren revisar prevalencia y composición. No se adjudican al cambio sintético. Los controles L07/L08 tienen avisos PSI cercanos a 0,26; L08 no cae bajo el umbral AP y no propone entrenamiento. No se afirma una tasa cero de falsas alarmas ni que un control sea estacionario. Se conserva el umbral predeclarado y se propone calibrar persistencia y costo de avisos sobre datos futuros, sin retocar el criterio tras observar el benchmark.

51 pruebas completas aprobaron localmente y dentro de Docker; la prueba del tablero con AppTest verificó ambos escenarios sin excepciones. Un bloqueo de lectura de cachés del entorno local se resolvió reinstalando las dependencias fijadas con copias completas; no cambió la fuente ni el entrenamiento. El Compose final aún debe incorporar Spark y MLflow; reentrenamiento, aprobación humana, CD/GHCR, comparación con el estático, equidad y comunicación siguen pendientes.


## Reentrenamiento — protocolo previo a la comparación (19-nov-2026)

Se congela `reentrenamiento-1` antes de ajustar el challenger. La ventana une el histórico de desarrollo purgado del PSet 03 y las matrículas recientes etiquetadas de semana 4 del plan de deriva, con igual peso y una fila por matrícula. Se reserva L08, el último lote etiquetado de ese corte por día de predicción; su cohorte completa, personas y contrapartes de otros cortes/escenarios quedan fuera del entrenamiento.

La política de cupos se comparte desde `api/esquemas.py` entre servicio y evaluación, con reexportación compatible en `api/main.py`; se evita abrir la aplicación al evaluar. `src/pipeline.py` permanece idéntico. Se clona el pipeline completo del champion y se conservan sus hiperparámetros, sin tuning nuevo. La variación de referencia se obtiene de las predicciones OOF históricas de ambos cortes con el presupuesto compartido 25/75, condicionada al módulo de comparación. La sigma de cobertura DDD es 0,016598013644254363; es dispersión entre cinco folds, no un intervalo de confianza.

Champion y challenger comparten el presupuesto y las propuestas de semana 2 ya registradas. La promoción requiere que la ganancia de cobertura supere estrictamente una sigma de esa política y una decisión humana posterior a la comparación. El predictor estático usa su propia política de dos rondas a igual cupo; se reporta por separado la meta de +10 % relativo. Los datos de comparación pertenecen a un benchmark ya inspeccionado y no se presentan como validación prospectiva nueva. La disponibilidad del histórico es un supuesto heredado de la simulación; no se reconstruyen fechas reales de publicación.

La alerta madura del escenario solicita `kestra/reentrenamiento.yml` de forma idempotente. El flujo prepara y registra el challenger y se detiene en `aprobacion`, sin duración de reanudación automática. El worker verificará el estado y los inputs reales de la pausa en Kestra antes de aceptar una decisión. Un candidato que no cumpla la regla no puede promoverse aun si se intenta aprobarlo. El despliegue continuo de código/GHCR se mantiene como bloque posterior independiente de la aprobación del modelo.


## Resultado del reentrenamiento y pausa humana (19-nov-2026)

La alerta persistente madura de L07 solicitó automáticamente el ciclo a través del monitor (`7S73IBhts7SFxtS88K5Lys`, SUCCESS). El flujo `6lcaE9ak8kGv4myx06ZMMw` terminó `preparar_y_comparar` y quedó PAUSED en `aprobacion`, sin reanudación por tiempo. La comparación y la propuesta están listas para revisión; no se ha registrado aprobación ni rechazo y ningún alias champion se ha movido.

La ventana contiene **24.376 filas**: 16.838 históricas de desarrollo y 7.538 recientes maduras de semana 4 del escenario sintético. Se excluyeron todas las 1.475 personas y matrículas de la cohorte reservada L08; el solapamiento por persona es cero. Las 95 filas recientes adicionales que no entran corresponden a personas de la reserva presentes en otras ediciones, y se excluyen por identidad, además de excluir el propio lote. No se duplica el control como entrenamiento independiente. La comparación usa 1.459 matrículas todavía elegibles en semana 4, con etiquetas sobre la base completa de 1.475 de semana 2 (363 Fail); conserva las 36 propuestas anteriores y utiliza 111 cupos nuevos, 147 acumulados por modelo. La política estática utiliza sus propias dos rondas y los mismos 147 cupos.

| Política sobre L08 | Cupos acumulados | Fail focalizados (TP) | No-Fail focalizados (FP) | Cobertura Fail | Precisión al cupo |
|---|---:|---:|---:|---:|---:|
| Estática | 147 | 54 | 93 | 14,8760 % | 36,7347 % |
| Champion vigente | 147 | 77 | 70 | 21,2121 % | 52,3810 % |
| Challenger reentrenado | 147 | 81 | 66 | 22,3140 % | 55,1020 % |

El incremento de cobertura es **1,1019 puntos porcentuales**, inferior a la sigma OOF predeclarada de **1,6598 puntos**. Se necesitan al menos siete TP adicionales para superarla estrictamente; se obtuvieron cuatro. **El candidato no es elegible para promoción; se recomienda rechazarlo y conservar la versión 1.** Su AP de semana 4 es 0,432826 frente a 0,433943 del champion; la regla principal usa valor de negocio, no selecciona automáticamente la mayor AP. Las mejoras relativas frente al estático son +42,59 % para el champion y +50 % para el candidato: ambas superan el objetivo +10 % en esta reserva, pero no sustituyen la comparación de promoción ni certifican el objetivo global del proyecto.

Se ajustaron cinco folds agrupados por persona y un modelo final con el pipeline y los hiperparámetros del champion, sin tuning. Las métricas CV nuevas de cobertura son single-cut al 10 % y están etiquetadas con ese alcance; **no** se usan como sigma de promoción. Esta última procede de los cinco folds históricos de la política completa de dos rondas para DDD. Se conserva `src/pipeline.py` byte a byte. La simulación incluye datos inducidos y un benchmark 2014J previamente inspeccionado; esta reserva está fuera del entrenamiento de ambos modelos, pero no constituye una validación prospectiva nueva. La disponibilidad histórica se asume en el reloj simulado; no se conocen fechas institucionales reales de publicación.

Trazabilidad: run `e0ca46ddc9a84d7eaeffa750633ee2ce`, tag `fase=reentrenamiento`, snapshot `ea52a9dc409630ab68d7154c12f7297d30903002755b2d888aeb1a2f7d7dafa5`, código de entrenamiento `6bb0d12`, referencia `1fc18b7cfd16bc54784995c4d2b90455331e32266452ee6cd6b01520e30c73e9`. Registry: `oulad-apoyo-academico-semana4-modelo@challenger` versión 2, `@champion` versión 1. El champion de semana 2 y el histórico de día 56 permanecen intactos. `docs/reentrenamientos.csv` exporta dos eventos inmutables (SOLICITADO/COMPARADO), con decisión y responsable vacíos; `docs/corridas.csv` conserva 384 runs, incluidos preparación y fallos históricos.

La primera tarea necesitó cuatro intentos en la misma ejecución: se corrigieron manifiestos ausentes en la imagen y tipos booleano/número al persistir la ventana Parquet. Se preserva el historial de errores y reinicios. Esos errores ocurrieron antes del ajuste/logging y se obtuvo un solo run de reentrenamiento de este ciclo; no se repitió el ajuste para seleccionar resultados. La prueba de ventana incluye lectura y escritura Parquet para cubrir el fallo de tipos. **57 pruebas** aprobaron localmente y en Linux/Docker.

No se ha ejecutado el paso de decisión. La rúbrica 7.2 exige «deténgase en una tarea en pausa hasta que una persona la apruebe o la rechace». La autorización general para comandos permite preparar esta comparación, pero la decisión sobre este candidato corresponde al responsable humano una vez revisado el resultado. Si se rechaza, se registrará el motivo y el champion quedará intacto. Una aprobación no elegible quedaría bloqueada por la regla. La demostración posterior de promoción/rollback debe estar identificada como prueba mecánica y no convertir este candidato en una mejora validada. CD/GHCR, Compose único, notebooks, subgrupos, escenarios presupuestarios y comunicación siguen pendientes.


## Cierre del ciclo: rechazo humano registrado (19-nov-2026)

Wilmer Puerta confirmó expresamente: «Estoy de acuerdo en rechazar por no alcanzar la métrica definida para el reemplazo». Se reanudó la pausa real de Kestra con `decision=rechazar`, `responsable=Wilmer Puerta` y el motivo: «Se rechaza el challenger por no alcanzar la métrica definida para el reemplazo: añade 4 TP, frente a los 7 mínimos exigidos, con los mismos 147 cupos. Se conserva el champion vigente».

La ejecución `6lcaE9ak8kGv4myx06ZMMw` terminó **SUCCESS**: preparación/comparación SUCCESS, pausa reanudada SUCCESS y aplicación de decisión SUCCESS. El worker contrastó los inputs de la pausa contra la ejecución antes de registrar la decisión. El instante de reanudación guardado por Kestra es `2026-11-20T01:35:27.018796918` (UTC; 19-nov en Ecuador), y la solicitud se registró a `2026-11-20T01:35:42.637866+00:00`. El campo de usuario técnico de Kestra queda nulo en esta respuesta de la edición instalada; la responsabilidad de negocio se conserva explícitamente en `responsable` y la confirmación del usuario está respaldada de forma privada.

El ciclo queda **RECHAZADO**, el champion de semana 4 permanece en **versión 1**, y la versión 2 conserva su alias challenger y el tag `estado_aprobacion=rechazado`. Se actualizó ese mismo tag en el run `e0ca46ddc9a84d7eaeffa750633ee2ce`. Los champions de semana 2 y día 56 permanecen intactos. No se entrenó otro modelo, no se repitió tuning y no se reconstruyó la imagen para aplicar esta decisión.

`docs/reentrenamientos.csv` exporta cuatro eventos: SOLICITADO, COMPARADO, DECISION_SOLICITADA y DECIDIDO; el último incluye estado RECHAZADO, responsable, motivo y evidencia de reanudación. `docs/corridas.csv` conserva 384 runs y refleja el tag del rechazo. La API y el tablero mantienen el modelo activo y muestran la decisión exportada. El respaldo privado preserva tanto la pausa anterior como el cierre, el Registry, la ventana de entrenamiento, el modelo y las particiones.

Este cierre demuestra el camino de **rechazo con supervisión humana** de la rúbrica 7.2. La demostración controlada de promoción/rollback, el CD/GHCR y los restantes bloques del proyecto siguen pendientes. No se promueve un candidato insuficiente para producir artificialmente evidencia de reemplazo.
