# Proyecto final: apoyo académico preventivo

Estado: **servicio batch implementado y verificado**, con modelos específicos de semanas 2 y 4, contrato Pydantic, registro transaccional, respaldo, fixtures y CI. La carga Snowflake y los ocho despachos de control quedaron verificados (18.323 predicciones únicas). La deriva, el reentrenamiento con aprobación, el tablero y los entregables de comunicación siguen pendientes. Este Compose integra API, Kestra y su PostgreSQL, utilizando el Registry existente; todavía no es el Compose único de los cinco servicios finales.

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
uv pip sync --python .venv/bin/python --only-binary=:all: --require-hashes requirements.txt
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

Pendientes: ingesta integrada, Compose único con Kestra/Spark/MLflow/API/tablero, notebooks 01-07, validación final de simulación temporal, Snowflake MONITOREO, deriva y alertas, reentrenamiento con pausa humana, CD/GHCR, análisis por subgrupos, CSV finales, pitch histórico en PDF, memo, presentación y video. [Cambios y evidencias](docs/cambios.md) distingue lo comprobado de lo pendiente.

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

Las solicitudes no contienen target. `ETIQUETAS` se materializa aparte solo cuando el reloj simulado alcanza fin de período +14 días; es una demora supuesta, porque OULAD no publica el instante real de disponibilidad. El flujo puede avanzar explícitamente al día 283 con `liberar_targets=true`, después de completar las ocho predicciones. El timestamp real de inferencia y el día simulado se guardan por separado. La deriva inducida y el monitoreo de estos controles corresponden al siguiente bloque.

```sh
# Repetición individual segura, una vez preparado el plan.
docker compose exec -T kestra python3 -m src.datos --procesar-lote L01 --base-local /workspace/.local/operacion.sqlite
# Verificar el horizonte antes de habilitar targets; no debe consultar resultados en día 31.
docker compose exec -T kestra python3 -m src.datos --liberar-etiquetas 31 --base-local /workspace/.local/operacion.sqlite
```

Los registros conservan entradas, salida, versión y run del modelo, snapshot, split, Gold, política, respaldo y latencia. `PLANES`, `LOTES_ENTRADA`, `LOTES_PROCESADOS` y `RELOJ` permiten auditar la secuencia. Solo hay un escritor de carga: concurrencia 1 en Kestra y exclusión local para ejecuciones CLI; no se afirma soporte para escritores distribuidos independientes.

Referencias: [conector Python de Snowflake](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example) y [bucles de Kestra](https://kestra.io/docs/how-to-guides/loop).

Validación ejecutada: 43 pruebas completas aprobadas localmente y en Docker; dos ejecuciones Kestra SUCCESS (original y repetición), 18.323 predicciones únicas, 920 propuestas sin duplicación y 9.231 etiquetas liberadas explícitamente al día simulado 283. `docs/predicciones.csv` contiene solo el plan de control. El monitoreo y la comparación contra el estático todavía no están calculados.
