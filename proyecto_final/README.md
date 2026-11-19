# Proyecto final: apoyo académico preventivo

Estado: **servicio batch implementado y verificado**, con modelos específicos de semanas 2 y 4, contrato Pydantic, registro transaccional, respaldo, fixtures y CI. La carga Snowflake y los ocho despachos de control quedaron verificados (18.323 predicciones únicas). Monitoreo, deriva y tablero quedaron verificados con controles y un escenario sintético separado. El reentrenamiento con aprobación y los entregables de comunicación siguen pendientes. Este Compose integra las API de control y escenario sintético, Kestra/PostgreSQL, monitor y tablero, utilizando el Registry existente; todavía no es el Compose único de los cinco servicios finales.

## Objetivo de negocio

Al menos **10 % de mejora relativa en cobertura de Fail frente al modelo estático, con iguales cupos**, durante el período en curso. La cobertura es `TP / Fail de la cohorte base` y la mejora relativa es `cobertura_longitudinal / cobertura_estatica - 1`. Con 500 Fail, 200 cupos y 100 TP del estático, la meta exige 110 TP: 22 % de cobertura frente a 20 %. Si la cobertura estática es cero, la razón no se define.

Control estático, Dummy y política reactiva son comparadores distintos. El adelanto del 30 % de la atención reactiva futura es un escenario presupuestario; la bolsa reactiva vigente se protege. Los cupos y el reparto experimentales no son fondos institucionales aprobados. Las propuestas requieren revisión humana; no equivalen a tutorías realizadas ni a reprobaciones evitadas.

## Estructura y continuidad

Se conserva el árbol de la rúbrica. `dbt/` y `spark/` contienen las fuentes del PSet 02 sin alterar; `src/pipeline.py` conserva byte a byte la preparación del PSet 03. Los tres memos anteriores están en `docs/historial/`; el pitch histórico y los notebooks integrados aún están pendientes. Las carpetas vacías usan `.gitkeep` solo para conservar su estructura. `.dockerignore` impide enviar entornos, credenciales y datos privados al build.

Los modelos tempranos reutilizan los artefactos completos del PSet 03; no se repitió tuning ni entrenamiento. Los nombres son `oulad-apoyo-academico-semana2-modelo@champion` y `oulad-apoyo-academico-semana4-modelo@champion`. Ambos se sirven por versiones iniciales específicas de su corte. El champion histórico del día 56 permanece intacto. Este uso es experimental y no constituye validación prospectiva independiente.

## Preparar el entorno

Desde `proyecto_final/`, con Python 3.11, uv y Docker Compose:

```sh
uv venv --python 3.11 .venv
uv pip sync --link-mode copy --python .venv/bin/python --only-binary=:all: --require-hashes requirements.txt
cp .env.example .env
```

`requirements.txt` fija la resolución completa con hashes. El ejemplo de entorno contiene valores públicos y campos de secretos vacíos; antes de usar Compose completar las contraseñas y rutas privadas descritas en la sección Snowflake/Kestra. Las pruebas con fixtures no necesitan esos secretos. No guardar contraseñas, tokens ni claves en Git. `.local/` se excluye de la publicación y contiene el registro de operación privado.

Para comprobar lo ya entregado no se necesitan datos originales ni servicios cloud:

```sh
PSET4_FULL_TESTS=1 PSET4_MODEL_MODE=fixture .venv/bin/python -m pytest tests -q -p no:cacheprovider
```

Las fixtures se exportaron con `mlflow.sklearn.save_model`, con firma y `predict_proba`. Sus hashes, procedencia y métricas de referencia están en `tests/fixtures/referencia.json`. La muestra contiene 60 observaciones de desarrollo por corte sin identificadores reales, derivadas de OULAD (The Open University, CC BY 4.0; DOI 10.1038/sdata.2017.171). Su AP es una referencia de reproducción sobre esa muestra, no la AP de CV ni una prueba independiente de generalización. La tolerancia `1e-10` admite redondeo numérico sin tolerar cambios sustanciales de predicción.

## Ejecutar la API

Para carga real por alias debe estar disponible el servidor del PSet 03 con sus artefactos y Registry, en `http://127.0.0.1:5001`. Dentro del contenedor se accede mediante `MLFLOW_TRACKING_URI=http://host.docker.internal:5001`; configurar otro destino si el servidor vive en otra máquina. La API no recibe claves Snowflake. Kestra realiza la carga periódica desde el registro durable local y concilia el lote antes de completarlo.

```sh
.venv/bin/python -m src.datos --ejemplo .local/ejemplo --cohorte-id ejemplo-modelo
docker compose up -d --build --wait api
curl http://localhost:8004/salud
curl 'http://localhost:8004/modelo?corte_dias=14'
curl -X POST http://localhost:8004/predecir -H 'Content-Type: application/json' --data-binary @.local/ejemplo/semana2.json
curl -X POST http://localhost:8004/predecir -H 'Content-Type: application/json' --data-binary @.local/ejemplo/semana4.json
curl http://localhost:8004/metricas
```

Documentación interactiva: `http://localhost:8004/docs`. El ejemplo registra 40 matrículas sintéticas, sin targets en las solicitudes. El valor de prueba reserva 1 cupo en semana 2 y 3 adicionales en semana 4. No se utiliza para estimar calidad o impacto educativo.

`GET /salud` informa el estado de los modelos cargados sin depender de una consulta de red en cada sondeo. `GET /modelo` consulta el alias y muestra nombre, versión, run_id, corte y procedencia. `POST /predecir` acepta una cohorte completa registrada, devuelve probabilidad de Fail, ranking, decisión, acción, versión e ID, y persiste el resultado antes de responder. `GET /metricas` informa p50/p95, volumen y tasas 4xx/5xx. Campos ausentes, tipos, categorías, rangos, entradas no finitas y targets en las features se rechazan con 422 y el campo identificado.

La carga de cohortes es una operación administrativa local; no se exponen endpoints públicos que permitan inventar un manifiesto o un presupuesto. Para un manifiesto procedente de la fuente confiable:

```sh
.venv/bin/python -m src.datos --registrar-cohorte /ruta/privada/cohorte.json
```

Su formato contiene `cohorte_id`, `base` (matrícula a edición), `elegibles` (mapas completos de días 14 y 28) y `personas`. La elegibilidad de día 28 pertenece a la base. Repetir el registro idéntico es seguro; la misma cohorte con otro nombre no obtiene presupuesto nuevo.

## Cupos, repetición y trazabilidad

La unidad es matrícula-asignatura, con personas únicas aparte. El prototipo fija `floor(0.10 × elegibles_día14)` por edición y comparte ese presupuesto entre ambas rondas. El reparto de prueba es 25/75 y aún no es una política seleccionada. La política se identifica por versión y hash de sus parámetros; las dos rondas conservan la misma política.

El orden es riesgo descendente y matrícula ascendente en empates. Las propuestas anteriores conservan su reserva aunque cambie la elegibilidad; no se cancelan ni se cobran otra vez. La primera ronda debe existir antes de la segunda cuando reserva cupos. El servidor rechaza fragmentos, duplicados o IDs que no correspondan al manifiesto.

La transacción SQLite serializa la asignación y guarda lote y predicciones juntos. Repetir un lote, incluso en otro orden, devuelve los mismos IDs y la versión original sin repuntuar. Cambiar el contenido de un corte ya procesado devuelve 409. Los registros contienen timestamp, entradas sin target, salida, modelo, versión, run_id, snapshot, split, referencia Gold y latencia HTTP. Los ejemplos sintéticos permanecen locales; la carga de producción simulada selecciona únicamente las cohortes del plan registrado.

## Respaldo y actualización de versiones

Si el modelo no carga o no produce probabilidades válidas, se utiliza la regla del Dummy `most_frequent` del PSet 03. Su probabilidad de Fail es 0; los empates se resuelven con la misma política de cupos. La respuesta informa `respaldo=true` y el run_id real del baseline. No se usa silenciosamente una fixture longitudinal cuando falla el Registry.

Para demostrar el interruptor, utilizar una cohorte sintética nueva; un lote ya procesado conserva su respuesta original:

```sh
.venv/bin/python -m src.datos --ejemplo .local/ejemplo-respaldo --cohorte-id ejemplo-respaldo
PSET4_FORCE_FALLBACK=1 docker compose up -d --wait api
curl -X POST http://localhost:8004/predecir -H 'Content-Type: application/json' --data-binary @.local/ejemplo-respaldo/semana2.json
PSET4_FORCE_FALLBACK=0 docker compose up -d --wait api
```

La API resuelve el alias en cada lote nuevo y fija una versión durante todo ese lote. Se comprobó la recarga 1→2→1 sin reconstruir la imagen. La versión 2 de esa demostración contiene los mismos pesos y está etiquetada como prueba mecánica; no es un challenger reentrenado ni una mejora. Las dos versiones activas volvieron a 1. El ciclo de reentrenamiento, comparación y aprobación humana sigue pendiente.

## Reproducir las fixtures y exportar corridas

Las fixtures ya están incluidas. Para reconstruirlas deliberadamente se necesitan el Registry y el snapshot privado original; la ruta es un insumo de preparación, no una dependencia de ejecución de la API:

```sh
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 .venv/bin/python -m src.reentrenar --preparar-servicio --origen-local ../pset_3/.local
# Versionar el código antes de registrar una referencia nueva.
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 .venv/bin/python -m src.reentrenar --registrar-referencia
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 .venv/bin/python -m src.reentrenar --exportar-corridas
```

La referencia CI se registra como `fase=preparacion_servicio`, sin entrenamiento y con su commit. `docs/corridas.csv` reúne las corridas del experimento definitivo del PSet 03 y del experimento operativo. La preparación valida snapshot y fuente y conserva el champion histórico; una versión temprana activa diferente no se reemplaza automáticamente.

## CI y alcance pendiente

`.github/workflows/ci.yml` instala las dependencias fijadas, prueba con fixtures sin MLflow/Snowflake, construye la imagen y prueba dentro del contenedor en cada push/PR. En el fork del curso se mantiene una copia idéntica en `.github/workflows/ci.yml` de la raíz real del repositorio; GitHub no ejecuta por sí solo workflows dentro de una carpeta anidada. La prueba general del repositorio conserva el núcleo portable; las pruebas de fixtures nativas se ejecutan en el job dedicado con sus versiones y `PSET4_FULL_TESTS=1`.

Pendientes: ingesta integrada, Compose único con Kestra/Spark/MLflow/API/tablero, notebooks 01-07, reentrenamiento con pausa humana, CD/GHCR, análisis por subgrupos, CSV finales, pitch histórico en PDF, memo, presentación y video. [Cambios y evidencias](docs/cambios.md) distingue lo comprobado de lo pendiente.

Referencias técnicas: [pruebas del ciclo de vida de FastAPI](https://fastapi.tiangolo.com/advanced/testing-events/), [validación estricta de Pydantic](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/) y [alias del Model Registry](https://www.mlflow.org/docs/latest/registry/).


## Snowflake y lotes de control con Kestra

La continuidad del PSet 02 utiliza `pset_2/` como referencia; el proyecto integrado se ejecuta desde esta carpeta. No depende de `pset-02/`. Los modelos y el servicio MLflow histórico se conservan durante esta etapa.

En `.env` local configurar dos contraseñas nuevas y las rutas absolutas a los archivos privados Snowflake existentes. No copiar sus contenidos al repositorio. Las variables `SNOWFLAKE_CONNECTION_HOST_PATH` y `SNOWFLAKE_PRIVATE_KEY_HOST_PATH` apuntan al JSON de conexión (`schema_version=1`, `account`, `private_key_passphrase`) y la clave cifrada. El rol de servicio es `PSET2_PIPELINE`, usuario `PSET2_SVC`, warehouse `PSET2_WH`; requiere crear las nuevas tablas identificadas dentro de `PSET2_OULAD.ANALYTICS`, schema ya autorizado para el servicio. El código rechaza objetos existentes con otra marca. Las capas históricas se consultan como fuentes.

```sh
docker compose up -d --build --wait api postgres kestra
docker compose exec -T kestra python3 -m src.datos --preparar-plan --base-local /workspace/.local/operacion.sqlite
```

Kestra queda en `http://localhost:8094`, con usuario `admin@psets.local` y la contraseña privada configurada. Importar `kestra/produccion_lotes.yml` y ejecutar con `liberar_targets=false` conserva los resultados ocultos. El flujo recorre L01-L08 en orden y llama a la API internamente; tras una respuesta durable carga `PSET2_OULAD.ANALYTICS.PREDICCIONES`. Reintentar no asigna cupos nuevos. Una diferencia en una clave ya publicada aborta la carga, sin sobrescribirla.

Son ocho despachos de control de la presentación 2014J, ya examinada retrospectivamente en PSet 03. Los módulos ordenados se reparten circularmente en cuatro ondas de ediciones completas. Días simulados de despacho: 14–17 y 28–31, con features congeladas en 14/28. Las demoras de 0..3 días son un supuesto de cola; no equivalen a ocho semestres independientes. La política experimental conserva 10 % por edición y reparto 25/75, sin afirmar aprobación institucional ni cumplimiento de la meta de negocio.

Las solicitudes no contienen target. `ETIQUETAS` se materializa aparte solo cuando el reloj simulado alcanza fin de período +14 días; es una demora supuesta, porque OULAD no publica el instante real de disponibilidad. El flujo puede avanzar explícitamente al día 283 con `liberar_targets=true`, después de completar las ocho predicciones. El timestamp real de inferencia y el día simulado se guardan por separado. Los flujos también ejecutan el monitoreo antes y después de la disponibilidad de etiquetas.

```sh
# Repetición individual segura, una vez preparado el plan.
docker compose exec -T kestra python3 -m src.datos --procesar-lote L01 --base-local /workspace/.local/operacion.sqlite
# Verificar el horizonte antes de habilitar targets; no debe consultar resultados en día 31.
docker compose exec -T kestra python3 -m src.datos --liberar-etiquetas 31 --base-local /workspace/.local/operacion.sqlite
```

Los registros conservan entradas, salida, versión y run del modelo, snapshot, split, Gold, política, respaldo y latencia. `PLANES`, `LOTES_ENTRADA`, `LOTES_PROCESADOS` y `RELOJ` permiten auditar la secuencia. Solo hay un escritor de carga: concurrencia 1 en Kestra y exclusión local para ejecuciones CLI; no se afirma soporte para escritores distribuidos independientes.

Referencias: [conector Python de Snowflake](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example) y [bucles de Kestra](https://kestra.io/docs/how-to-guides/loop).

Validación ejecutada: 51 pruebas completas aprobadas localmente y en Docker. Se preservan los ocho controles y su repetición; el escenario de deriva completo terminó en SUCCESS. Hay 36.646 predicciones únicas entre ambos planes, 32 eventos de monitoreo y 28 alertas. `docs/predicciones.csv` incluye ambos planes; sus poblaciones y presupuestos se analizan por separado. La comparación contra el estático sigue pendiente.


## Monitoreo, deriva y tablero

```sh
docker compose up -d --build --wait api api_deriva monitoreo tablero kestra
```

El tablero está en `http://localhost:8504`; la API del escenario sintético usa `http://localhost:8006`. El monitor no publica un puerto al host. El servicio API conserva su registro local y carece de credenciales Snowflake; el worker de monitoreo realiza las consultas cloud. El tablero lee solo CSV de `docs/`, sin claves. El Compose usa `!override` para separar los puertos de las dos API y requiere una versión de Compose que lo admita. La integración de Spark y MLflow dentro del Compose único todavía está pendiente.

Importar primero `kestra/monitoreo.yml` y luego `kestra/produccion_lotes.yml`. Este último llama al monitor después de cada predicción. Ejecutar con `plan_id=oulad-2014j-deriva-v1` utiliza un SQLite separado, conserva las matrículas y cupos originales y modifica únicamente L06 y L07: permuta vectores completos de features dentro de cada edición, con semilla `5041+orden`, y suma 120 a `studied_credits`. Las etiquetas permanecen iguales y no participan de la alteración. Las demografías de esos dos lotes son sintéticas; la evaluación de equidad posterior usará los controles originales. El control no se sobrescribe.

`liberar_targets=true` habilita la revisión madura después de las predicciones. Se ordenan los eventos por disponibilidad completa del target y luego por día de predicción; DDD madura al día 276 y las otras ondas completas al 283. Una revisión de predicción consulta `ETIQUETAS` con `DIA_DISPONIBLE <= día_de_revisión`, aunque la tabla ya contenga resultados posteriores. Los 16 eventos de predicción exportados tienen AP vacía. Los IDs deterministas y el escritor serializado hacen segura la repetición.

La referencia `tests/fixtures/referencia_monitoreo.json` contiene perfiles del entrenamiento, bins y conteos completos, muestras deterministas de hasta 1000 valores numéricos para KS y métricas OOF por los cinco folds históricos. Compara el mismo corte y los módulos de cada onda; conserva también la CV global del PSet 03. Se validan sus hashes y snapshot y se excluyen estudiantes 2014J del desarrollo. La referencia, sus estadísticas y muestras también derivan de OULAD (The Open University, CC BY 4.0, [fuente](https://research.stem.open.ac.uk/ouanalyse/dataset/), DOI 10.1038/sdata.2017.171).

PSI usa bins congelados y pseudoconteo 0,5 por celda para evitar divisiones por cero, incluidos faltantes y categorías nuevas. 0,10 es una zona de vigilancia y >0,25 genera revisión en un lote con al menos 200 matrículas. Son umbrales operativos heurísticos predeclarados, no una prueba de causalidad. La duración curricular conserva PSI y rango como contexto, sin activar sola un incidente de comportamiento. KS es un respaldo aproximado con empates; chi-cuadrado agrupa categorías escasas y solo informa p cuando las frecuencias esperadas alcanzan 5. La decisión de deriva usa PSI. [Documentación de SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html).

El desempeño se evalúa con todos los targets de la base disponibles y al menos 20 Fail y 20 no-Fail. AP inferior a media OOF menos dos desviaciones estándar genera revisión; dos caídas consecutivas etiquetadas del mismo corte proponen estudiar un challenger. La dispersión entre folds no es un intervalo de confianza. Los cambios de prevalencia y mezcla se muestran para investigar diagnósticos posibles. Cambios de entradas sin caída de desempeño no proponen reentrenar. Una promoción requerirá comparación de negocio y aprobación humana en el siguiente bloque.

Cada alerta registra métrica, valor, umbral, ventana, severidad, receptor y acción en `ALERTAS` y en el log de Kestra. El receptor es un rol operativo; no se envían mensajes externos. `MONITOREO` conserva latencias p50/p95, solicitudes, errores, distribución de scores/decisiones, calidad de las 20 entradas, AP, TP/FP, precisión de propuestas nuevas y cobertura acumulada de la cohorte base, además de modelo, run y referencia.

Las peticiones nuevas llevan cabeceras de atribución operativa; esas cabeceras son solo telemetría, no autorización ni fuente del presupuesto. En los controles históricos sin esa atribución, las tasas de error por lote son desconocidas y se informa la latencia de su respuesta conciliada. En el escenario nuevo hay una solicitud batch por lote; el p95 de una observación no estima un SLA. El protocolo exige al menos 20 solicitudes para evaluar alertas de latencia >10 s, 5xx >1 % o 4xx >5 %. Estos límites son supuestos de demostración, no acuerdos institucionales.

El escenario sintético redujo los TP de las propuestas nuevas en L06 de 122 a 55 con 273 cupos y en L07 de 79 a 43 con 207 cupos. Esto ilustra el costo de perder focalización; no mide tutorías realizadas ni reprobaciones evitadas. L06/L07 del control también quedan bajo su referencia CV, por lo que la caída no se atribuye exclusivamente a la alteración. Dos controles originales generan avisos PSI cercanos a 0,26: control significa sin modificación manual, no población estacionaria. L08 conserva AP sobre su umbral y recibe solo revisión de datos, sin propuesta de entrenamiento. Se preservan los avisos; la calibración futura debe usar períodos nuevos y revisar prevalencia, composición, persistencia y costo de alarmas, sin reajustar el umbral con este benchmark ya observado.

```sh
# Revisión histórica segura de controles mediante el mismo motor.
docker compose exec -T monitoreo python -m monitoreo.deriva --plan oulad-2014j-control-v1 --fase prediccion
docker compose exec -T monitoreo python -m monitoreo.deriva --plan oulad-2014j-control-v1 --fase maduro
# Exportar después de completar los dos planes.
docker compose exec -T monitoreo python -m monitoreo.deriva --exportar /app/.local/monitoreo-export
docker compose exec -T kestra python3 -m src.datos --exportar-escenarios /workspace/.local/predicciones-escenarios.csv
cp .local/monitoreo-export/monitoreo.csv .local/monitoreo-export/alertas.csv docs/
cp .local/predicciones-escenarios.csv docs/predicciones.csv
```

Para reconstruir deliberadamente la referencia, con el snapshot y los OOF privados originales: `PYTHONPATH=. .venv/bin/python -m monitoreo.deriva --preparar-referencia ../pset_3/.local`. La ejecución ordinaria usa la referencia publicada y funciona sin importar módulos históricos.

El próximo bloque debe reservar el último lote etiquetado de comparación y excluir sus matrículas de todos los cortes y de ambos escenarios al armar entrenamiento. No mezclar control y escenario sintético como si fueran muestras independientes. La comparación con el estático a igual cupo, el escenario presupuestario del 30 %, la equidad y la decisión de negocio siguen pendientes.
