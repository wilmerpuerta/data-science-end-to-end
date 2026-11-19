# PSet 3: experimentación y selección del modelo

Esta es la carpeta de entrega **`pset_3/`**, con los archivos de la rúbrica directamente en su raíz. Los notebooks, `src/` y `docs/` son carpetas reales; no se necesita entrar en una carpeta `v2/` ni resolver enlaces simbólicos.

## Entregables

- [Documento técnico de seis páginas](docs/PSet3_memo_Puerta_Wilmer.pdf).
- [Notebooks 01-05 con salidas guardadas](notebooks/); el análisis de anticipación está en `notebooks/anexos/06_anticipacion.ipynb`.
- [Corridas exportadas](docs/corridas.csv), [auditoría](docs/auditoria-rubrica.md) y [gráfico de tuning](docs/tuning/default_vs_ajustado.svg).
- Champion: `models:/oulad-apoyo-academico-v2-modelo@champion`, HGB versión 1. Challenger: logística versión 2.

Se conserva el nombre del PDF acordado con el autor: primer apellido y nombre. El análisis, los modelos, las particiones, las métricas, el PDF y los run_ids históricos proceden de la experimentación definitiva del PSet 03. El empaquetado no constituye un experimento nuevo. El generador también guarda el PDF directamente en `docs/`; la entrega no contiene `output/pdf/`.

La carpeta incluye además `config/`, `prompts/`, `scripts/`, `tests/` y `mlflow/`: contienen dependencias reales del código y del servidor. El árbol de la rúbrica muestra los archivos mínimos, no todas estas dependencias.

## Instalación

Trabajar desde esta carpeta dentro del clon Git que conserva el historial del proyecto:

```sh
cd pset_3
uv python install 3.11.16
uv venv --python 3.11.16 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements.lock.txt
cp .env.example .env
docker compose up -d mlflow
```

MLflow usa `http://127.0.0.1:5001` y volúmenes persistentes de SQLite y artefactos. El nombre Compose se conserva para poder usar la evidencia local existente. Para restaurar en otra máquina, se necesitan el backend, los artefactos y la imagen del respaldo privado: levantar un servidor vacío no recupera el Registry. No borrar los volúmenes de evidencia.

## Snowflake e insumos congelados

El estudio consume el snapshot de la OBT `PSET2_OULAD.ANALYTICS.OBT_FEATURES` y los outcomes exportados desde PSet 02. No consulta Snowflake en vivo durante la reproducción. La configuración de la conexión y reconstrucción de Raw-Bronze-Silver-Gold-OBT está descrita en el README de PSet 02 del mismo proyecto. Las credenciales se configuran fuera de Git; una extracción nueva no reemplaza el snapshot original.

El paquete público excluye `.local/`, datos privados, respuestas de API, predicciones individuales, entornos y volúmenes. Para reproducir exactamente, importar los bundles originales y restaurar el servidor desde el respaldo. Con la carpeta privada original disponible:

```sh
.venv/bin/python scripts/preparar_runtime_local.py --origen-local /ruta/privada/.local
```

La reproducción de champion necesita también `.local/seleccion/predicciones_prueba.parquet` del respaldo. La auditoría global necesita el libro de costos histórico `.local/llm/costos.json`; no crear uno vacío para representar el consumo original. No se requieren llamadas nuevas a OpenAI para verificar champion.

Las llamadas nuevas al LLM son opcionales y separadas de la entrega. Si se realizan deliberadamente, las credenciales se leen de `.secrets/pset3-openai.env` dentro de esta carpeta o de las variables `OPENAI_*` del entorno; no se incluyen claves. Se conserva el tope histórico de USD 10 y el gasto registrado, sin reiniciar su libro.

## Orden de ejecución

Seleccionar el kernel preparado mediante `JUPYTER_PATH=.local/share/jupyter` y ejecutar Restart/Run All:

1. `notebooks/01_eda.ipynb`.
2. `notebooks/02_features.ipynb`.
3. `notebooks/03_baseline_candidatos.ipynb`.
4. `notebooks/04_tuning.ipynb`.
5. `notebooks/05_seleccion.ipynb`.
6. Opcional para ampliar el negocio: `notebooks/anexos/06_anticipacion.ipynb`.

Para ejecutar los seis de forma consecutiva en kernels nuevos: `.venv/bin/python scripts/ejecutar_notebooks_entrega.py`.

Los notebooks de entrega recalculan EDA y preparación y verifican resultados, decisiones y reproducción desde las evidencias originales. Los run_ids que muestran son referencias históricas; no se registran nuevos entrenamientos ni nuevas corridas al releer la entrega. Los scripts de ejecución del estudio se conservan para una repetición deliberada y separada, sujeta al protocolo y los recursos privados.

```sh
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/reproducir.py
.venv/bin/python scripts/auditar_entrega.py
```

El pytest general del repositorio omite las pruebas que requieren recursos privados; se habilitan con `PSET3_PYTEST=1` cuando se proporciona el entorno preparado. Los manifiestos `docs/01-verificacion.json` a `06-verificacion.json` identifican la ejecución guardada de esta distribución.

## Resultados y límites

Dos baselines, seis familias incluido GPT prompting y 30 configuraciones por cada una de las tres familias mejor clasificadas por negocio. El criterio es cobertura de Fail con cupo del 10 % por edición. El control estático es distinto del Dummy y de la política reactiva.

HGB obtiene en la prueba reutilizada 465 TP de 1.947 Fail con 872 cupos, frente a 309 TP de su control estático. La logística obtiene 477 TP; no se cambia el ganador usando prueba. La ventaja CV del champion no supera la dispersión entre folds. Los resultados de tutorías son simulaciones de focalización, no reprobaciones evitadas.

2014J ya se había observado: no se presenta como un hold-out nuevo. GPT fue evaluado mediante prompting; su adopción externa queda como decisión posterior de costo-beneficio con la Universidad. El gasto experimental conservador fue USD 1,1167655.

La [enmienda de portabilidad](docs/enmienda-portabilidad.json) registra la detección de raíz Git y la ubicación local de credenciales. Conserva las fuentes anteriores y verifica hashes antes/después. La preparación, modelos, datos, métricas y decisiones permanecen iguales. No se reescriben los protocolos ni los commits de los entrenamientos.
