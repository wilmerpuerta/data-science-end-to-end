# PSet 3: experimentación y selección por el criterio del negocio

Versión final reconstruida: **v2**, 18-nov-2026. La carpeta canónica de ejecución es `pset-03/v2/`. Los accesos `pset-03/src`, `notebooks`, `scripts`, `tests`, `docs`, `output` y requisitos enlazan a esta versión para conservar las rutas de entrega. Los symlinks no duplican experimentos. La versión anterior quedó en respaldos privados verificados; sus métricas no se presentan como ejecuciones nuevas.

## Resultado y entregables

- Champion: **HistGradientBoosting**, `oulad-apoyo-academico-v2-modelo@champion`, versión 1; challenger logística, versión 2. Champion maximiza la media CV de cobertura de Fail a cupo fijo. Su ventaja no supera la dispersión entre folds y no demuestra superioridad económica.
- Prueba retrospectiva reutilizada: 465 Fail captados / 1.947 con K=872; AP 0,4265069557086188; cobertura 0,23882896764252695. Frente al HGB estático ajustado independientemente: 309 TP, +156 / +50,49 %. No es un efecto causal de tutorías. Logística captura 477 en prueba; no se reelige después de observarla.
- Dos baselines antes de seis familias, incluido GPT mediante prompting; tuning de las tres primeras por negocio con 30 configuraciones cada una. Controles estáticos separados del Dummy; política reactiva con prevención cero y capacidad posterior acotada.
- [Memo de seis páginas](docs/PSet3_memo_Puerta_Wilmer.pdf), [fuente editable](memo-pset3.md), [corridas](docs/corridas.csv), [decisión previa](docs/negocio/finalistas.json), [reproducción exacta](docs/seleccion/reproduccion-champion.json), [auditoría](docs/auditoria-rubrica.md).
- Seis notebooks ejecutados en kernels nuevos: EDA, features, baselines/candidatos, tuning, selección y anexo de anticipación. Los manifiestos `docs/01-verificacion.json` a `06-verificacion.json` registran hashes y ejecución.

## Prompting: respuesta y decisión posterior

**Sí es factible y se ensayó.** La adopción de un LLM externo es una decisión de negocio posterior: evaluar consumo, latencia, integración, mantenimiento y valor incremental con la Universidad mediante un análisis de costo-beneficio. El consumo conservador de este proyecto fue USD 1,1167655 de un tope autorizado de USD 10, incluyendo pilotos y fallos; no demuestra un gasto elevado en esta muestra ni estima el costo anual. El GPT evaluado tuvo menor cobertura CV que los modelos tabulares y no ingresó al top 3 de tuning. No se justifica su omisión por falta de GPU.

El GPT no ajusta sus pesos con todas las matrículas: usa 18 ejemplos y las proporciones de clases del train-fold. La preparación y todas las filas de validación son las mismas para los seis modelos; la métrica de train usa las mismas 1.000 filas por fold. Ver [protocolo de prompting](docs/prompting.md). El preentrenamiento del proveedor es desconocido y no se garantiza determinismo del servicio; las respuestas se archivan para reproducción.

## Entorno y servidor

Desde la raíz del paquete `oulad/` (o la raíz local de este proyecto):

```sh
uv python install 3.11.16
uv venv --python 3.11.16 pset-03/v2/.venv
uv pip sync --python pset-03/v2/.venv/bin/python --require-hashes pset-03/v2/requirements.lock.txt
docker compose -f pset-03/docker-compose.yml up -d mlflow
```

El Dockerfile fija las versiones reales del servidor en `pset-03/mlflow/requirements.lock.txt`; SQLite y artefactos viven en volúmenes persistentes. Tracking: `http://127.0.0.1:5001`; experimento definitivo `oulad-apoyo-academico-v2`. Los dos intentos técnicos previos tienen nombres separados y se conservan. No ejecutar `docker compose down -v` sobre las evidencias.

## Recursos privados y alcance de reproducción

GitHub y el ZIP público excluyen `.env`, `.secrets`, `.local`, entornos, CSV originales, respuestas individuales, predicciones privadas, modelos serializados y volúmenes. **El paquete público no es una réplica autónoma del servidor ni del snapshot privado.** Para reproducir exactamente este estudio se necesitan sus bundles congelados y los volúmenes/imágenes del respaldo privado final; para las figuras y tablas basta la evidencia agregada incluida.

El snapshot y las particiones se verifican por SHA-256, IDs `0a75615bd8ff...` y `231cd638f375...`. No hay consultas Snowflake en vivo durante el estudio. Para reconstruir fuentes, seguir `pset-02/README.md` y su configuración privada de Snowflake/OBT; una extracción nueva tiene otra identidad y exige un protocolo nuevo. No sustituir un bundle congelado por un Parquet externo ni alterar sus manifiestos.

Con el bundle original disponible en una ubicación privada, preparar punteros y kernel usando `scripts/preparar_runtime_local.py --origen-local /ruta/privada/.local`. Para el servidor exacto, restaurar los archivos backend/artifacts y la imagen desde el respaldo privado, conforme a su manifiesto; levantar un servidor vacío no recupera las versiones del Model Registry.

La clave OpenAI se configura fuera del repositorio versionado, en `.secrets/pset3-openai.env` de la raíz del paquete. El modelo es `gpt-6-luna`; Responses, JSON Schema por consultas, razonamiento none, lotes de 32 y hasta ocho peticiones concurrentes. El libro `.local/llm/costos.json` conserva gasto y reservas globales y nunca se reinicia para eludir el presupuesto. No se requieren llamadas nuevas para reproducir champion. ChatGPT y API tienen facturación independiente.

## Orden, pruebas y reproducción

El protocolo, las seis búsquedas predeclaradas y sus enmiendas están en `config/` y `docs/protocolo-congelado.json` / `enmienda-*.json`. Los commits históricos son reales y se conservan en Git; las enmiendas técnicas no cambian las filas, folds, prompts, probabilidades ya usadas ni el criterio predictivo. Se contrastaron 283 respuestas para corregir lectura de `final_answer`, con cero diferencias de probabilidades. Los rechazos sin inferencia tienen como máximo un reintento por hash según enmienda, con reservas conservadoras; errores ambiguos o respuestas sin validación detienen la fase.

```sh
pset-03/v2/.venv/bin/python -m unittest discover -s pset-03/v2/tests -v
pset-03/v2/.venv/bin/python pset-03/v2/scripts/reproducir.py
pset-03/v2/.venv/bin/python pset-03/v2/scripts/auditar_entrega.py
```

Para una ejecución deliberada del estudio: `scripts/ejecutar_estudio.py`, desde el entorno v2. Comprueba fuente limpia en Git y protocolo congelado; recupera checkpoints ya existentes. No vuelve a usar prueba para seleccionar. `scripts/ejecutar_notebooks_finales.py` hace Restart/Run All de 03-06 desde kernels nuevos al completar el estudio; 01 y 02 se ejecutan con `scripts/ejecutar_preparacion.py`. Reproducir métricas ya registradas no equivale a buscar otra vez sobre prueba.

El pytest general del fork omite las pruebas locales de PSet 3 para no intentar cargar snapshots/MLflow privados. Las 48 pruebas se ejecutaron explícitamente con unittest; se puede habilitar su colección pytest con `PSET3_PYTEST=1` si se proporcionan dependencias y recursos. Esto no sustituye las pruebas del pipeline PSet 2.

## Anticipación y límites

Las semanas 2/4/6 tienen cohortes propias, sin condicionar elegibilidad futura en día 56. Un solo presupuesto nace de día 14, sin repetir matrícula, y también se informan estudiantes únicos. Plazos de coordinación/apoyo y días 56/70 son escenarios no validados con una institución. La asociación de ausencia de registros y su incremento predictivo se evalúan separadamente, sin causalidad. Ver el anexo 06.

2014J ya fue observado en v1: es benchmark retrospectivo reutilizado, no un nuevo hold-out independiente. La maduración/publicación de etiquetas y el impacto causal requieren validación prospectiva y piloto. No se afirma despliegue real ni beneficio monetario realizado.

## PDF y publicación

El generador `scripts/generar_memo.py` produce exactamente seis páginas con gráficos nativos vectoriales y una captura real de MLflow. Requiere un entorno editorial separado con `requirements-editorial.txt` y Arial o DejaVu; los PNG de revisión quedan privados en `tmp/`. Poppler renderiza para control visual. El costo-beneficio del LLM se declara como decisión posterior, con el gasto medido separado del costo operativo futuro.

Destino autorizado: `https://github.com/wilmerpuerta/data-science-end-to-end`, rama master, carpeta `psets/proyecto/oulad/`. Se preservan los materiales del curso y el historial; solo se actualiza el proyecto. Los commits de los entrenamientos se importan y mantienen alcanzables desde la publicación, no se reemplazan por SHAs posteriores ficticios.
