# PSet 2: pipeline de datos OULAD

Entrega de Wilmer Puerta. El pipeline prepara Fuente → Kestra → Snowflake Raw → dbt Bronze/Silver/Gold → Spark OBT → Snowflake. Esta carpeta contiene la implementación y evidencia del PSet 02 reorganizadas para la entrega. La reorganización no es una ejecución cloud nueva.

```text
pset_2/
├── docker-compose.yml
├── .env.example
├── README.md
├── kestra/                 # Flujos, ingesta, orquestación y auxiliares
├── dbt/                    # Modelos, tests y SQL de aprovisionamiento
├── spark/                  # Construcción y pruebas de la OBT
└── docs/                   # Memo, contrato, verificaciones y evidencias
```

El override cloud está en `kestra/docker-compose.cloud.yml`; los comandos están en `kestra/scripts/`. Se incluye `.gitignore` para excluir configuración privada, claves, entornos y artefactos locales. No se necesitan enlaces simbólicos ni la carpeta histórica `pset-02/` para ejecutar esta entrega.

## Recursos necesarios

- Docker Desktop con Compose; la ejecución histórica usó linux/amd64, 4 CPU y aproximadamente 7,8 GiB de memoria del motor. Se conservan versiones y digests fijados; compatibilidad ARM sin acreditar.
- Python 3 y, para el cliente Snowflake del host, Python 3.11 con las dependencias de `kestra/scripts/requirements-conexion.txt`.
- Los cinco CSV originales de OULAD y su manifiesto. No se distribuyen los CSV. [Metadatos e instrucciones](docs/referencias/datasets/README.md); [manifiesto](docs/referencias/datasets/manifest.json).
- Cuenta Snowflake, rol `PSET2_PIPELINE`, usuario `PSET2_SVC`, warehouse `PSET2_WH` y base `PSET2_OULAD`. [Aprovisionamiento](dbt/snowflake/01_aprovisionar.sql), [comprobaciones](dbt/snowflake/02_verificar_recursos.sql) y [guía](docs/configuracion-snowflake.md).

La auditoría agregada necesaria del PSet 1 se incluye en `docs/referencias/pset1-auditoria-resultados.json`. No se requieren el código ni los archivos privados del PSet 3.

## Preparar y levantar la infraestructura

Ejecutar desde esta carpeta. Los scripts también resuelven sus rutas al invocarlos desde otro directorio.

```sh
python3 kestra/scripts/infra.py prepare
```

El comando crea `.env.infra` con contraseñas aleatorias y permisos privados; si existe, lo conserva. `.env.example` es una plantilla pública con valores ficticios: no sirve como contraseña real. Por defecto los CSV se buscan en `../datasets`; para otra ubicación, establecer `OULAD_DATA_DIR` en `.env.infra`, con los CSV y `manifest.json` en esa misma carpeta. No cambiar contraseñas de un proyecto con volúmenes existentes sin un procedimiento de recuperación.

```sh
python3 kestra/scripts/diagnostico.py --data-dir ../datasets
python3 kestra/scripts/infra.py validate --local-only
python3 kestra/scripts/infra.py pull --local-only
python3 kestra/scripts/infra.py build --local-only
python3 kestra/scripts/infra.py up --local-only
python3 kestra/scripts/infra.py status --local-only
python3 kestra/scripts/comprobar_kestra.py --seed
python3 kestra/scripts/comprobar_kestra.py --execute --check-auth
python3 kestra/scripts/infra.py dbt-version --local-only
python3 kestra/scripts/infra.py spark-test --local-only
```

La entrega usa el proyecto Compose `pset2-entrega`: Kestra en `http://localhost:18090` y gestión en `18091`, independientes del stack histórico. El usuario local es `admin@psets.local`; la contraseña está solo en `.env.infra`. PostgreSQL y los ejecutores no publican puertos. Los nombres y puertos pueden cambiarse mediante `PSET2_COMPOSE_PROJECT_NAME`, `PSET2_KESTRA_PORT` y `PSET2_KESTRA_MANAGEMENT_PORT`.

Para detener conservando los volúmenes: `python3 kestra/scripts/infra.py stop --local-only`. El comando `down` elimina contenedores y red, conserva los volúmenes y no utiliza `-v`.

## Configurar Snowflake y los ejecutores

```sh
uv venv --python 3.11 .venv
uv pip sync --only-binary :all: --python .venv/bin/python kestra/scripts/requirements-conexion.txt
.venv/bin/python kestra/scripts/probar_conexion.py --check-installation
```

Las claves se preparan interactivamente con `kestra/scripts/preparar_claves.py`, fuera del repositorio, y se registra la pública según la guía de [autenticación](docs/autenticacion-local.md). Con autenticación ya configurada, `probar_conexion.py` comprueba el contexto y `configurar_cloud.py` prepara las referencias privadas; se ejecutan en una terminal local sin pegar secretos en el chat. Una configuración externa existente se conserva: para reutilizarla, copiar únicamente sus referencias `.env.cloud` a esta carpeta, revisar que apunten a los archivos correctos y mantener permisos 0600. No regenerar claves por el cambio de carpeta.

`.env.cloud` referencia dos archivos externos: configuración Snowflake y clave privada. Se montan en solo lectura; no se escriben contraseñas, tokens ni claves en YAML, documentación o Git.

```sh
python3 kestra/scripts/infra.py validate --cloud
python3 kestra/scripts/infra.py build --cloud
python3 kestra/scripts/infra.py up --cloud
python3 kestra/scripts/infra.py status --cloud
```

El modo cloud se activa automáticamente si existe `.env.cloud`; `--local-only` selecciona expresamente el modo sin montajes cloud. No alternar modos durante una carga. Si se levantó el stack local y después se activa cloud, no ejecutar tareas mientras Compose actualiza los ejecutores.

## Ejecutar el pipeline completo con Kestra

```sh
python3 kestra/scripts/ejecutar_pipeline.py --deploy
python3 kestra/scripts/ejecutar_pipeline.py
```

El flujo `pset2.oulad/oulad_pipeline` ejecuta Raw → gate → dbt → Spark → verificación. La ejecución espera su resultado y escribe informes agregados en `docs/evidencia/pipeline/`. Las salidas completas privadas se conservan en `.local/`. Los calendarios permanecen desactivados; no se activa una carga periódica al desplegar.

Para consultar una ejecución existente sin crear otra: `python3 kestra/scripts/ejecutar_pipeline.py --resume-execution ID`. La carga Raw es idempotente por fichero y checksum; la publicación es transaccional por etapa, no por toda la cadena. No ejecutar las etapas manuales en paralelo con el flujo integral.

## Ejecutar las etapas individualmente

Con las referencias privadas preparadas y el stack cloud saludable:

```sh
python3 kestra/scripts/ejecutar_raw.py --deploy
python3 kestra/scripts/ejecutar_raw.py --check-connection
python3 kestra/scripts/ejecutar_raw.py
python3 kestra/scripts/ejecutar_dbt.py parse
python3 kestra/scripts/ejecutar_dbt.py debug
python3 kestra/scripts/ejecutar_dbt.py build-gold
python3 kestra/scripts/ejecutar_dbt.py quality-export
python3 kestra/scripts/ejecutar_dbt.py quality-export-silver
python3 kestra/scripts/ejecutar_dbt.py quality-export-gold
python3 kestra/scripts/ejecutar_spark.py check-connection
python3 kestra/scripts/ejecutar_spark.py test-features
python3 kestra/scripts/ejecutar_spark.py build-obt
```

`build-gold` incluye Bronze y Silver. `build-bronze`, `build-silver` y `test-gold` permiten operar por capa. Spark publica `ANALYTICS.OBT_FEATURES` con 35 columnas y mantiene los outcomes separados. Estas órdenes pueden usar recursos y escribir en Snowflake; revisar rol, destino y configuración antes de una repetición deliberada. Para revisar el trabajo cerrado basta con sus informes.

## Documentación y reproducción

- [Memo técnico aprobado](docs/PSet2_memo_Puerta_Wilmer.pdf) y [fuente original](docs/memo-pset2.md), de seis páginas. Sus comandos y referencias históricas se traducen mediante [rutas de entrega](docs/rutas-entrega.md).
- [Enunciado](docs/enunciado.md), [rúbrica](docs/rubrica.md), [contrato de datos](docs/contrato-datos.md), [orquestación](docs/orquestacion-integral.md) y [OBT](docs/obt-spark.md).
- [Ejecución cloud histórica](docs/pipeline-verificacion.json), [reproducción limpia histórica](docs/reproduccion-limpia.json) y [validación de esta estructura](docs/validacion-entrega.md).

La evidencia histórica registra cinco fuentes con 10.726.852 filas Raw, 23 modelos y 168 tests dbt, y OBT de 108.277 filas y 35 columnas. Las pruebas nuevas de reorganización se identifican aparte: no certifican una recarga cloud desde esta ruta. El costo monetario histórico sigue sin cuantificar; la cuenta Snowflake y los datos originales son recursos externos.

```sh
python3 kestra/scripts/verificar_paquete.py
python3 kestra/scripts/paquete.py
```

El segundo comando genera `PSet2_entrega_Puerta_Wilmer.zip` en la carpeta contenedora, con raíz `pset_2/`, manifiesto SHA-256 y exclusión de recursos privados. El [procedimiento de reproducción limpia](docs/reproduccion-limpia.md) sigue disponible para una repetición completa deliberada con Snowflake. Esa repetición requiere los datos y la configuración externa y puede detener temporalmente el stack de esta entrega; conserva el stack histórico por usar otro proyecto Compose.

Para regenerar o revisar el memo, preparar un entorno editorial separado con `kestra/scripts/requirements-memo.txt` y ejecutar `kestra/scripts/generar_memo.py` o `kestra/scripts/verificar_memo.py --render` con ese Python. El generador escribe directamente en `docs/`. Las pruebas Raw se ejecutan con `PYTHONPATH=kestra/ingestion .venv/bin/python -m unittest discover -s kestra/ingestion -p 'test_*.py' -v`. Las entradas `spark-submit` se excluyen de la colección pytest y se prueban en su contenedor.
