# PSet 2: pipeline de datos OULAD

Wilmer Puerta · Continuidad del [PSet 1](../pset-01/README.md).

El pipeline reproduce Fuente → Kestra → Snowflake Raw → dbt Bronze/Staging → dbt Silver → dbt Gold estrella → Spark OBT → Snowflake. La cadena integral terminó SUCCESS y la reproducción desde exportación limpia está verificada. El [memo técnico de seis páginas](output/pdf/PSet2_memo_Puerta_Wilmer.pdf) explica la implementación y sus límites; su [fuente Markdown](memo-pset2.md) y sus comandos de exportación están disponibles. La [revisión del paquete](docs/revision-paquete.md) documenta las comprobaciones previas a publicar. El costo monetario sigue sin cuantificar. GitHub queda para el final.

## Estado real al 13-nov-2026

| Componente | Estado y evidencia |
|---|---|
| Fuente | Cinco CSV coincidentes con el manifiesto; montaje de solo lectura y SHA-256 comprobados desde Spark |
| Snowflake | Base, cinco esquemas, warehouse suspendido X-Small y rol comprobados mediante resultados del autor |
| Autenticación del host | PSET2_SVC por claves, rol y contexto correctos; [informe real](docs/conexion-snowflake.json) |
| Compose | [Configuración implementada](docker-compose.yml), PostgreSQL/Kestra/Spark saludables y persistencia comprobada |
| Kestra local | Flujo infra_smoke ejecutado en SUCCESS y conservado tras reinicio; API rechaza acceso sin autenticación |
| Spark local | Trabajo real Spark 3.5.6: suma de rango, 32.593 matrículas y cinco checksums |
| dbt Core en Docker | Core 1.10.13/adaptador 1.10.2 conectados; cinco vistas Bronze, perfil agregado y 45 tests aprobados |
| Raw desde Kestra | Cinco fuentes, 10.726.852 filas reconciliadas; cinco NOOP, retry controlado y backfill por fichero comprobados |
| Calendario Raw | Días 1 y 15 a las 09:00 America/Guayaquil; configurado y desactivado, sin disparo temporal probado |
| Silver dbt | Siete tablas; 8.459.320 claves diarias, 39.605.099 clics conservados y 101 tests Bronze/Silver aprobados |
| Gold dimensional | Cinco dimensiones, dos hechos y tres tablas complementarias/de calidad; 168 tests de las tres capas aprobados |
| Spark cloud y OBT | 108.277 filas matrícula–corte y 35 columnas en ANALYTICS.OBT_FEATURES; población, pruebas temporales y lectura de vuelta verificadas |
| Orquestación integral | Kestra oulad_pipeline SUCCESS; fallo permanente y retry controlados, orden verificado y trabajos internos sin duplicación |
| Reproducción limpia | SUCCESS en carpeta/proyecto/volúmenes nuevos; cinco CSV recargados, 168 tests y cuatro huellas OBT idénticas |
| Memo técnico | Seis páginas, dos diagramas vectoriales y [verificación de coherencia](docs/memo-verificacion.json) |
| Revisión del paquete | Comprobaciones locales, entregables, enlaces y exclusiones según [informe](docs/revision-paquete.md) |
| Pendiente | Medición de costo monetario y decisión de publicación GitHub |

La conexión del host y la del ejecutor Kestra están verificadas. Raw está cargado y Bronze construido con tests aprobados. dbt ya construyó Bronze, Silver y Gold; Spark cloud y OBT también se comprobaron; ver la sección Spark. Los permisos Raw, Bronze, Silver y Gold funcionaron; el timeout configurado en el warehouse aún necesita evidencia específica. [Estado detallado](docs/estado-ejecucion.md) e [informe de infraestructura](docs/infraestructura-verificacion.json).

## Recorrido desde una copia nueva

Requisitos: Git, Docker Desktop con Compose, Python 3 y uv para preparar el cliente de conexión Python 3.11; OpenSSL para generar claves si aún no existen. El pipeline local probado usa linux/amd64. Ejecutar desde la raíz y completar las etapas en orden:

1. Obtener los cinco CSV según [datasets/README.md](../datasets/README.md) y comprobar identidad con manifest.json. Los originales no se distribuyen en Git.
2. Aprovisionar los recursos de este proyecto con [01_aprovisionar.sql](snowflake/01_aprovisionar.sql) y comprobarlos con [02_verificar_recursos.sql](snowflake/02_verificar_recursos.sql). La [guía Snowflake](docs/configuracion-snowflake.md) explica roles, recursos preexistentes y límites.
3. Preparar claves externas y registrar el usuario de servicio según [autenticacion-local.md](docs/autenticacion-local.md). Si ya existen, conservarlas y comprobar su asignación; no regenerarlas para cada ejecución.
4. Preparar el cliente Python con los comandos siguientes, verificar autenticación y crear la configuración privada usando [configurar_cloud.py](scripts/configurar_cloud.py). Sus prompts se completan solamente en la terminal local.

```bash
uv --cache-dir tmp/uv-cache venv --python 3.11 pset-02/.venv
uv --cache-dir tmp/uv-cache pip sync --only-binary :all: --python pset-02/.venv/bin/python pset-02/scripts/requirements-conexion.txt
pset-02/.venv/bin/python pset-02/scripts/probar_conexion.py --check-installation
pset-02/.venv/bin/python pset-02/scripts/probar_conexion.py
pset-02/.venv/bin/python pset-02/scripts/configurar_cloud.py
```

5. Preparar la infraestructura local, descargar las imágenes base, construir los tres clientes y levantar los cinco servicios:

```bash
python3 pset-02/scripts/infra.py prepare
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/infra.py pull --cloud
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py up --cloud
python3 pset-02/scripts/infra.py status --cloud
```

6. Desplegar y ejecutar la cadena completa según la sección «Ejecutar toda la cadena desde Kestra». Sus tareas ejecutan Raw, dbt y Spark y validan el resultado. Las secciones por etapa permiten inspeccionar o repetir componentes individualmente; no es necesario ejecutar ambas rutas para una misma carga.
7. Verificar entregables y paquete según [revision-paquete.md](docs/revision-paquete.md). Para exportar el memo, seguir [memo-tecnico.md](docs/memo-tecnico.md). Detener con `python3 pset-02/scripts/infra.py stop --cloud` preserva los volúmenes.

La configuración privada, los recursos cloud y los datos identificados son dependencias explícitas. Preparar un entorno o exportar un documento no sustituye ejecutar y verificar la cadena.

## Levantar la infraestructura local

Abrir Docker Desktop. Desde la raíz del repositorio, con Python 3 y Docker Compose disponibles:

```bash
python3 pset-02/scripts/infra.py prepare
python3 pset-02/scripts/infra.py validate
python3 pset-02/scripts/infra.py pull
python3 pset-02/scripts/infra.py build
python3 pset-02/scripts/infra.py up
python3 pset-02/scripts/infra.py status
```

prepare genera contraseñas aleatorias locales en .env.infra, excluido de Git, con permisos privados; no contiene credenciales Snowflake y no sobrescribe archivos existentes. validate no muestra secretos. pull obtiene imágenes fijadas por digest; build construye dbt desde base fijada y [dependencias resueltas con hashes](dbt/requirements.txt). up espera salud de los servicios. status muestra únicamente servicio, estado y salud. Los auxiliares resuelven rutas desde su ubicación.

Kestra: http://localhost:8080, usuario admin@psets.local. Consultar la contraseña PSET2_KESTRA_PASSWORD solamente en el archivo local .env.infra; no enviarla al chat ni incluirla en documentación. Puertos 8080 y 8081 ligados a localhost. No se publican puertos de PostgreSQL ni Spark. [Guía completa](docs/infraestructura-local.md).

El autor confirmó acceso a la interfaz. Configuración cloud utilizada: [preparar configuración privada de ingesta](docs/configuracion-ingesta.md) con `pset-02/.venv/bin/python pset-02/scripts/configurar_cloud.py`. El asistente valida la conexión del host y guarda cuenta/frase fuera del repositorio con permisos 0600; .env.cloud solo contiene rutas locales y está excluido de Git. El autor ejecutó ese asistente y después se comprobó la conexión del ejecutor Kestra. El asistente no carga CSV; el flujo Raw posterior sí se ejecutó y reconcilió.

## Ejecutar las comprobaciones de Kestra, dbt y Spark

```bash
python3 pset-02/scripts/comprobar_kestra.py --seed
python3 pset-02/scripts/comprobar_kestra.py --execute --check-auth
python3 pset-02/scripts/infra.py dbt-version
python3 pset-02/scripts/infra.py spark-test
```

Estos comandos prueban la infraestructura: flujo local de log, instalación dbt y trabajo Spark sin escritura cloud. La carga real Raw usa los comandos de la sección siguiente. Spark corre local[2] dentro de un contenedor ejecutor, sin clúster master/worker. dbt es un servicio puntual del perfil tools y termina después del comando. El proyecto dbt y los comandos de conexión/build/tests Bronze ya existen y se explican en la sección siguiente. La OBT ya se construyó según obt-spark.md; orquestación completa ya verificada; reproducción desde exportación limpia ya verificada; ver la sección de reproducción. El aviso de versiones más recientes no actualiza las versiones fijadas.

Para detener y volver a iniciar, preservando datos y configuración:

```bash
python3 pset-02/scripts/infra.py stop
python3 pset-02/scripts/infra.py up
```

También existe down para quitar contenedores/red conservando volúmenes; no utiliza -v. Mantener .env.infra junto con los volúmenes: regenerar contraseñas no cambia automáticamente la contraseña persistida en PostgreSQL.

## Datos, recursos y reproducción

Originales y manifest.json en [../datasets](../datasets/README.md). Se montan como solo lectura desde pset-02; OULAD_DATA_DIR permite otra carpeta con archivos y manifiesto coherentes. No hay rutas personales fijas. La auditoría original puede repetirse con `python3 pset-02/scripts/diagnostico.py --output pset-02/docs/diagnostico-local.json`.

Entorno local probado: linux/amd64 en Docker Desktop, 4 CPU y unos 7,8 GiB asignados al motor. Ejecutar trabajos por etapas. Versiones y digests en [versiones-infraestructura.json](docs/versiones-infraestructura.json). La [guía de infraestructura](docs/infraestructura-local.md) detalla límites de memoria, dependencias y alcance probado. No se afirma compatibilidad ARM ni mínimos universales sin medirlos.

Desde un clon limpio: obtener datos identificados y verificar hashes; preparar secretos locales; descargar y construir imágenes; levantar y verificar servicios con los comandos anteriores. Para reproducir la parte cloud se requieren además cuenta, roles, recursos y claves según la guía Snowflake. Docker por sí solo no reproduce Snowflake. Ninguna contraseña, token o clave se incluye en archivos versionados. .env.example contiene únicamente ejemplos ficticios; .env, .env.infra, claves, caches y salidas locales están excluidos de Git. No guardar Compose expandido, entornos completos o logs con autenticación como evidencia.

## Ejecutar la ingesta Raw real

Con el asistente de configuración privada ya completado:

```bash
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/infra.py up --cloud
python3 pset-02/scripts/ejecutar_raw.py --deploy
python3 pset-02/scripts/ejecutar_raw.py --check-connection
python3 pset-02/scripts/ejecutar_raw.py
```

En Kestra: namespace **pset2.oulad**, flujo **oulad_raw**. La conexión y las cinco cargas ocurren dentro del ejecutor Process, sin pasos manuales entre fuentes. La configuración y la clave se montan individualmente como solo lectura, nunca como inputs o valores en YAML. Con .env.cloud y el override presentes, infra.py activa también el modo cloud por defecto; --local-only permite volver explícitamente al modo sin esos montajes. No cambiar de modo durante una carga.

Reejecutar la última orden debe devolver NOOP para las cinco fuentes reconciliadas, sin agregar filas a los datos Raw. Backfill comprobado: `python3 pset-02/scripts/ejecutar_raw.py --file courses.csv --force-reload`. La partición de esta versión es fichero/checksum completo, no módulo-edición; se conserva la versión actual por fuente. La publicación solo afecta tablas con contrato gestionado y utiliza una transacción tras validar la tabla temporal.

[Guía de ingesta](docs/ingesta-raw.md), [evidencia real](docs/ingesta-raw-verificacion.json) y [consultas de verificación](snowflake/04_verificar_raw.sql). Los informes sanitizados están en output/raw/. La ingesta usa el warehouse: no se ha cuantificado consumo monetario. El trigger horario permanece desactivado; repetir manualmente toda la carga no es necesario para inspeccionar los resultados.

## Ejecutar dbt Bronze/Staging y revisar calidad

Con Raw cargado y los archivos privados ya preparados:

```bash
python3 pset-02/scripts/ejecutar_dbt.py parse
python3 pset-02/scripts/ejecutar_dbt.py debug
python3 pset-02/scripts/ejecutar_dbt.py build-bronze
python3 pset-02/scripts/ejecutar_dbt.py quality-export
python3 pset-02/scripts/resumir_bronze.py
```

Estos comandos ya se ejecutaron: conexión correcta, cinco vistas tipadas y una tabla agregada en BRONZE, **45 tests aprobados** y métricas globales exportadas. Los cinco conteos coinciden con Raw; no se eliminaron filas ni se imputaron atributos. Los valores numéricos vacíos pasan a NULL; errores de conversión harían fallar los tests. Días negativos se conservan. El total de clics es 39.605.099.

La [guía detallada](docs/calidad-bronze.md) explica cada comando, claves, tipos, secretos y pruebas. Los [resultados y decisiones](docs/calidad-bronze-resultados.md) se generan desde [métricas reales](docs/calidad-bronze.json) y el [build dbt](docs/dbt-build-bronze.json). Se encontraron 2.195.960 filas adicionales respecto de claves matrícula–recurso–día distintas; se mantienen hasta justificar su consolidación. También se documentan fechas faltantes y discrepancias retrospectivas entre retiro y resultado.

Para repetir solo pruebas existe `python3 pset-02/scripts/ejecutar_dbt.py test-bronze`; después de cambiar Raw, repetir build-bronze y exportar las métricas para renovar la instantánea. No ejecutar ingesta y dbt simultáneamente. Los artefactos completos y logs permanecen en .local/dbt, excluido de Git; docs solo recibe campos permitidos y agregados. dbt debug usa --connection; no requiere Git ni dbt deps en este proyecto. Silver y Gold ya están implementados según las secciones siguientes.

## Ejecutar Silver: consolidación y reglas de calidad

Con Raw disponible y la configuración privada existente:

```bash
python3 pset-02/scripts/ejecutar_dbt.py parse
python3 pset-02/scripts/ejecutar_dbt.py build-silver
python3 pset-02/scripts/ejecutar_dbt.py quality-export-silver
python3 pset-02/scripts/resumir_silver.py
```

El build vuelve a validar Bronze y construye siete tablas en SILVER: ediciones, recursos, antecedentes de matrícula, registro, resultados retrospectivos, actividad diaria y perfil agregado de calidad. **101 tests aprobados: 45 de Bronze y 56 de Silver**. La actividad se consolida mediante suma por matrícula–recurso–día: 10.655.280 filas fuente quedan representadas en 8.459.320 claves diarias, con los mismos 39.605.099 clics. No se borran contribuciones por parecer idénticas; el impacto de esa alternativa se cuantifica aparte.

Las 32.593 matrículas se conservan, incluidas 3.365 sin actividad. Registro clasifica 32.314 matrículas con fecha conocida <= 0, 234 posteriores al inicio y 45 sin fecha. Esta clasificación no es todavía elegibilidad por corte. Los resultados y banderas retrospectivas van en SLV_OUTCOMES; una lista permitida de columnas protege SLV_ENROLLMENTS de su inclusión accidental.

La [guía Silver](docs/silver.md) explica comandos, grano, linaje, decisiones y limitaciones. Los [resultados](docs/silver-resultados.md) se generan desde el [build](docs/dbt-build-silver.json) y las [métricas](docs/calidad-silver.json). Dos builds aprobaron las pruebas y mantuvieron las mismas 27 métricas agregadas: [evidencia de repetición](docs/repeticion-silver.json). El procedimiento checkpoint/build/export/verify de la guía permite reproducir esa comprobación.

`python3 pset-02/scripts/ejecutar_dbt.py test-silver` permite ejecutar solo las pruebas Silver. Si cambia Raw, repetir build-silver y exportación; no cargar Raw en paralelo. Gold ya está implementado según la sección siguiente; Spark cloud y OBT ya están verificados según la sección siguiente. No se ha cuantificado costo monetario de las ejecuciones Snowflake.

## Ejecutar Gold: dimensiones y hechos

```bash
python3 pset-02/scripts/ejecutar_dbt.py parse
python3 pset-02/scripts/ejecutar_dbt.py build-gold
python3 pset-02/scripts/ejecutar_dbt.py quality-export-gold
python3 pset-02/scripts/resumir_gold.py
```

El build construye/revalida Bronze, Silver y Gold: **168 tests aprobados**, incluidos 67 de Gold. GOLD contiene cinco dimensiones (persona, edición, recurso, contexto de matrícula y día relativo), dos hechos (matrícula y actividad diaria), retiro registrado, resultados retrospectivos y perfil de calidad. La [guía Gold](docs/gold.md) explica los granos, el diagrama, medidas aditivas y cómo combinar hechos sin multiplicar matrículas o créditos.

Se conservan 32.593 matrículas, incluidas 3.365 sin actividad, y 39.605.099 clics en 8.459.320 filas diarias. Unir las cinco dimensiones mantiene filas y clics por edición. Los antecedentes variables quedan en DIM_ENROLLMENT; DIM_STUDENT contiene solo las 28.785 identidades. La dimensión de día cubre -25 a 269 e incluye los cuatro cortes. Retiro y resultados permanecen separados de antecedentes.

Los [resultados Gold](docs/gold-resultados.md) se generan desde el [build](docs/dbt-build-gold.json) y las [métricas](docs/calidad-gold.json). La referencia poblacional por corte coincide con PSet 1: 27.881, 27.307, 26.795 y 26.294 elegibles en días 14, 28, 42 y 56. Esa referencia se utilizó para comprobar la OBT ya construida con Spark.

La [repetición Gold](docs/repeticion-gold.json) comprobó dos builds distintos con 168 pruebas aprobadas cada uno y las mismas 26 métricas agregadas.

`python3 pset-02/scripts/ejecutar_dbt.py test-gold` permite ejecutar solo pruebas Gold. La guía incluye checkpoint/build/export/verify para medir repetición sin acumulación; no cambiar Raw durante esa comprobación. Los logs y artefactos completos continúan en .local/dbt; los informes versionables son agregados y no contienen credenciales. Spark cloud y OBT están verificados según la sección siguiente; orquestación completa ya verificada; ver orquestacion-integral.md.

## Ejecutar Spark y publicar la OBT

Con Gold disponible y la configuración privada existente:

```bash
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/ejecutar_spark.py check-connection
python3 pset-02/scripts/ejecutar_spark.py test-features
python3 pset-02/scripts/ejecutar_spark.py build-obt
python3 pset-02/scripts/resumir_obt.py
```

Estos comandos ya se ejecutaron. Spark 3.5.6/Scala 2.12.18/Java 17 se conecta con el conector 3.2.3-spark_3.5 y JDBC 4.4.1, fijados por hash. Los secretos se montan como solo lectura y la clave se descifra únicamente en memoria. Las agregaciones se ejecutan en Spark con autopushdown desactivado por DataFrame; Snowflake aporta Gold y recibe la salida validada. [Dependencias](docs/spark-dependencias.json) y [guía completa](docs/obt-spark.md).

La tabla **PSET2_OULAD.ANALYTICS.OBT_FEATURES** contiene **108.277 filas y 35 columnas**, con clave única matrícula–corte. Se construye la población antes de agregar actividad y se preservan matrículas sin registros. Filas por corte: 14=27.881, 28=27.307, 42=26.795, 56=26.294; todas coinciden con Gold y PSet 1. Los siete casos sintéticos y cuatro pruebas reales de perturbación futura pasaron. La lectura completa de vuelta desde Snowflake coincide con el DataFrame antes de publicar.

El [contrato de features](spark/feature-contract.json) separa identificadores, variables estáticas, actividad y auditoría; resultados finales y fecha de retiro están excluidos. Los contadores cero representan ausencia de registros, no cobertura completa; recencia queda NULL sin actividad. No se ajustaron imputaciones, codificadores ni modelos. Los [resultados](docs/obt-resultados.md) se generan desde el [informe real](docs/obt-verificacion.json) y se contrastan con la auditoría previa.

La publicación escribe una tabla provisional de construcción, valida y hace rename/swap del destino gestionado; no usa append. .local/spark conserva temporales y logs fuera de Git. No reconstruir Gold durante el trabajo. Las [consultas de revisión](snowflake/08_verificar_obt.sql) muestran agregados y diferencias de claves. Las etiquetas permanecen en GOLD.OUTCOME_ENROLLMENT para evaluación posterior separada.

Dos construcciones completas mantuvieron las mismas cuatro huellas SHA-256, filas, claves, columnas y métricas: [repetición OBT](docs/repeticion-obt.json). La guía incluye el procedimiento checkpoint/build-obt/verify para comprobarlo después de un build exitoso.

## Ejecutar toda la cadena desde Kestra

```bash
python3 pset-02/scripts/infra.py up --cloud
python3 pset-02/scripts/ejecutar_pipeline.py --deploy
python3 pset-02/scripts/ejecutar_pipeline.py
```

El flujo **pset2.oulad/oulad_pipeline** llama a Raw como subflujo, espera su resultado, ejecuta dbt mediante dbt-runner, Spark mediante spark-runner y cierra con reconciliación. Los cinco servicios quedan saludables. Los dos ejecutores son internos: sin puertos publicados, sin socket Docker, sin comandos libres y con las mismas imágenes probadas. Las peticiones solo contienen el ID de ejecución; credenciales y logs completos permanecen privados.

La ejecución **6X7mzEdM0yvoBSbp8MnALv** terminó SUCCESS: cinco fuentes Raw reconciliadas (NOOP), 23 modelos/168 tests dbt y OBT de 108.277 filas/35 columnas. El retry controlado falló una vez antes de dbt/Spark y se recuperó. Otra ejecución con fallo permanente se detuvo tras Raw y gate sin iniciar transformaciones. Repetir las solicitudes internas reutilizó el mismo job_id/intento de dbt y Spark.

[Guía integral](docs/orquestacion-integral.md), [resultados](docs/pipeline-resultados.md), [pruebas JSON](docs/pipeline-pruebas.json) y [cierre de la ejecución](docs/pipeline-verificacion.json). La OBT orquestada mantiene las mismas cuatro huellas de contenido que la ejecución standalone previa. Los calendarios padre y Raw permanecen desactivados.

Pruebas reproducibles: `ejecutar_pipeline.py --fail-after-raw` debe terminar con error deliberado; `ejecutar_pipeline.py --retry-probe` debe recuperarse y completar la cadena. Backfill disponible con `--file courses.csv --force-reload`, por fichero completo, seguido de reconstrucción completa. `--resume-execution ID` consulta una ejecución existente sin relanzarla. No ejecutar comandos manuales en paralelo con el padre. La atomicidad es por etapa, no una transacción de todo el pipeline.

Para actualizar los informes canónicos de un flujo nuevo y regenerar los resúmenes, seguir la sección de evidencia de la guía. Un SUCCESS exige verification.json válido; la mera presencia de tablas no demuestra ejecución completa. La exportación limpia ya se reprodujo y el memo está generado; el costo monetario sigue sin cuantificar. GitHub queda para el final.

## Reproducir desde una exportación limpia

```bash
python3 pset-02/scripts/reproduccion_limpia.py prepare
python3 pset-02/scripts/reproduccion_limpia.py run --run-id ID_PREPARADO
python3 pset-02/scripts/reproduccion_limpia.py collect --run-id ID_PREPARADO
python3 pset-02/scripts/resumir_reproduccion.py
```

Usar el ID que devuelve prepare. El procedimiento ya se ejecutó con **849681d33298**: 214 archivos versionables en otra carpeta, contraseñas locales nuevas, proyecto Compose aislado, puertos 18080/18081 y volúmenes PostgreSQL/Kestra nuevos. Las tres imágenes propias se reconstruyeron con --no-cache. Los cinco CSV quedaron **LOADED**, con 10.726.852 filas Raw; dbt aprobó 168 pruebas y Spark publicó 108.277 filas/35 columnas con las mismas cuatro huellas de contenido.

La prueba detiene temporalmente el stack principal y lo restaura al terminar; conserva detenida la copia para inspección. Referencia los CSV y secretos externos, sin copiarlos al árbol exportado, y reutiliza los recursos Snowflake existentes. Es una exportación limpia, no un clon remoto ni una cuenta Snowflake nueva. [Procedimiento y alcance](docs/reproduccion-limpia.md), [resultados](docs/reproduccion-resultados.md), [informe](docs/reproduccion-limpia.json).

El proyecto y los puertos se parametrizan en .env.infra mediante PSET2_COMPOSE_PROJECT_NAME, PSET2_KESTRA_PORT y PSET2_KESTRA_MANAGEMENT_PORT; los defaults principales siguen siendo pset2 y 8080/8081. `infra.py build --cloud --no-cache` permite reconstruir las capas propias sin cache. Los datos, claves, entornos, logs y archivos de prueba permanecen excluidos de Git. No ejecutar operaciones manuales durante esta reproducción.

## Continuación del pipeline

La carga Raw ya utiliza checksum/run_id/partición por fichero, publicación transaccional e idempotencia. Se probaron retry con un fallo controlado y backfill de courses.csv. El calendario está definido para días 1 y 15, pero desactivado hasta cerrar la operación del pipeline; no equivale a un disparo periódico probado. OULAD es un histórico estático: frecuencia de ejecución no implica nuevos datos. Bronze usa source(), ref() y tests de negocio. Silver, Gold y Spark/OBT están construidos; la orquestación integral y la reproducción desde exportación limpia están verificadas. El memo está generado y la revisión local está documentada; la publicación requiere decidir el destino GitHub. La OBT tiene grano matrícula–corte, elegibilidad antes de actividad y separación de target y predictores, conforme al contrato.

Los comandos Raw ya se ejecutaron y verificaron. La cadena completa se ejecutó desde Kestra y desde una exportación limpia con volúmenes nuevos y dependencias cloud documentadas. Batch basta para revisión quincenal. Streaming requeriría fuente continua y necesidad validada de baja latencia; no se implementará. El costo monetario no está cuantificado; mantener auto-suspend y documentar suspensión/limpieza.

## Memo técnico: generar y comprobar

El [PDF de seis páginas](output/pdf/PSet2_memo_Puerta_Wilmer.pdf) se exporta desde [memo-pset2.md](memo-pset2.md), con diagramas vectoriales y cifras reconciliadas con los informes JSON. La [guía de exportación](docs/memo-tecnico.md) explica dependencias, fuentes y revisión visual. Desde un entorno Python con [requirements-memo.txt](scripts/requirements-memo.txt) instalado:

```bash
python pset-02/scripts/generar_memo.py
python pset-02/scripts/verificar_memo.py --render
```

El verificador contrasta texto por página, cifras, diagramas, enlaces y Markdown de resultados contra sus generadores. El [informe](docs/memo-verificacion.json) registra las huellas de la fuente, el PDF y las evidencias utilizadas. Exportar no conecta con Snowflake ni vuelve a ejecutar el pipeline. El memo y estos scripts son posteriores a la instantánea de la reproducción limpia; los límites y pendientes permanecen explícitos.

## Documentación

- [Enunciado del profesor](enunciado.md) y [rúbrica](rubrica.md).
- [Memo PDF](output/pdf/PSet2_memo_Puerta_Wilmer.pdf), [fuente Markdown](memo-pset2.md) y [exportación/verificación](docs/memo-tecnico.md).
- [Revisión completa antes de publicar](docs/revision-paquete.md) e [informe verificable](docs/paquete-verificacion.json).
- [Paso a paso](docs/paso-a-paso.md) y [plan de implementación](docs/plan-implementacion.md).
- [Arquitectura](docs/arquitectura.md) y [contrato de datos](docs/contrato-datos.md).
- [Preparación de Snowflake](docs/configuracion-snowflake.md), [autenticación local](docs/autenticacion-local.md) y [.env.example](.env.example).
- [Ingesta Raw](docs/ingesta-raw.md) y [verificación de ingesta](docs/ingesta-raw-verificacion.json).
- [Bronze y calidad paso a paso](docs/calidad-bronze.md), [resultados](docs/calidad-bronze-resultados.md) y [tests dbt](docs/dbt-build-bronze.json).
- [Silver: reglas y ejecución](docs/silver.md), [resultados](docs/silver-resultados.md) y [repetición](docs/repeticion-silver.json).
- [Gold: guía y diagrama dimensional](docs/gold.md), [resultados](docs/gold-resultados.md) y [consultas de revisión](snowflake/07_verificar_gold.sql).
- [Spark y OBT paso a paso](docs/obt-spark.md), [resultados](docs/obt-resultados.md), [contrato de features](spark/feature-contract.json) e [informe](docs/obt-verificacion.json).
- [Orquestación integral con Kestra](docs/orquestacion-integral.md), [resultados](docs/pipeline-resultados.md) y [pruebas](docs/pipeline-pruebas.json).
- [Reproducción limpia](docs/reproduccion-limpia.md), [resultados](docs/reproduccion-resultados.md) e [informe](docs/reproduccion-limpia.json).
- [Infraestructura local](docs/infraestructura-local.md), [estado de ejecución](docs/estado-ejecucion.md) y [verificación](docs/infraestructura-verificacion.json).
