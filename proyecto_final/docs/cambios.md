# Cambios y decisiones del proyecto final

## Estado de esta etapa

Estado actual: integración completa verificada con nueve servicios saludables, 84 pruebas, ingesta fuente→OBT, Registry propio y evidencias operativas conservadas. Memo técnico de 12 páginas, presentación de 12 diapositivas, anexos y guion de 6:35 preparados para revisión. Los siete notebooks están ejecutados con salidas y PSet1 conciliado. Quedan pitch histórico en PDF y grabar/publicar el video e insertar su URL. Las entradas anteriores se conservan como registro cronológico; el estado vigente se detalla al final.

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


## Despliegue continuo — configuración preparada (19-nov-2026)

Se incorpora `cd.yml` canónico y efectivo en la raíz GitHub, con `push` a `main`, CI reutilizable obligatorio, permisos `packages:write` limitados al job de publicación y autenticación mediante `GITHUB_TOKEN`. La imagen lleva el SHA completo como tag y las etiquetas OCI de repositorio/revisión; se prueban las fixtures dentro del artefacto exacto antes de publicarlo. El digest se conserva en el resumen y en un artefacto JSON. El build utiliza la lista de archivos permitidos de `.dockerignore`, sin credenciales ni datos privados.

Compose exige una referencia explícita en `PSET4_API_IMAGE`; API, escenario sintético, worker y tablero consumen la misma imagen. Kestra continúa con su imagen local. La ejecución y descarga GHCR, la actualización del servicio y la evidencia de rollback se comprobarán antes de declarar el bloque completado. No se cambia ningún alias del modelo en el workflow de publicación.


## CD/GHCR y rollback técnico verificados (19-nov-2026)

El [PR #1](https://github.com/wilmerpuerta/data-science-end-to-end/pull/1) aprobó CI y se integró a `main` en `97e9a18003554e1d0de5287fb87c0f23812557f5`. Se preservan íntegros `master` y su historia; `master` permanece como rama predeterminada del repositorio del curso y `main` contiene la integración de despliegue. Los workflows efectivos están en la raíz real GitHub y coinciden con los canónicos de entrega. El [workflow CD](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44660981181) ejecutó CI como dependencia y probó la imagen exacta antes de publicarla; el login usó `GITHUB_TOKEN`, sin agregar credenciales al repositorio.

Imagen publicada por commit: `ghcr.io/wilmerpuerta/oulad-proyecto-final-api:97e9a18003554e1d0de5287fb87c0f23812557f5`. Digest comprobado y configurado en los cuatro servicios: `ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:bc5ff9e0b215795b3388bc4da526ea6bece369404f8ed2c7b4a24d6fda16cae5`. Plataforma `linux/amd64`. Se comprobó descarga desde GHCR, etiqueta OCI de revisión, servicios healthy, `/salud`, `/modelo` y tablero. Los modelos y todos los conteos de ambos SQLite permanecieron iguales antes/después del cambio. Kestra conserva su contenedor e historial de aprobación; no se alteraron los volúmenes ni las credenciales Snowflake. El Compose único con MLflow/Spark sigue pendiente.

La recarga/rollback se demostró en un servicio aislado con un proveedor configurado mediante `crear_app`, reutilizando exactamente el código publicado. Se registraron dos versiones del mismo artefacto histórico de semana 2 bajo `oulad-apoyo-academico-recarga-cd-semana2`, etiquetadas como prueba mecánica y `new_training=false`. El servicio observó 1→2→1 desde el alias y produjo 40 predicciones por fase (120 en total), con igual imagen, mismo contenedor, probabilidades idénticas y sin respaldo. El modelo de prueba terminó en versión 1. Los aliases de semana 2/4 y día 56 permanecieron en 1; el candidato de semana 4 continúa rechazado. No se presenta esta prueba como mejora, nuevo candidato de negocio o promoción aprobada de producción.

Las tres cohortes sintéticas usan un SQLite privado separado; no se cargan a Snowflake ni consumen los cupos de los dos escenarios operativos. La evidencia privada conserva metadatos de publicación, digest, identidades de contenedores, estado antes/después y resultados de recarga. El respaldo conserva también `.env` previo protegido, fuente versionada y Registry actualizado. No hubo tuning, entrenamiento ni llamadas LLM. La siguiente etapa pendiente es ética operativa, subgrupos, retirada y respaldo, seguida de evaluación final de negocio e integración/comunicación.


## Ética operativa: protocolo previo al análisis (20-nov-2026)

Se fija `etica-operativa-1` antes de calcular métricas por subgrupo: discapacidad declarada (`disability`, Y/N; faltantes separados), porque diferencias de acceso y uso de la herramienta pueden afectar la oportunidad de apoyo. Solo se utilizarán entradas originales del plan de control y etiquetas disponibles al reloj simulado; no se usarán las demografías permutadas del escenario sintético. Se conservarán los modelos, hiperparámetros y cupos. La definición de discapacidad corresponde al registro declarado de OULAD, no a una inferencia médica ([publicación original](https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/)).

Se reportarán AP de Fail y prevalencia sobre matrículas elegibles de cada corte, las tasas de las tres decisiones y TP/FP/FN, además de cobertura acumulada sobre la cohorte base de semana 2. Las propuestas previas conservan su cupo aun si cambia la elegibilidad. Habrá resultados globales, por lote y edición; personas únicas se contarán separadamente. No se sumarán dos cortes como personas distintas ni se confundirá propuesta con tutoría realizada.

Criterios descriptivos de revisión fijados: brecha absoluta Y-N de cobertura acumulada >5 puntos porcentuales o de FPR >3 puntos, con al menos 200 matrículas, 20 Fail y 20 no-Fail en cada grupo comparable. Un primer lote activa revisión; dos lotes maduros distintos consecutivos del mismo corte proponen suspender el ranking automático para lotes nuevos y usar revisión administrativa. Son umbrales experimentales que requieren acuerdo institucional; no prueban discriminación causal ni cumplimiento legal. Los resultados no llevan intervalos de confianza y las matrículas de una misma persona no son independientes; la edición y prevalencia deben revisarse antes de atribuir diferencias al modelo.

También quedan fijados: bloquear entradas fuera de contrato; pasar a respaldo ante modelo no disponible o artefacto incompatible; retirar ranking si rinde menos que el estático a iguales cupos y población Fail en dos lotes maduros tras evaluar reentrenamiento; y restaurar infraestructura/revisión manual ante 5xx >1 % en dos lotes con al menos 20 solicitudes cada uno. Las condiciones proponen acciones auditables y no promueven ni cambian modelos automáticamente. El comparador de negocio lote por lote se completará en la siguiente etapa.

El respaldo existente conserva el Dummy congelado del PSet 03 y el orden por matrícula, los cupos compartidos y la persistencia. Se añade `puntuacion_individual=false`, un criterio administrativo y un mensaje operativo: el valor técnico constante de Dummy no expresa riesgo individual cero. La acción solicita revisión humana de necesidades. Esta aclaración es aditiva; no modifica respuestas históricas ya registradas ni la preparación del modelo.


## Ética operativa: resultados y responsabilidades (20-nov-2026)

El protocolo se congeló en `65cf599a34f8a18aa01d856fd20c184ce86ce10f` antes del cálculo. Se auditaron las 18.323 predicciones originales de control: 9.231 matrículas de semana 2 y 9.092 elegibles en semana 4, con targets maduros al día simulado 283. No se escribió en Snowflake, no se repuntuó ni se entrenó. Se excluyó el escenario sintético. Hay 72 filas agregadas y 24 comparaciones por ámbito (global, lote y edición); el grupo sin dato se conserva explícitamente y tiene cero casos. Los modelos y cupos originales no cambian.

| Corte | Discapacidad declarada | Matrículas elegibles | Fail elegibles | AP de Fail | Cobertura acumulada | FPR acumulada |
|---|---|---:|---:|---:|---:|---:|
| Semana 2 | N | 8374 | 1731 | 0.3686 | 6,30 % | 1,43 % |
| Semana 2 | Y | 857 | 216 | 0.4051 | 5,56 % | 1,56 % |
| Semana 4 | N | 8250 | 1731 | 0.3789 | 21,89 % | 6,95 % |
| Semana 4 | Y | 842 | 216 | 0.4281 | 18,98 % | 5,93 % |

AP y prevalencia corresponden a las matrículas todavía elegibles en cada corte. La cobertura y FPR acumuladas utilizan la base de semana 2, separada por grupo, e incluyen propuestas previas aunque la matrícula ya no sea elegible. En esa base hay 8.374 matrículas N (1.731 Fail) y 857 Y (216 Fail); no se utiliza solo el saldo de semana 4 como denominador. La AP mayor en Y no garantiza igual acceso al apoyo: la prevalencia y la composición de módulos difieren. Las unidades son matrículas, no personas independientes; las personas únicas por grupo/corte se conservan en la exportación y no deben sumarse entre rondas o ediciones.

| Corte | Grupo | Proponer tutoría nueva | Tutoría ya propuesta | Seguimiento |
|---|---|---:|---:|---:|
| Semana 2 | N | 2,44 % (204) | 0,00 % (0) | 97,56 % (8170) |
| Semana 2 | Y | 2,57 % (22) | 0,00 % (0) | 97,43 % (835) |
| Semana 4 | N | 7,72 % (637) | 2,42 % (200) | 89,85 % (7413) |
| Semana 4 | Y | 6,77 % (57) | 2,61 % (22) | 90,62 % (763) |

**Aceptabilidad condicionada.** En el agregado, la cobertura Y queda 0,74 puntos por debajo de N en semana 2 y 2,91 puntos por debajo en semana 4; las diferencias de FPR son +0,13 y −1,03 puntos. No cruzan los límites experimentales globales, pero no demuestran igualdad de oportunidades ni autorizan un despliegue institucional. Al desagregar aparece una señal que el promedio oculta:

| L06, semana 4, control original | Base | Fail en base | TP acumulados | FN acumulados | Cobertura acumulada |
|---|---:|---:|---:|---:|---:|
| N | 3291 | 687 | 159 | 528 | 23,14 % |
| Y | 346 | 87 | 13 | 74 | 14,94 % |

En L06, Y presenta una brecha de cobertura de **−8,20 puntos porcentuales**, superior al límite de revisión de 5 puntos. Es una diferencia relevante para las personas y para la focalización: equivale descriptivamente a unas ocho propuestas menos por cada cien Fail de Y frente a la tasa de N. **No se acepta el uso automático sin revisión en esa onda.** La coordinación académica debe revisar composición por módulo, accesibilidad y necesidades con el equipo del modelo. No se infiere discriminación causal ni se retocan umbrales o cupos para hacer desaparecer la brecha en este benchmark ya observado. Los resultados por edición se conservaron para esa revisión; las celdas sin tamaño suficiente no se usan para afirmar ausencia de diferencias.

Solo L06 activa `equidad_revision`; no hay dos cohortes comparables consecutivas con exceso, por lo que no se activa la regla de suspensión persistente. El servicio permanece como simulación con propuestas sujetas a revisión humana. N significa que no consta discapacidad declarada en ese registro; no demuestra ausencia de necesidades. La revisión por este atributo no cubre todos los riesgos de equidad ni reemplaza una evaluación prospectiva con la Universidad.

### Quién asume el costo del error

| Resultado | Persona o área que asume el costo | Respuesta operativa |
|---|---|---|
| FP: propuesta sobre matrícula que no termina en Fail | Universidad y tutores: tiempo y cupo; estudiante: tiempo de contacto y posible estigmatización; otras personas: oportunidad de apoyo postergada. | Revisar necesidad y consentimiento antes de confirmar atención. No llamar al estudiante «falso positivo». No-Fail incluye Withdrawn: una falsa alerta de Fail no prueba que el apoyo sea innecesario. |
| FN: Fail que queda sin propuesta | Estudiante: oportunidad de contacto preventivo no priorizada; coordinación académica: posible carga reactiva posterior. | Mantener vías de apoyo y revisión a solicitud, revisar omisiones por grupo y edición. No afirmar que una tutoría habría evitado el Fail. |
| Error o ausencia de datos | Equipo de datos y coordinación del módulo; el estudiante puede recibir una interpretación errónea. | Verificar cobertura y calendario; bloquear entradas inválidas. Ausencia de actividad no equivale a desinterés. |
| Falla del servicio o del modelo | Operación de plataforma y responsable del modelo; tutores requieren continuidad de la cola de revisión. | Respaldo marcado si la API funciona; recuperación de infraestructura y revisión manual fuera del servicio si no funciona. |

No se cuantifican dólares, eficacia tutorial, tutorías realizadas ni ahorros: esos datos no están disponibles.

### Criterios observables de ajuste o retirada

| Criterio | Métrica y umbral | Ventana y acción | Responsable |
|---|---|---|---|
| Calidad | Al menos una entrada fuera de contrato o categoría no admitida. | Inmediato: bloquear el lote (422), corregir la fuente. El respaldo no elude el contrato. | Equipo de datos. |
| Integridad/disponibilidad | Error de carga, firma/preparación incompatible o modelo no disponible. | Inmediato: respaldo administrativo para lotes nuevos y revisión humana; corregir y verificar antes de reactivar. | Responsable del modelo y operación. |
| Valor de negocio inferior | TP del modelo < TP estático, con iguales cupos y base Fail. | Dos lotes maduros de cohortes distintas del mismo corte, tras evaluar reentrenamiento: retirar ranking y operar revisión administrativa. La comparación estática por lote se completará en la etapa de negocio; aquí no se presenta como ejecutada. | Coordinación académica y responsable del modelo. |
| Brecha de acceso | Diferencia absoluta de cobertura >5 puntos o FPR >3 puntos, con mínimo 200 casos/20 Fail/20 no-Fail por grupo. | Un lote: revisión; dos cohortes maduras consecutivas del mismo corte: proponer suspensión del ranking para lotes nuevos. No mezclar cortes ni repetir una cohorte para simular persistencia. | Coordinación académica y equipo del modelo. |
| Fallo persistente del sistema | 5xx >1 % con al menos 20 solicitudes por lote. | Dos lotes consecutivos del mismo corte: restaurar servicio y evaluar respaldo; pausar despachos si la API no está disponible. Las muestras actuales no permiten estimar un SLA. | Operación de plataforma. |

`monitoreo/alertas.py::evaluar_retirada` implementa las condiciones y sus responsables; las pruebas cubren tamaños, persistencia, distintos cortes y comparadores incompatibles. El fallo de carga ya activa respaldo en la API; las otras suspensiones requieren decisión del responsable y operación del interruptor. PSI solo no retira ni reentrena un modelo. Los umbrales son de demostración y deben acordarse con la Universidad, no se presentan como estándares legales.

### Revisión del juicio humano del PSet 01

Se conserva la revisión del tutor sobre contexto y contactos previos definida en `pset-01/proyecto-completo-pset1.md`, sección 3.1.6. Se precisa a la luz de L06: revisar accesibilidad, calidad del registro y oportunidad de apoyo por grupo antes de confirmar la propuesta; coordinación académica resuelve conflictos de cupo y puede suspender la priorización. El estudiante conserva canales habituales de atención y puede pedir revisión aunque no esté seleccionado.

La decisión final de contacto/tutoría y el motivo de una modificación se registrarán en el proceso institucional; ese módulo de seguimiento y apelación no está implementado en la API del prototipo. La API sí conserva propuesta, origen, modelo, política y momento. El modelo no decide sanciones, causas de reprobación, diagnósticos ni recorte automático de presupuesto; una mejora predictiva no acredita tutorías realizadas o Fail evitados.

### Reproducción del análisis

Con Snowflake y las ocho ondas de control conciliadas y maduras:

```sh
docker compose run --rm --no-deps --entrypoint python monitoreo -m monitoreo.deriva --etica /app/.local/etica --codigo-etica <SHA_DE_CODIGO>
```

Los archivos privados `subgrupos.csv`, `subgrupos.json`, `brechas.json`, `retirada.json` y `linaje.json` conservan agregados, criterios y hashes de las entradas y etiquetas maduras. No se agregan CSV de fila individual al repositorio ni se alteran los cinco CSV de evidencia histórica requeridos. El comando rechaza la falta de etiquetas maduras y datos inconsistentes. La inclusión posterior en el notebook y memo final forma parte de la integración pendiente.


## Demostración HTTP del respaldo y cierre de ética (20-nov-2026)

Imagen `ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:e32f542e7320ae939625586d5ce8776fd1ac1933b596cb62b7676e98973ed2a3`, commit de publicación `6c392a3fc7d86e0774fc207d37f19bbc66768c07`, [CD](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44722770969). Se aprobaron 63 pruebas del proyecto; la publicación registra dinámicamente el número real de pruebas aprobadas de la imagen. API, API sintética, monitor y tablero se desplegaron por digest y están healthy. Los modelos conservaron nombre, versión, run y snapshot y los dos registros SQLite mantuvieron sus conteos. Los campos nuevos de metadatos distinguen puntuación individual y cola administrativa.

| Fase del servicio aislado | Configuración | Resultado HTTP y persistencia |
|---|---:|---|
| Normal | `PSET4_FORCE_FALLBACK=0` | 40 predicciones con champion versión 1 y puntuación individual. |
| Respaldo | `PSET4_FORCE_FALLBACK=1` | 80 predicciones nuevas de semanas 2/4, 1+3 cupos sin repetición, mensaje de revisión y `puntuacion_individual=false`. Un tipo inválido siguió devolviendo 422. Repetir el lote normal devolvió su respuesta original. |
| Reactivado | `PSET4_FORCE_FALLBACK=0` | 40 predicciones nuevas con el modelo. Repetir el lote de respaldo conservó la respuesta histórica de respaldo. |

Se usó la misma imagen, recreando el contenedor para leer la variable en cada fase. Las tres cohortes son sintéticas, con un SQLite separado y sin credenciales Snowflake en esa API. Hay 160 predicciones de prueba, ninguna incorporada al análisis de negocio ni al presupuesto del control. El contenedor se retiró. No se cambiaron aliases, modelos, hiperparámetros, particiones ni fuentes Gold; el candidato rechazado sigue rechazado. Los servicios operativos terminan con respaldo no forzado y supervisión humana de propuestas.

Con esto quedan demostrados el interruptor, su reversibilidad y el efecto sobre lotes nuevos sin reescribir historia. Los criterios de retirada continúan como recomendaciones auditables para responsables; L06 requiere revisión y no hay una suspensión persistente automática de producción. La comparación estática por lote y el escenario del 30 % pertenecen a la siguiente etapa de resultado de negocio.


## Protocolo previo al resultado de negocio (20-nov-2026)

Se fija `negocio-operativo-1` antes de calcular el contraste completo. La comparación principal usa el control original, día 28 acumulado: longitudinal frente a estático con idéntica base Fail, corte, política y cupos; meta de al menos +10 % relativo (no 10 puntos porcentuales). La semana 2 es intermedia. Se reutilizan los dos estáticos HGB congelados y los scores longitudinales registrados, sin entrenamiento ni tuning. El replay de la política 25/75 debe reproducir exactamente las decisiones originales; L08 debe coincidir con la comparación de reentrenamiento ya cerrada.

Se comparan políticas de una ronda al día 14, una al día 28 y dos rondas 25/75, manteniendo K por edición. Las alternativas son contrafactuales descriptivos; no se cambia la política activa por observar este benchmark reutilizado. Dummy/cola administrativa, estático y longitudinal permanecen distintos. La reactiva se calcula solo después del cierre+14 simulado con Fail ya conocidos y se informa como cobertura posterior, no como predicción o anticipación. No actuar tiene cero propuestas preventivas/reactivas en la cohorte; no elimina los canales habituales de apoyo. No se infieren Fail del semestre previo a partir de intentos anteriores.

Se informarán propuestas nuevas y acumuladas, TP/FP/FN, precisión y cobertura, personas únicas y casos Fail ganados/perdidos frente al estático (la meta utiliza la diferencia neta). No se sumarán las dos rondas para inflar cobertura o contar dos veces propuestas previas. Plan control y deriva se evalúan separados. El entrenamiento se marcará en L07 sintético y la comparación/rechazo en L08; el candidato no reemplazará ningún score histórico.

Para el 30 % se usa una bolsa reactiva futura **hipotética** igual a K por edición; la bolsa reactiva vigente se protege y su importe real es desconocido. El adelanto es floor(0,30 × R_futuro) por edición, y el saldo queda en R_futuro−adelanto. Se evalúan: solo adelanto si no hay bolsa preventiva financiada, y preventiva independiente K más adelanto. Se vuelve a ordenar cada cohorte con esos presupuestos; no se extrapolan TP/FP linealmente ni se consume presupuesto por fragmento. Un +10 % de detección a igual K no significa que hagan falta 10 % más cupos.

Los escenarios contables suponen cupos de costo unitario comparable; no representan dinero aprobado ni gastos observados. Asistencia {0,1}, efectividad {0,1/4,1/2,1} y probabilidad de requerir apoyo reactivo tras Fail {0,1/2,1} son supuestos, no estimaciones. La reducción potencial de necesidad reactiva es TP × asistencia × efectividad × probabilidad reactiva; no se denomina Fail evitado. Se calcula demanda no cubierta por edición con saldos futuros, incluyendo efectividad cero. El umbral contable de equilibrio es una sensibilidad simplificada, no garantía de ahorro; costos, horas, aceptación y efecto tutorial requieren un piloto con la Universidad.


## Resultado de negocio: focalización, oportunidad y presupuesto (20-nov-2026)

Protocolo `negocio-operativo-1` congelado en `52bd9070ffd789a2a6c481ae12f4f0158574a2a8` antes del cálculo. Se reprodujeron exactamente las decisiones registradas del longitudinal y la comparación L08 del reentrenamiento. La evaluación es de solo lectura: 340 filas de lotes/agregados, 100 contrastes de la meta y 288 escenarios contables; cero entrenamientos y cero escrituras Snowflake. Las alternativas mantienen entradas, elegibilidad y resultados observados fijos; una intervención real podría cambiarlos, efecto que este replay no estima.

### Respuesta al objetivo acordado

En el **control original**, la política de dos rondas usa **920 cupos** sobre **1.947 Fail** en la cohorte base. El longitudinal prioriza **420 Fail** y el estático **314**. La mejora relativa de cobertura es **33,76 %** (`420/314−1`), superior al objetivo +10 %; la cobertura sube de **16,13 % a 21,57 %**, 5,44 puntos porcentuales. La meta exigía al menos 346 TP y se obtuvieron 420.

| Comparador | Propuestas tempranas | TP tempranos | FP tempranos | Precisión al cupo | Cobertura temprana | Personas con propuesta | Fail priorizados después de conocer el resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| Longitudinal | 920 | 420 | 500 | 45,65 % | 21,57 % | 893 | No observado |
| Estático HGB | 920 | 314 | 606 | 34,13 % | 16,13 % | 907 | No observado |
| Dummy / cola administrativa | 920 | 187 | 733 | 20,33 % | 9,60 % | 916 | No observado |
| Reactiva posterior | 0 | 0 | 0 | No definida | 0,00 % | 0 | 920 |
| Sin acción del programa | 0 | 0 | 0 | No definida | 0,00 % | 0 | 0 |

Las 106 detecciones adicionales son **netas y por matrícula-asignatura**, no necesariamente 106 personas. Se ganan 257 Fail que el estático no priorizó y se pierden 151 que sí priorizó: `257−151=106`. No se necesitan 106 cupos por encima de 920 para materializar esa mejor focalización. A igual cupo, el conteo de FP baja de 606 a 500 (106 menos); esto no demuestra 106 tutorías ahorradas. Las propuestas no acreditan aceptación ni tutorías realizadas.

La proporción FP entre propuestas del longitudinal es 500/920=54,35 %; la FPR convencional es 500/7.284=6,86 %. Son denominadores distintos. Un FP solo significa no-Fail observado y puede incluir Withdrawn que también necesite apoyo. La meta no afirma que todo Fail habría sido evitable.

La reactiva llega después del cierre+14 simulado, cuando ya conoce los Fail: puede priorizar 920 de ellos a esa capacidad, sin anticipación. Su precisión posterior es 100 % por construcción, no una predicción superior. No se reconstruye el apoyo al semestre previo: esa historia y su presupuesto real no se observan. La bolsa reactiva vigente permanece protegida en el diseño. «Sin acción» se refiere a este programa sobre la cohorte, no a la eliminación de las vías habituales de ayuda.

### Resultado por lote y efecto de la deriva

Cupos, TP y FP de semana 4 son **acumulados** sobre la base de semana 2 de esa onda. No sumar L01+L05, L02+L06, L03+L07 o L04+L08 como contactos independientes. Las filas de semana 2 utilizan solo su fracción inicial del mismo presupuesto.

**Control original**

| Lote | Corte | Cupos acumulados | TP longitudinal | TP estático | FP longitudinal | Mejora relativa | Meta +10 % |
|---|---|---:|---:|---:|---:|---:|---|
| L01 | Semana 2 | 33 | 19 | 13 | 14 | 46,15 % | Sí |
| L02 | Semana 2 | 90 | 50 | 41 | 40 | 21,95 % | Sí |
| L03 | Semana 2 | 67 | 26 | 26 | 41 | 0,00 % | No |
| L04 | Semana 2 | 36 | 26 | 17 | 10 | 52,94 % | Sí |
| L05 | Semana 4 | 136 | 66 | 43 | 70 | 53,49 % | Sí |
| L06 | Semana 4 | 363 | 172 | 132 | 191 | 30,30 % | Sí |
| L07 | Semana 4 | 274 | 105 | 85 | 169 | 23,53 % | Sí |
| L08 | Semana 4 | 147 | 77 | 54 | 70 | 42,59 % | Sí |

**Escenario sintético separado**

| Lote | Corte | Cupos acumulados | TP longitudinal | TP estático | FP longitudinal | Mejora relativa | Meta +10 % |
|---|---|---:|---:|---:|---:|---:|---|
| L01 | Semana 2 | 33 | 19 | 13 | 14 | 46,15 % | Sí |
| L02 | Semana 2 | 90 | 50 | 41 | 40 | 21,95 % | Sí |
| L03 | Semana 2 | 67 | 26 | 26 | 41 | 0,00 % | No |
| L04 | Semana 2 | 36 | 26 | 17 | 10 | 52,94 % | Sí |
| L05 | Semana 4 | 136 | 66 | 43 | 70 | 53,49 % | Sí |
| L06 | Semana 4 | 363 | 105 | 93 | 258 | 12,90 % | Sí |
| L07 | Semana 4 | 274 | 69 | 73 | 205 | -5,48 % | No |
| L08 | Semana 4 | 147 | 77 | 54 | 70 | 42,59 % | Sí |

No se ocultan resultados desfavorables: L03 empata y no alcanza +10 %. En la deriva, L07 queda **69 frente a 73 TP**, −5,48 %, a iguales 274 cupos acumulados. El resultado global sintético sigue sobre la meta (**317 frente a 263 TP, +20,53 %**), pero pierde **103 TP** frente al longitudinal del control. El estático también se deteriora, porque la inducción modifica vectores completos de features y créditos; no es un experimento de cambios exclusivos en la actividad. Los escenarios no son poblaciones independientes y sus presupuestos o personas no se suman.

**Retirada por valor de negocio:** ahora existen comparadores estáticos por lote, reemplazando esa carencia de la etapa previa. Solo L07 sintético es inferior; L06 sigue sobre el estático. No hay dos cohortes consecutivas por debajo que cumplan la regla persistente. La igualdad de L03 no es inferioridad estricta. La revisión de L07 y la revisión ética de acceso en L06 se mantienen; una mejora agregada no las cancela. No se observó un período posterior con un modelo reentrenado promovido.

### Anticipación y elección de ronda

| Escenario | Política temporal | Cupos totales | TP al terminar semana 4 | FP |
|---|---|---:|---:|---:|
| Control | solo_semana2 | 920 | 415 | 505 |
| Control | dos_rondas | 920 | 420 | 500 |
| Control | solo_semana4 | 920 | 426 | 494 |
| Deriva | solo_semana2 | 920 | 415 | 505 |
| Deriva | dos_rondas | 920 | 317 | 603 |
| Deriva | solo_semana4 | 920 | 278 | 642 |

A igual capacidad total, solo semana 4 obtiene 11 TP más que solo semana 2 en el control (426 frente a 415), con 11 FP menos. No se atribuye causalmente esa diferencia a mayor información: también cambia la elegibilidad y se usan modelos propios de cada corte. El reparto 25/75 logra 420 TP y adelanta **226 propuestas**, 121 con Fail posterior, con **14 días más de anticipación** que esperar semana 4 para la misma onda. Solo esperar semana 4 suma seis TP frente a dos rondas, pero pierde ese adelanto de contacto. En la deriva, dos rondas obtiene 317 TP frente a 278 al esperar toda la capacidad hasta semana 4. Es un análisis de sensibilidad, no una selección prospectiva de política óptima.

El margen de las propuestas nuevas hasta cierre del módulo está entre **245 y 255 días** en semana 2 y **231 y 241** en semana 4, según módulo y cola simulada. Proviene de las duraciones de OULAD y no se traslada automáticamente al calendario de la Universidad. Tampoco garantiza disponibilidad de tutores o eficacia: los 21 días ilustrativos del PSet 03 no son una condición validada aquí. El reparto operativo 25/75 continúa experimental; no se cambia con este benchmark ya inspeccionado.

### Reentrenamiento: dónde ocurrió y qué cambió

El disparador fue la caída persistente madura del **L07 sintético**, al día simulado 283, después de haber realizado las ocho predicciones (días 14–31). Se reservó **L08** como último lote etiquetado por fecha de predicción para comparar. El challenger obtuvo **81 TP frente a 77** del champion; la regla exigía siete adicionales y obtuvo cuatro. Wilmer Puerta confirmó su rechazo.

Ningún score histórico cambió y todas las predicciones de esta evaluación mantienen **versión 1**. El efecto observado del ciclo sobre el despliegue es **cero cambios de versión**, no un aumento atribuible de TP. El +33,76 % procede del longitudinal original frente al estático, no del candidato rechazado. No hay un período posterior con modelo nuevo en producción que permita estimar su efecto operativo.

### Qué puede financiar un adelanto del 30 %

Para ilustrar capacidad, se supone una bolsa reactiva futura igual a **920 cupos**, distribuida por edición como K. No es una cifra presupuestaria de la Universidad. `sum(floor(0,30×R_edición))` adelanta **274** y deja **646**; los redondeos permanecen en el saldo reactivo, no se pierde presupuesto. Si se moviera una bolsa única sin separación por edición serían 276: es otra regla, no la aplicada. La bolsa reactiva vigente no se toca y su importe sigue desconocido.

| Escenario de financiación, control | Preventivos disponibles | TP longitudinal | FP longitudinal | Cobertura Fail | Reactivos futuros restantes |
|---|---:|---:|---:|---:|---:|
| Referencia K, prevención independiente | 920 | 420 | 500 | 21,57 % | 920 |
| Solo adelanto, sin prevención financiada previa | 274 | 152 | 122 | 7,81 % | 646 |
| Prevención K más adelanto | 1194 | 530 | 664 | 27,22 % | 646 |

Se recalcularon los rankings, no se extrapolaron FP: con solo 274 cupos hay 122 FP; con 1.194 hay 664. El 30 % de una bolsa reactiva futura de 920 no financia los 920 cupos preventivos del benchmark. Si ya existe una bolsa preventiva independiente de 920, el adelanto la amplía a 1.194, con 110 TP adicionales y 164 FP adicionales frente a la referencia. Las bolsas preventivas y reactivas futuras suman 1.840 antes y después de esa transferencia; en el caso sin prevención previa suman 920. No se cuenta el mismo dinero/cupo como financiación y también como beneficio. Si los costos por tutoría preventiva/reactiva difieren, porcentajes monetarios no equivalen a estos porcentajes de cupos.

### Sensibilidad de la necesidad reactiva futura

Se conserva el target original. Se supone que una fracción `a` de propuestas se atiende, una efectividad hipotética `e` reduce necesidad reactiva y una fracción `q` de los Fail requeriría ese apoyo. La necesidad potencialmente reducida es `TP×a×e×q`; **no son Fail evitados medidos**. Cada celda de demanda no cubierta se calcula por edición, sin usar el sobrante de otro módulo. La tabla siguiente usa `a=q=1`, un extremo ilustrativo, con costos unitarios preventivo/reactivo iguales y la bolsa futura asumida de 920.

| Financiación | Efectividad supuesta | Demanda reactiva no cubierta sin adelanto | Con adelanto |
|---|---:|---:|---:|
| solo_adelanto | 0,00 % | 1027 | 1301 |
| solo_adelanto | 25,00 % | 1027 | 1263 |
| solo_adelanto | 50,00 % | 1027 | 1225 |
| solo_adelanto | 100,00 % | 1027 | 1149 |
| preventiva_mas_adelanto | 0,00 % | 1027 | 1301 |
| preventiva_mas_adelanto | 25,00 % | 922 | 1168.5 |
| preventiva_mas_adelanto | 50,00 % | 817 | 1036 |
| preventiva_mas_adelanto | 100,00 % | 608 | 771 |

Con efectividad cero no se reduce necesidad y quedan 274 cupos reactivos menos. Aun con efectividad y asistencia 100 % y q=1, el caso de prevención independiente más adelanto pasa de 608 a 771 necesidades no cubiertas: adelanta 274 cupos pero suma 110 TP respecto de la prevención ya financiada. El equilibrio contable simplificado exigiría `e=274/110=2,49` con a=q=1, fuera de [0,1]; no es alcanzable bajo esos supuestos. En solo adelanto, `274/152=1,80` también supera 1. Esto no demuestra que el apoyo temprano carezca de valor: no se valoran timing, costos distintos, otros resultados o demanda real; demuestra que **no se puede justificar el adelanto como ahorro garantizado**. Se conservaron 288 combinaciones, incluidas asistencia cero, efectividad cero y q=0, 0,5 o 1; ninguna es una estimación causal.

### ¿Valió la pena actuar según la predicción?

**Sí hay evidencia retrospectiva de mejor focalización a igual capacidad:** el longitudinal supera al estático en 106 Fail netos en el control y cumple la meta acordada; la revisión puede adelantarse al período en curso. **No hay evidencia de que las tutorías se hayan realizado, evitado Fail o producido ahorro económico.** Antes de adoptar una transferencia presupuestaria, la Universidad debe validar capacidad realmente financiada, unidad de atención, costos, demanda reactiva, aceptación, efecto del apoyo y revisión de acceso de L06. La opción de más detección a igual cupo no requiere justificar automáticamente un presupuesto mayor.

El benchmark 2014J fue inspeccionado antes: no es una validación prospectiva nueva ni ocho semestres independientes. La meta principal se fijó antes del cálculo y no se selecciona la variante más favorable para redefinirla. La incertidumbre de generalización e impacto requiere cohortes nuevas y un piloto; no se presentan p-valores ni intervalos como prueba institucional.

### Reproducción y trazabilidad

```sh
# Desde proyecto_final/, con Registry y credenciales privadas de Snowflake configurados.
docker compose run --rm --no-deps --entrypoint python monitoreo -m src.reentrenar --evaluar-negocio /app/.local/negocio --codigo-negocio <SHA_DEL_CODIGO>
```

La salida privada contiene `lotes`, `meta`, `presupuestos`, `finanzas`, `selecciones`, `reentrenamiento` y `linaje` en JSON y tablas agregadas CSV. Guarda hashes de entradas/targets maduros, pipelines estáticos, snapshots, runs y código. No reemplaza los cinco CSV históricos de la rúbrica. El tablero lee únicamente agregados locales montados de solo lectura, sin credenciales cloud, y muestra el contraste por lote, la mejora y los comparadores por horizonte. No se cambian alias, cupos operativos ni el reparto de la API.


## Publicación y comprobación del resultado de negocio (20-nov-2026)

[PR #3](https://github.com/wilmerpuerta/data-science-end-to-end/pull/3) integrado con sus controles aprobados. Imagen `ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:ee4e0da32b14bb5254463229dd40c31483118ef57360657a84ece166cff4b9f6`, revisión `eb8da65b6a7fcaa8f9ec4a19a2fcfbf9cfd18119`, [CD](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44734850139). Se aprobaron 69 pruebas completas en CI y en la imagen final. API, API sintética, monitor y tablero están healthy con el mismo digest y revisión OCI. El tablero mostró 106 y 54 TP netos adicionales en control y deriva, sin excepciones y usando agregados de solo lectura.

Se conservaron íntegros los dos registros SQLite, los tres champions versión 1 y el candidato de semana 4 rechazado. Snowflake mantiene 36.646 predicciones, 32 eventos de monitoreo y cuatro de reentrenamiento. La evaluación no entrenó, cambió alias ni escribió registros cloud; no se alteró la política experimental 10 % y reparto 25/75. La bolsa del 30 % sigue siendo un supuesto de análisis. Se conserva respaldo privado de agregados, linaje, registros y evidencias de ejecución, fuera de Git. El siguiente bloque es integración completa y comunicación; esta comprobación no cierra aún el PSet 04.


## Compose único e ingesta hasta OBT (20-nov-2026)

**Observación:** el proyecto todavía dependía del MLflow del PSet 03 y faltaba `kestra/ingesta.yml`. Se agregan MLflow, dbt y Spark al Compose propio y se integra la ingesta en `src/datos.py`. Los Dockerfiles de dbt/Spark y el target Kestra incorporan código, contratos y dependencias fijadas; no requieren ejecutar ni importar los proyectos anteriores. El SQL y las features originales y `src/pipeline.py` se conservan byte a byte. CI valida Compose con valores ficticios y las 84 pruebas verifican contrato, modelo, negocio y controles de publicación. No se llamó a un LLM ni se entrenó/promovió un modelo en esta etapa.

**Registry:** copia SQLite online con integridad y comparación de filas/hashes de todas las tablas; artefactos en volúmenes independientes con 20.790 archivos / 2.838.908.573 bytes idénticos. Permanecen 825 runs, ocho experimentos y diez versiones, con los mismos IDs, fuentes, aliases, tags y decisiones. El MLflow histórico conserva su puerto 5001 y sus volúmenes; el proyecto final usa 5004 en el host y `http://mlflow:5000` entre servicios. No se cambiaron los modelos ni la decisión humana de rechazo.

**Incidencia y corrección:** la ejecución inicial `sUznAZ24sXpaD706ZP4zH` terminó FAILED en dbt por un error de E/S al leer el perfil desde el directorio sincronizado; Spark no se ejecutó. Se corrigió el directorio de trabajo de dbt y se retiraron los mounts de código de los ejecutores, incorporándolo en las imágenes. Se conserva la evidencia fallida; no se oculta ni se atribuye a un problema del modelo.

**Ejecución aceptada:** `2sQlV9Hreu3bWXWi7MtYRE` terminó SUCCESS, tareas Raw → dbt → Spark → verificar, todas a la primera, con código `74e1002c5b5ad9cca4931c44a540df1fc51202a5`. Raw reconcilió cinco archivos y 10.726.852 filas, sin recarga de una versión ya verificada. dbt aprobó 23 modelos y 168 pruebas. Spark publicó 108.277 claves matrícula/corte, 35 columnas y cuatro cortes con pruebas de perturbación futura; validó todas las columnas de lectura de vuelta antes del swap. Los hashes por corte coinciden con la referencia histórica `6X7mzEdM0yvoBSbp8MnALv` del PSet 02. Las evidencias completas son privadas en `.local/ingesta/`.

| Corte | Filas OBT | Sin actividad registrada | Hash frente al PSet 02 |
|---|---:|---:|---|
| 14 | 27,881 | 1,582 | Idéntico |
| 28 | 27,307 | 881 | Idéntico |
| 42 | 26,795 | 684 | Idéntico |
| 56 | 26,294 | 576 | Idéntico |

Los ejecutores HTTP no publican puertos al host, exigen un secreto interno y solo aceptan un `execution_id` válido, sin campos de comandos. Las pruebas HTTP comprobaron 401 sin secreto, rechazo 400 del comando libre, ausencia de trabajos tras la solicitud inválida y repetición de un trabajo exitoso con el mismo ID/intento. Kestra limita concurrencia a uno; no se ejecutan simultáneamente escritores de stacks históricos sobre la misma base.

La nueva reproducción de infraestructura usa un solo Compose y el mismo orden de datos; no equivale a reentrenar ni a validar prospectivamente los modelos. La reconstrucción del Registry en una máquina nueva requiere restauración o registro de modelos. Permanecen pendientes los notebooks finales y la comunicación; no se declara cerrado el PSet 04.


## Publicación y despliegue del Compose integrado (20-nov-2026)

[PR #4](https://github.com/wilmerpuerta/data-science-end-to-end/pull/4), revisión `a4fc842a0f38ddf2f4ccba01638f6c67be36f9a3`, [CD](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44757001546). CI validó el Compose sin servicios ni credenciales reales y aprobó 84 pruebas; la imagen exacta también aprobó 84 antes de publicarse. Referencia desplegada: `ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:c8c922877eeaa909c9463deaa877e3908451e1e373e5b9eeff10ed7b58ab5c96`.

Nueve servicios saludables tras `docker compose up -d --no-build --pull never --wait`; cinco con digest/revisión OCI publicados. Se comprobaron código incorporado en dbt/Spark/Kestra, ausencia de sus binds de código y de puertos HTTP de los ejecutores al host. API y monitor resuelven `http://mlflow:5000`; la UI propia está en localhost:5004. Los datos originales siguen montados de solo lectura. Las credenciales se copiaron íntegramente a `.local/credenciales/`, sin retirar sus originales ni versionarlas.

Se conservaron las filas de ambos SQLite, 36.646 predicciones / 32 eventos de monitoreo / cuatro eventos de reentrenamiento en Snowflake, y los hashes de todas las tablas del Registry frente al snapshot inicial. Los champions siguen en versión 1 y el challenger de semana 4 rechazado. El tablero confirmó 106 / 54 TP netos adicionales de control/deriva, sin errores. No se realizó entrenamiento, tuning, promoción ni consumo de API LLM. Se preservan fuente de datos, preparación, política y decisiones anteriores. Notebooks finales, memo, presentación y video siguen pendientes.


## 2026-11-20 — Memo, presentación y guion de demostración

Se prepararon `PSet4_memo_Puerta_Wilmer.pdf` (12 páginas) y `PSet4_presentacion_Puerta_Wilmer.pdf` (12 diapositivas), con fuentes de texto en `memo.md` y `presentacion.md`. `guion_video.md` distribuye nueve escenas en 6:35 minutos, con 25 segundos de margen, narración y comandos de ensayo. Los gráficos de los documentos son vectoriales; `arquitectura.png` y `modelo_dimensional.png` conservan vistas de alta resolución. Se renderizaron e inspeccionaron las páginas y diapositivas antes de incorporarlas a la entrega.

La comunicación responde al objetivo de negocio con la misma población y capacidad: 420 frente a 314 TP, 106 matrículas netas adicionales, +33,76 % relativo con 920 cupos. Se muestran resultados por lote y se marcan L07 como disparador maduro y L08 como reserva de comparación, sin colocarlos falsamente como una promoción anterior a la inferencia. El reentrenamiento ocurrió después de las ocho predicciones; el candidato sumó cuatro TP cuando requería siete y se conserva el rechazo humano. La presentación recomienda ajustar y validar mediante un piloto supervisado; no afirma efectos causales ni ahorro por el escenario del 30 %.

El memo incluye EDA y validación agrupada de PSet 03, selección por valor de negocio, prueba de GPT mediante prompting, modelos específicos de semanas 2/4, criterios de retirada y tasas de decisión por discapacidad. Distingue el predictor estático, el Dummy administrativo, no actuar y la atención reactiva posterior. Describe la brecha de cobertura de L06 y la necesidad de revisión humana, y conserva los supuestos y resultados desfavorables.

Se capturó directamente GitHub Actions en Chrome: run 44781023359, revisión 03018cb, CI reutilizable y publicación en Success. La captura completa y su URL se conservan en `github_actions.png` y `evidencia_comunicacion.json`. La imagen activa se mantiene por el digest previamente comprobado; publicar documentación no promueve modelos ni cambia el entorno desplegado.

`ejemplo_api.json` conserva solicitudes completas de semanas 2/4, respuestas HTTP 200 y error HTTP 422 reales, obtenidos con la imagen publicada y el Registry propio en un servicio aislado. Los IDs son sintéticos; sus features son valores repetidos de la muestra de desarrollo pública OULAD. El contenedor se retiró; no se cargaron filas a Snowflake ni se tocaron aliases operativos, entrenamiento, tuning o API LLM. El guion separa esta demostración, la recarga 1→2→1 con pesos idénticos y el interruptor de respaldo de la evaluación real de negocio.

`PSet4_anexos_Puerta_Wilmer.pdf` reúne sin modificar los tres memos anteriores y una copia fechada de este registro. El límite de 12 páginas aplica al memo principal y excluye estos anexos. La convención `Puerta_Wilmer` se mantiene por indicación del autor, sin atribuir una excepción docente al requisito literal de dos apellidos.

Pendiente para cerrar el PSet 04: notebooks 01-07 con salidas y Restart/Run All, pitch histórico en PDF, grabación de la demo de máximo siete minutos, publicación del enlace e incorporación de la URL real al memo y auditoría final de la rúbrica. El guion y el marcador explícito «pendiente de publicación» no sustituyen el video. No se declara completado el proyecto final.


## 2026-11-20 — Corrección del calendario de PSet 02

Feedback recibido en Kestra (9,5): activar el cron de días 1 y 15 y presentar evidencia programada. Se corrigió `pset_2/kestra/oulad_pipeline.yml`: `0 9 1,15 * *`, 09:00 America/Guayaquil, padre activo y Raw sin calendario independiente. En la instancia de entrega `pset2-entrega` se recuperó mediante backfill la fecha del 15-nov-2026; el planificador creó `5Iuxh5EoC9h21NtOUObQuS` con trigger Schedule y la cadena terminó SUCCESS el 20-nov. No se afirma observar la llegada del cron el día 15 en tiempo real.

Raw, 23 modelos y 168 pruebas dbt, y Spark aprobaron al primer intento; la OBT conservó 108.277 filas ×35 columnas y sus cuatro hashes. Un error EIO de lectura de `audit.json` requirió reponer la referencia idéntica a Git, remontar Kestra y reiniciar solo la verificación final; fallo y recuperación manual se conservan. La documentación y el memo de PSet 02 (seis páginas) se actualizaron, con el original aprobado preservado en su historial. Evidencia: `pset_2/docs/calendario-programado.md`, `calendario-verificacion.json` y capturas reales en `docs/evidencia/calendario/`.

La corrección no cambia SQL, features, contrato, entrenamientos, aliases ni predicciones del proyecto final. El cron activo corresponde a PSet 02; `proyecto_final/kestra/ingesta.yml` no despliega un segundo cron sobre las mismas tablas. Antes de trasladar esa responsabilidad al despliegue final debe elegirse un único escritor calendarizado. Los originales OULAD y archivos del proyecto deben permanecer disponibles localmente; la siguiente fecha registrada es 1-dic-2026 09:00 y exige equipo, Docker, Kestra y acceso cloud disponibles. Los anexos de comunicación ya emitidos conservan su corte documental anterior a esta corrección.


## 2026-11-20 — Redacción de la procedencia en la comunicación final

Se simplificó la atribución del conjunto de datos en el memo y su fuente editorial: The Open University (OULAD). El memo conserva 12 páginas; las páginas 2-12 mantienen texto y geometría. Se revisaron la presentación y el guion, cuyos textos ya identificaban OULAD como fuente. Se actualizaron el generador editorial y los hashes del memo para reproducir esta redacción. Se preservan resultados, criterios de negocio, modelos, decisiones y documentos históricos.


## 2026-11-21 — Ampliación y equilibrio visual del memo

Se amplió la explicación en las páginas 1 y 3-12, según el espacio disponible, manteniendo 12 páginas. Se desarrollan el uso de los cupos y los falsos positivos, el join que conserva matrículas sin actividad, la selección por cobertura al cupo, el reparto entre semanas, la operación ante errores API, la separación código/modelo, el diagnóstico de alertas, el rechazo del candidato, el seguimiento del acceso, la lectura de métricas por onda y el diseño del piloto. La página 2 conserva contenido y distribución; se actualiza la fecha del pie de revisión en todo el documento.

Los párrafos anteriores, tablas, gráficos, cifras y decisiones se conservan. Se revisaron visualmente las 12 páginas y se comprobaron fuentes, límites y ausencia de recortes. Los márgenes de cierre quedan entre 53,4 y 65,4 puntos. No se cambia el tamaño de letra ni se introducen resultados experimentales; tampoco se repiten entrenamiento, tuning o llamadas a un LLM. Se actualizan la fuente editorial, el generador local y los hashes de comunicación.


## Notebooks, fuentes PSet1 y lectura de negocio (24-nov-2026)

- Se integraron los siete notebooks en `proyecto_final/notebooks/`, con kernel nuevo, ejecución completa y salidas guardadas. `src/notebooks.py` permite repetirlos y genera un informe con las huellas de los notebooks ejecutados. La dependencia opcional de Jupyter permanece dentro de `notebooks/`.
- Se releyeron los cinco originales: huellas y tamaños idénticos; claves, faltantes, relaciones, clases y poblaciones elegibles en 14/28/42/56 coinciden con PSet1. Son 32.593 matrículas, 28.785 personas y 10.655.280 filas de actividad; cero filas huérfanas o clics negativos. `docs/validacion_pset1.json` conserva la comprobación. No se sobrescribieron manifiesto ni informes históricos.
- Se distinguen el desarrollo del día 56 y la preparación temprana: sus poblaciones elegibles y purgas no son intercambiables. Las transformaciones se verifican dentro de cada fold; la preparación original `src/pipeline.py` conserva sus bytes.
- Los notebooks 03-04 recalculan métricas de folds y búsquedas ya registradas. El 05 verifica probabilidades de muestras de desarrollo; el 06 ejecuta HTTP con modelos exportados y SQLite temporal; el 07 reproduce rechazo, negocio, alertas y revisión de acceso. No se hicieron nuevas llamadas LLM, búsquedas ni entrenamientos de clasificadores.
- Se atendió el feedback PSet3 en el memo final: lenguaje más directo, lectura de tablas orientada a decisiones, definición de cobertura/precisión/TP/FP/FPR y separación entre detección, atención e impacto. Se conserva en 12 páginas con gráficos vectoriales y revisión visual de todas las páginas.
- Se hace explícito desde la primera página que 2014J es una evaluación retrospectiva conocida, no un hold-out independiente de un solo uso. Purga, nueva estructura y reserva L08 no borran el conocimiento previo. La validación independiente queda para una cohorte futura con protocolo fijado antes de ver sus resultados.
- Las 84 pruebas del servicio aprobaron en una copia local fuera de la carpeta sincronizada. Se comprobó igualdad de los árboles Git de API, tests y pipeline con la fuente de trabajo; el entorno temporal evita bloqueos FileProvider de macOS. Esta ejecución no constituye un nuevo despliegue ni una validación prospectiva.
- El memo PSet3 histórico se conserva como antecedente; sus limitaciones se incorporan a la interpretación del proyecto final. Pendientes de entrega: pitch histórico PDF, video/URL y auditoría final conjunta de la rúbrica.
