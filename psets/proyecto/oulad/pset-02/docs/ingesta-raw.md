# Ingesta Raw con Kestra

Estado: ejecutada y reconciliada. Se cargaron los cinco CSV originales a PSET2_OULAD.RAW desde el ejecutor de Kestra. Conexión desde contenedor, carga completa, idempotencia, retry controlado y backfill por fichero comprobados. El horario periódico está configurado pero desactivado; Bronze dbt se construyó después según [calidad-bronze.md](calidad-bronze.md); Silver también se construyó según [silver.md](silver.md); Gold también se construyó según [gold.md](gold.md); Spark/OBT ya se ejecutó: [guía](obt-spark.md) y [resultados](obt-resultados.md).

## Reproducir preparación y carga

Prerequisitos: los pasos Snowflake, claves y configuración privada ya descritos en configuracion-snowflake.md, autenticacion-local.md y configuracion-ingesta.md. Los CSV y su manifiesto deben coincidir. Desde raíz:

```bash
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/infra.py up --cloud
python3 pset-02/scripts/ejecutar_raw.py --deploy
python3 pset-02/scripts/ejecutar_raw.py --check-connection
python3 pset-02/scripts/ejecutar_raw.py
```

infra.py agrega docker-compose.cloud.yml, las rutas locales de .env.cloud y las credenciales locales de .env.infra sin imprimirlas. También activa el modo cloud automáticamente si ambos archivos de configuración están presentes; --local-only selecciona explícitamente el modo sin secretos y puede retirar los montajes de Kestra al recrearlo. Usar --cloud en la secuencia de ingesta para dejar clara la intención. build evita el problema de normalización Unicode Compose/Bake ya documentado usando contextos relativos con Docker directamente.

La imagen de Kestra para ingesta se construye sobre la base fijada por digest y un conector Python 4.7.4 resuelto para Python 3.10/Linux. Se instala en /opt/oulad-deps sin cambiar el Python del host ni incluir secretos en capas Docker. El runner Process ejecuta load_raw.py con ese PYTHONPATH, sin socket Docker. CSV y código se montan en solo lectura. JSON privado y clave privada se montan individualmente como solo lectura en /run/secrets; la cuenta y la frase no se envían como inputs del flujo ni se registran en logs.

Desde Kestra también se puede abrir namespace pset2.oulad, flujo oulad_raw y ejecutar con sus inputs. La carga de los cinco archivos se realiza dentro de una ejecución sin pasos manuales entre fuentes. Mantener un solo escritor: el flujo tiene concurrency.limit=1 y behavior=QUEUE. No ejecutar load_raw.py en paralelo fuera de Kestra.

## Granos y conservación

| Fuente | Tabla Raw | Filas comprobadas |
|---|---|---:|
| studentInfo.csv | STUDENTINFO | 32.593 |
| studentRegistration.csv | STUDENTREGISTRATION | 32.593 |
| courses.csv | COURSES | 22 |
| vle.csv | VLE | 6.364 |
| studentVle.csv | STUDENTVLE | 10.655.280 |
| Total | Cinco fuentes | 10.726.852 |

Una fila Raw corresponde a una fila de datos del archivo original, no necesariamente una clave natural única. Las columnas originales se conservan como VARCHAR, con nombres equivalentes en mayúscula; se añaden SOURCE_SHA256, SOURCE_ROW_NUMBER, LOAD_RUN_ID y LOADED_AT. Archivo de origen identificado por tabla, comentario de contrato y registro INGESTION_LOG. La clave técnica de linaje es archivo/checksum/número de fila. Los números de fila vienen de METADATA$FILE_ROW_NUMBER; no se presupone que comiencen en 1 tras saltar la cabecera.

No se deduplican registros de actividad ni se imputan vacíos en Raw. El formato CSV evita convertir campos vacíos o el literal NULL en valores nulos; la limpieza se decidirá con dbt. Antes de subir se verifican checksum, bytes, cabecera, ancho de cada fila y conteo del CSV. ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE permite el COPY con columnas técnicas añadidas; el ancho se valida explícitamente en el lector local, no se ignoran filas irregulares.

Comprobaciones de valores ejecutadas contra Raw: Fail=7.052, Withdrawn=10.156 y aprobación=15.385; 1.111 imd_band vacíos, 45 fechas de registro vacías, 22.521 fechas de retiro vacías y 5.243 week_from/week_to vacíos. Estos vacíos no se convirtieron silenciosamente en NULL. La validación no demuestra exactitud respecto a la realidad externa ni cobertura completa de actividad.

## Publicación, idempotencia y recuperación

Cada fichero se comprime de forma determinista en un temporal del contenedor y se sube mediante PUT a un stage interno, bajo tabla/checksum. COPY carga una tabla temporal con datos y metadatos. Se exige conteo esperado, número de filas de origen distintas igual al conteo y un único checksum correcto antes de publicar.

La publicación realiza DELETE/INSERT y registro LOADED dentro de una transacción sobre la tabla gestionada de esa fuente. No usa TRUNCATE ni reemplaza objetos ajenos. El contrato y las columnas deben coincidir; una tabla sin el comentario de contrato esperado se rechaza. El target mantiene una versión actual por fichero; stage y log conservan linaje de cargas. Si falla antes de publicar, el target anterior permanece; si falla dentro de la transacción, rollback. Los temporales no son tablas finales.

Si el target ya contiene las filas esperadas, números de origen únicos y checksum correcto, se registra NOOP y se evita PUT/COPY/publicación. Esta condición se comprobó reejecutando las cinco entradas: todas devolvieron NOOP y mantuvieron sus conteos. Revisar checksum actualizado antes de aceptar otra versión: no se mezclan versiones silenciosamente. El log y los informes sí añaden evidencia de cada intento, aunque los datos Raw no cambien.

Kestra reintenta el proceso con espera exponencial de 5 s, máximo 30 s, hasta tres intentos. Se verificó con un fallo controlado antes de conectar: primer intento fallido y segundo correcto, ejecución SUCCESS. No se simuló una caída real del proveedor. En esta versión, errores permanentes también pueden agotar los intentos; las validaciones impiden publicar datos inválidos. Los informes distinguen ese fallo inyectado de un fallo de producción.

Backfill implementado por partición fichero/checksum completo, en lugar de módulo–edición del diseño preliminar. Permite repetir una fuente histórica sin rehacer las otras y publicar atómicamente esa fuente. No permite todavía recarga parcial por módulo/edición; esas granularidades se conservarán en las capas de datos. Se probó una recarga forzada de courses.csv, que mantuvo 22 filas:

```bash
python3 pset-02/scripts/ejecutar_raw.py --file courses.csv --force-reload
```

Sin --force-reload una partición ya reconciliada resulta NOOP. Tras una ejecución interrumpida, revisar primero el estado de Kestra. Si el controlador agota la espera, consultar la misma ejecución con --resume-execution ID para no lanzar otra innecesariamente. Una ejecución fallida puede repetirse por fichero: las fuentes ya publicadas se reconocerán y las demás se recuperarán sin duplicados adicionales.

## Frecuencia y consumo

El trigger validado por Kestra está definido para los días 1 y 15 a las 09:00 America/Guayaquil, con disabled=true. Es dos veces al mes, no un intervalo exacto de 14 días. OULAD es un histórico estático: la frecuencia revisa versiones y no implica nuevos datos del proveedor. El disparo temporal no se ha probado ni activado; no se presenta como una automatización calendarizada ya operativa. Se habilitará de forma explícita cuando se cierre el pipeline y su operación.

Las pruebas de COPY y reconciliación utilizaron el warehouse del proyecto. No se atribuye gratuidad ni costo cuantificado sin datos de consumo. Conservar auto-suspend; las reejecuciones NOOP evitan cargas pero todavía ejecutan consultas de comprobación.

## Evidencia y comprobaciones

Los informes de intentos y ejecuciones están en output/raw/, sin credenciales ni datos de filas. Los marcadores internos de la prueba de retry se excluyen de Git. [Resumen derivado de evidencia real](ingesta-raw-verificacion.json).

```bash
python3 -m unittest discover -s pset-02/ingestion -p 'test_*.py' -v
python3 pset-02/scripts/resumir_raw.py
```

Pruebas aisladas: preservación de duplicados/vacíos en la entrada, rechazo de hash cambiado, NOOP sin publicación, conteo temporal incorrecto sin eliminación del target y rollback ante error de publicación. Estas pruebas no sustituyen las ejecuciones cloud reales, conservadas por separado. Para consultar manualmente las tablas, [04_verificar_raw.sql](../snowflake/04_verificar_raw.sql) contiene solo consultas y selección de contexto; utiliza el warehouse.

Retry controlado, únicamente en modo de conexión:

```bash
python3 pset-02/scripts/ejecutar_raw.py --check-connection --retry-probe
```

La evaluación global de calidad y Bronze/Staging ya se ejecutaron: [guía](calidad-bronze.md) y [resultados](calidad-bronze-resultados.md). Silver ya se construyó: [guía](silver.md) y [resultados](silver-resultados.md). Gold ya se construyó: [guía y diagrama](gold.md). Spark y OBT ya se ejecutaron: [guía](obt-spark.md) y [resultados](obt-resultados.md). El siguiente paso es orquestación completa.

Fuentes técnicas: [PUT](https://docs.snowflake.com/en/sql-reference/sql/put), [COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table), [runner Process de Kestra](https://kestra.io/plugins/core/runner/io.kestra.plugin.core.runner.process) y [concurrencia](https://kestra.io/docs/workflow-components/concurrency). Las propiedades del flujo fueron aceptadas y probadas en la versión Kestra instalada.
