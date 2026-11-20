# Proyecto final: apoyo académico preventivo

Estado: **servicio batch implementado y verificado**, con modelos específicos de semanas 2 y 4, contrato Pydantic, registro transaccional, respaldo, fixtures y CI. La carga Snowflake y los ocho despachos de control quedaron verificados (18.323 predicciones únicas). Monitoreo, deriva y tablero quedaron verificados con controles y un escenario sintético separado. El challenger se reentrenó, comparó y rechazó por decisión humana; Kestra terminó en SUCCESS y el champion permanece en versión 1. La imagen GHCR y la recarga/rollback técnica quedaron verificadas. Los entregables de comunicación siguen pendientes. Este Compose integra las API de control y escenario sintético, Kestra/PostgreSQL, monitor y tablero, utilizando el Registry existente; todavía no es el Compose único de los cinco servicios finales.

## Objetivo de negocio

Al menos **10 % de mejora relativa en cobertura de Fail frente al modelo estático, con iguales cupos**, durante el período en curso. La cobertura es `TP / Fail de la cohorte base` y la mejora relativa es `cobertura_longitudinal / cobertura_estatica - 1`. Con 500 Fail, 200 cupos y 100 TP del estático, la meta exige 110 TP: 22 % de cobertura frente a 20 %. Si la cobertura estática es cero, la razón no se define.

Control estático, Dummy y política reactiva son comparadores distintos. El adelanto del 30 % de la atención reactiva futura es un escenario presupuestario; la bolsa reactiva vigente se protege. Los cupos y el reparto experimentales no son fondos institucionales aprobados. Las propuestas requieren revisión humana; no equivalen a tutorías realizadas ni a reprobaciones evitadas.

## Estructura y continuidad

Se conserva el árbol de la rúbrica. `dbt/` y `spark/` contienen las fuentes del PSet 02 sin alterar; `src/pipeline.py` conserva byte a byte la preparación del PSet 03. Los tres memos anteriores están en `docs/historial/`; el pitch histórico y los notebooks integrados aún están pendientes. Las carpetas vacías usan `.gitkeep` solo para conservar su estructura. `.dockerignore` impide enviar entornos, credenciales y datos privados al build.

Los champions tempranos reutilizan los artefactos completos del PSet 03. Se reentrenó un challenger de semana 4 conservando la preparación y los hiperparámetros, sin repetir tuning. Los nombres son `oulad-apoyo-academico-semana2-modelo@champion` y `oulad-apoyo-academico-semana4-modelo@champion`. Ambos se sirven por versiones iniciales específicas de su corte. El champion histórico del día 56 permanece intacto. Este uso es experimental y no constituye validación prospectiva independiente.

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

Instrucciones del portal, ejemplos y solución de errores: [guía de usuario](docs/guia_usuario.md).

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

La API resuelve el alias en cada lote nuevo y fija una versión durante todo ese lote. Se comprobó la recarga 1→2→1 sin reconstruir la imagen. La versión 2 de esa demostración contiene los mismos pesos y está etiquetada como prueba mecánica; no es un challenger reentrenado ni una mejora. Las dos versiones activas volvieron a 1. El ciclo real ya entrenó un challenger distinto, registrado como versión 2 de semana 4; la comparación recomendó rechazarlo y Wilmer Puerta confirmó ese rechazo. Los champions siguen en versión 1.

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

Pendientes: ingesta integrada, Compose único con Kestra/Spark/MLflow/API/tablero, notebooks 01-07, CSV finales, pitch histórico en PDF, memo, presentación y video. [Cambios y evidencias](docs/cambios.md) distingue lo comprobado de lo pendiente.

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

Validación ejecutada: 69 pruebas completas aprobadas localmente y en Docker. Se preservan los ocho controles y su repetición; el escenario de deriva completo terminó en SUCCESS. Hay 36.646 predicciones únicas entre ambos planes, 32 eventos de monitoreo y 28 alertas. `docs/predicciones.csv` incluye ambos planes; sus poblaciones y presupuestos se analizan por separado. La comparación de reentrenamiento sobre L08 incluye el estático con los mismos cupos; la comparación completa por lote ya quedó calculada y documentada.


## Monitoreo, deriva y tablero

```sh
docker compose up -d --build --wait api api_deriva monitoreo tablero kestra
```

El tablero está en `http://localhost:8504`; la API del escenario sintético usa `http://localhost:8006`. El monitor no publica un puerto al host. El servicio API conserva su registro local y carece de credenciales Snowflake; el worker de monitoreo realiza las consultas cloud. El tablero lee solo CSV de `docs/`, sin claves. El Compose usa `!override` para separar los puertos de las dos API y requiere una versión de Compose que lo admita. La integración de Spark y MLflow dentro del Compose único todavía está pendiente.

Importar primero `kestra/reentrenamiento.yml`, después `kestra/monitoreo.yml` y luego `kestra/produccion_lotes.yml`. Este último llama al monitor después de cada predicción. Ejecutar con `plan_id=oulad-2014j-deriva-v1` utiliza un SQLite separado, conserva las matrículas y cupos originales y modifica únicamente L06 y L07: permuta vectores completos de features dentro de cada edición, con semilla `5041+orden`, y suma 120 a `studied_credits`. Las etiquetas permanecen iguales y no participan de la alteración. Las demografías de esos dos lotes son sintéticas; la evaluación de equidad posterior usará los controles originales. El control no se sobrescribe.

`liberar_targets=true` habilita la revisión madura después de las predicciones. Se ordenan los eventos por disponibilidad completa del target y luego por día de predicción; DDD madura al día 276 y las otras ondas completas al 283. Una revisión de predicción consulta `ETIQUETAS` con `DIA_DISPONIBLE <= día_de_revisión`, aunque la tabla ya contenga resultados posteriores. Los 16 eventos de predicción exportados tienen AP vacía. Los IDs deterministas y el escritor serializado hacen segura la repetición.

La referencia `tests/fixtures/referencia_monitoreo.json` contiene perfiles del entrenamiento, bins y conteos completos, muestras deterministas de hasta 1000 valores numéricos para KS y métricas OOF por los cinco folds históricos. Compara el mismo corte y los módulos de cada onda; conserva también la CV global del PSet 03. Se validan sus hashes y snapshot y se excluyen estudiantes 2014J del desarrollo. La referencia, sus estadísticas y muestras también derivan de OULAD (The Open University, CC BY 4.0, [fuente](https://research.stem.open.ac.uk/ouanalyse/dataset/), DOI 10.1038/sdata.2017.171).

PSI usa bins congelados y pseudoconteo 0,5 por celda para evitar divisiones por cero, incluidos faltantes y categorías nuevas. 0,10 es una zona de vigilancia y >0,25 genera revisión en un lote con al menos 200 matrículas. Son umbrales operativos heurísticos predeclarados, no una prueba de causalidad. La duración curricular conserva PSI y rango como contexto, sin activar sola un incidente de comportamiento. KS es un respaldo aproximado con empates; chi-cuadrado agrupa categorías escasas y solo informa p cuando las frecuencias esperadas alcanzan 5. La decisión de deriva usa PSI. [Documentación de SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html).

El desempeño se evalúa con todos los targets de la base disponibles y al menos 20 Fail y 20 no-Fail. AP inferior a media OOF menos dos desviaciones estándar genera revisión; dos caídas consecutivas etiquetadas del mismo corte proponen estudiar un challenger. La dispersión entre folds no es un intervalo de confianza. Los cambios de prevalencia y mezcla se muestran para investigar diagnósticos posibles. Cambios de entradas sin caída de desempeño no proponen reentrenar. La comparación ya se ejecutó y la pausa se reanudó con el rechazo humano; el flujo terminó en SUCCESS sin promoción.

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

El reentrenamiento reserva L08 y excluye todas sus personas de la ventana. No mezcla control y escenario sintético como muestras independientes. El escenario presupuestario del 30 %, la equidad y la evaluación final del resultado de negocio siguen pendientes.


## Reentrenamiento y revisión humana

La alerta madura de L07 del escenario sintético inició el ciclo `reentrenamiento-28-deriva-v1`. Kestra ejecutó la preparación, entrenamiento y comparación, esperó en `aprobacion` (PAUSED) y terminó en SUCCESS después del rechazo explícito de Wilmer Puerta, ejecución `6lcaE9ak8kGv4myx06ZMMw`. [Resultado, límites y criterio](docs/cambios.md#resultado-del-reentrenamiento-y-pausa-humana-19-nov-2026).

Con 147 cupos, el champion detecta 77 Fail, el challenger 81 y el estático 54. El challenger mejora cuatro detecciones; la regla congelada exige al menos siete para superar una sigma de cobertura. **No es elegible para promoción; el responsable confirmó el rechazo y se conservó el champion.** La meta de +10 % relativo frente al estático se supera en esta comparación local, sin demostrar un resultado causal o una validación prospectiva del objetivo global.

`docs/reentrenamientos.csv` contiene SOLICITADO, COMPARADO, DECISION_SOLICITADA y DECIDIDO; el último evento registra RECHAZADO, responsable, motivo y reanudación de la pausa. `docs/corridas.csv` incluye el nuevo entrenamiento (384 corridas históricas en total). Los aliases de semana 2 y 4 y el champion histórico permanecen sin modificación. El candidato se conserva como `@challenger` para auditoría, con `estado_aprobacion=rechazado` en el run y en su versión del Registry.

Para reproducir la preparación privada en un entorno con los datos históricos restaurados, antes de solicitar un ciclo nuevo:

```sh
PYTHONPATH=. .venv/bin/python -m src.reentrenar --preparar-recursos --origen-local ../pset_3/.local
# Con Registry en 5001, Snowflake y los flujos importados:
docker compose up -d --build --wait api api_deriva monitoreo tablero kestra
docker compose exec -T monitoreo python -m src.datos --reentrenar solicitar
```

La referencia pública fija el protocolo y sus cinco folds; `.local/reentrenamiento/` conserva el histórico privado, sus hashes, snapshot y checkpoint. El comando valida el código y datos antes de entrenar; el mismo ciclo se reutiliza sin duplicar el ajuste. Un cambio de datos, protocolo o champion requiere revisar/versionar el ciclo. El target solo entra una vez maduro; la reserva de comparación jamás se añade al entrenamiento. La operación ordinaria corre desde este proyecto y no importa módulos del PSet 02/03.

El rechazo/aprobación se registra desde la tarea Pause de Kestra con decisión, responsable y motivo. El worker verifica esos inputs en la ejecución real antes de modificar un alias. Una aprobación no puede saltarse la regla cuantitativa. `--reentrenar rollback` exige una promoción aprobada previa y responsable/motivo explícitos; la recarga/rollback técnica se verificó en un servicio aislado con la imagen publicada. No hubo promoción del candidato rechazado.


## Publicación de código en GHCR

`.github/workflows/cd.yml` publica en cada integración a `main`, después de ejecutar el CI reutilizable. Construye `linux/amd64`, ejecuta las 69 pruebas dentro de esa imagen exacta y solo entonces publica `ghcr.io/wilmerpuerta/oulad-proyecto-final-api:<SHA_COMPLETO_DEL_COMMIT>`. El resumen y el artefacto `imagen-publicada-<SHA>` guardan el digest, commit, plataforma y ejecución. Un fallo de CI, build o pruebas impide publicar.

Los workflows efectivos están en `.github/workflows/` de la raíz real del repositorio del curso; los de este directorio conservan la definición canónica para la entrega. `master` y su historial se conservan; `main` es la rama de integración del despliegue. El PR #1 se integró con las pruebas aprobadas; la imagen se publicó y descargó desde GHCR y se verificó en los cuatro servicios. El repositorio del curso conserva `master` como rama histórica y predeterminada; los cambios de este bloque están en `main`.

Para utilizar una versión publicada, copiar del resumen el valor completo `PSET4_API_IMAGE=ghcr.io/...@sha256:...` a `.env` y ejecutar:

```sh
docker compose pull api api_deriva monitoreo tablero
docker compose up -d --no-build --pull never --wait api api_deriva monitoreo tablero
curl --fail http://localhost:8004/salud
curl --fail http://localhost:8004/modelo
```

`PSET4_API_IMAGE` es obligatorio: se fija un commit o, preferiblemente, un digest. Para desarrollo local se puede establecer explícitamente `proyecto-final-api:local` y construir con `docker compose build api`. El servicio Kestra mantiene por ahora su construcción local; el Compose único con MLflow/Spark sigue pendiente.

GHCR puede exigir autenticación si el paquete permanece privado. Para descargar una imagen privada, configurar fuera del repositorio un token clásico con `read:packages` y usar `docker login ghcr.io --username <usuario> --password-stdin`. Nunca guardar el token en `.env`, notebooks o archivos versionados. Un paquete público permite descarga anónima; su visibilidad se administra aparte de la del repositorio.

El despliegue de código no promueve modelos: el Registry mantiene sus aliases y la API los consulta para cada lote nuevo. El challenger rechazado continúa rechazado. La selección/promoción del modelo conserva su control de negocio y supervisión humana.


### Primer despliegue CD comprobado (19-nov-2026)

Primer release verificado: `ghcr.io/wilmerpuerta/oulad-proyecto-final-api:97e9a18003554e1d0de5287fb87c0f23812557f5`. Referencia histórica del primer despliegue:

```text
ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:bc5ff9e0b215795b3388bc4da526ea6bece369404f8ed2c7b4a24d6fda16cae5
```

[Publicación automática](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44660981181) desde el [PR #1](https://github.com/wilmerpuerta/data-science-end-to-end/pull/1), con CI y pruebas de la imagen final aprobados. API, API sintética, monitor y tablero quedaron healthy con esa referencia y la etiqueta OCI de revisión `97e9a18003554e1d0de5287fb87c0f23812557f5`. Se conservaron los conteos de ambos SQLite y los modelos servidos en semanas 2 y 4.

La prueba de recarga usó el modelo aislado `oulad-apoyo-academico-recarga-cd-semana2`: dos versiones de los mismos pesos históricos, marcadas como prueba, sin entrenamiento. Una instancia separada de la misma imagen observó 1→2→1 y produjo 120 predicciones sintéticas; conservaron imagen, contenedor y probabilidades. Los aliases operativos permanecieron en 1 durante toda la prueba y el candidato de semana 4 siguió rechazado. Las predicciones de prueba están en otro SQLite y no entran a Snowflake, presupuestos productivos ni CSV de negocio. Se retira la instancia aislada después de verificarla.

Para revertir **código**, restaurar en `.env` el digest anterior conservado en el registro de despliegue y ejecutar `docker compose up -d --no-build --pull never --wait api api_deriva monitoreo tablero`; descargar antes esa referencia si no está en caché. Para revertir **modelo**, restaurar el alias a la versión previamente aprobada en el Registry; la API lo resuelve en el siguiente lote nuevo. No borrar volúmenes ni modificar el historial de predicciones. La decisión de modelo sigue separada de la publicación de código.


## Ética y respaldo

La auditoría original por discapacidad declarada y sus criterios de revisión están en [cambios y decisiones](docs/cambios.md#ética-operativa-resultados-y-responsabilidades-20-nov-2026). El agregado no cruza el límite experimental; L06 presenta una brecha de cobertura de −8,20 puntos y requiere revisión académica. No se afirma igualdad de oportunidades ni aceptación institucional. Los modelos y cupos se mantienen.

`PSET4_FORCE_FALLBACK=1` activa, al recrear API/API sintética, una cola administrativa sin estimación individual. La respuesta añade `puntuacion_individual=false` y un mensaje operativo; el valor numérico técnico del Dummy no significa riesgo cero. Las respuestas previas permanecen inmutables. [Procedimiento para operar el interruptor](docs/guia_usuario.md#operación-del-respaldo-y-revisión-de-necesidades).

El análisis se reproduce con `python -m monitoreo.deriva --etica <directorio_privado> --codigo-etica <SHA_DE_CODIGO>` dentro del worker con credenciales Snowflake; usa únicamente controles y etiquetas ya maduras. La evaluación de negocio quedó calculada; notebooks, Compose único y comunicación siguen pendientes.


### Imagen ética activa y comprobación del interruptor

La imagen activa y fijada en `.env.example` es `ghcr.io/wilmerpuerta/oulad-proyecto-final-api@sha256:e32f542e7320ae939625586d5ce8776fd1ac1933b596cb62b7676e98973ed2a3`, publicada desde el commit `6c392a3fc7d86e0774fc207d37f19bbc66768c07` mediante el [CD aprobado](https://github.com/wilmerpuerta/data-science-end-to-end/actions/runs/44722770969). La API, API sintética, monitor y tablero quedaron healthy con esa referencia. Se conservaron versiones, runs y snapshots de los modelos y todos los conteos de los SQLite operativos; los únicos campos nuevos en `/modelo` explicitan el método de priorización.

La prueba HTTP utilizó un servicio aislado con esa misma imagen y `PSET4_FORCE_FALLBACK` en secuencia 0→1→0, recreando el contenedor al cambiar la configuración. Produjo 160 predicciones sintéticas: normal (40), respaldo en semanas 2/4 (80), y reactivado (40). El respaldo reservó 1+3 cupos de su propia cohorte, mantuvo la validación 422 y devolvió las respuestas anteriores sin recalcular. La reactivación tampoco reemplazó respuestas históricas de respaldo. La puntuación técnica constante quedó marcada como no individual. La instancia de prueba se retiró y sus datos no entran a Snowflake ni a los CSV de negocio.

El champion sigue en versión 1, el candidato de semana 4 continúa rechazado y el respaldo no está forzado en los servicios operativos. La señal de L06 queda para revisión académica; no se declara una aprobación institucional de equidad. El resultado de negocio y los escenarios presupuestarios están documentados; siguen pendientes notebooks y cierre de integración/comunicación.


## Resultado de negocio

El control original cumple la meta: **420 Fail frente a 314** del estático, con **920 cupos**, +33,76 % relativo. Son 106 casos netos por matrícula, sin aumentar cupos. L03 empata; L07 bajo deriva queda por debajo del estático. La bolsa futura ilustrativa de 920 permite adelantar 274 y conserva 646; no se demuestra ahorro. [Comparación completa, rondas y escenarios](docs/cambios.md#resultado-de-negocio-focalización-oportunidad-y-presupuesto-20-nov-2026).

La evaluación se reproduce con `python -m src.reentrenar --evaluar-negocio <directorio_privado> --codigo-negocio <SHA_DEL_CODIGO>` dentro del worker. Solo lee Snowflake/Registry, usa los estáticos congelados y los scores históricos, sin entrenar ni modificar registros. En el tablero, la comparación se muestra por escenario y horizonte; el grupo de datos se mantiene separado entre control y deriva. Las alternativas de presupuesto y calendario son contrafactuales de análisis, no cambios aprobados de la operación.
