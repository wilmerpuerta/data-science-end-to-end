# Paso 6A: calidad y Bronze/Staging con dbt

Este paso convierte las cinco tablas Raw en cinco vistas tipadas dentro de BRONZE. No construye todavía Silver, Gold ni la OBT. Su propósito es hacer explícitos los tipos, medir anomalías y probar las relaciones antes de decidir cómo consolidar los datos. Raw conserva el texto original y su linaje.

## 1. Conectar dbt sin copiar credenciales

Desde la raíz, después de preparar Raw y la configuración privada:

```bash
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/ejecutar_dbt.py parse
python3 pset-02/scripts/ejecutar_dbt.py debug
```

`parse` comprueba Jinja, YAML y dependencias, sin consultar datos. `debug` ejecuta `dbt debug --connection`: comprueba la conexión independientemente de Git, que no está instalado en esta imagen. El proyecto no tiene paquetes externos ni requiere `dbt deps`. Las dependencias Python están fijadas en requirements.txt y ya instaladas en la imagen. Si la imagen no existe, ejecutar antes `infra.py build --cloud`.

El perfil profiles.yml contiene referencias Jinja, no valores de autenticación. bootstrap.py lee dentro del contenedor los dos archivos privados montados en solo lectura. Proporciona cuenta y frase a dbt mediante variables DBT_ENV_SECRET; dbt las oculta en sus logs. No se pasan valores privados como argumentos CLI. Tampoco se usa el rol administrador para transformar datos.

La imagen define un usuario sin privilegios para uso general. El override cloud ejecuta este cliente puntual como root para poder leer archivos del host con permisos 0600. No tiene socket Docker ni puertos publicados. Proyecto y secretos se montan como solo lectura; solo .local/dbt permite escribir artefactos. Es una solución local, no aislamiento multitenant. No modificar permisos de las claves para resolver el acceso.

El macro generate_schema_name dirige modelos a los esquemas precreados BRONZE/SILVER/GOLD/ANALYTICS; evita nombres como BRONZE_BRONZE y no crea esquemas. Los tests usan BRONZE y no guardan filas fallidas. Este entorno comparte nombres entre ejecuciones: ejecutar un único escritor por vez. Una variante de desarrollo simultáneo requerirá esquemas y grants separados. No ejecutar backfill Raw durante build o exportación de calidad.

## 2. Construir las vistas y probarlas

```bash
python3 pset-02/scripts/ejecutar_dbt.py build-bronze
```

El comando equivale a `dbt build --select tag:bronze`. Crea las cinco vistas, ejecuta tests y materializa DQ_BRONZE_PROFILE como una pequeña tabla agregada. La tabla de calidad es una instantánea de esa ejecución; las vistas consultan el estado actual de Raw. Después de cambiar Raw, repetir build antes de exportar métricas. Dos hilos limitan el paralelismo; las consultas se ejecutan en el warehouse PSET2_WH.

| Modelo | Fuente mediante source() | Grano conservado |
|---|---|---|
| STG_STUDENT_INFO | RAW.STUDENTINFO | Matrícula: módulo–edición–estudiante |
| STG_STUDENT_REGISTRATION | RAW.STUDENTREGISTRATION | Matrícula |
| STG_COURSES | RAW.COURSES | Módulo–edición |
| STG_VLE | RAW.VLE | Módulo–edición–recurso |
| STG_STUDENT_VLE | RAW.STUDENTVLE | Fila fuente de actividad, identificada por SHA-256 y número de fila |

Las dependencias entre modelos y tests usan ref(). Las claves concatenadas incluyen módulo y edición; `id_student` por sí solo identifica una persona, no una matrícula. Los componentes se validan como no nulos. La unicidad de matrícula–recurso–día no se impone a los eventos: primero se mide su multiplicidad global.

Cada columna numérica admite únicamente una representación entera, con signo opcional. No se redondean decimales para convertirlos. Texto vacío o formado solo por espacios pasa a NULL en Staging. Un valor no vacío que no cabe o no es un entero activa HAS_TYPE_ERROR y hace fallar el test; Raw permite investigar el original. Los metadatos SOURCE_SHA256, SOURCE_ROW_NUMBER, LOAD_RUN_ID y LOADED_AT permanecen disponibles.

No hay imputación, eliminación de filas ni deduplicación. Tampoco se entrenan transformaciones. Se conserva FINAL_RESULT como dato retrospectivo de origen; su presencia en Staging no autoriza usarlo como predictor. Silver/Gold ya separan las etiquetas conforme al contrato.

Los tests verifican claves requeridas y únicas según su grano, linaje técnico único, igualdad de filas Raw–Bronze, ausencia de errores de conversión, cuatro resultados finales válidos, relaciones completas entre tablas y dominios de clics, antecedentes, duración y semanas. Los días relativos pueden ser negativos. Una fecha de retiro vacía no se trata como error general: significa que la fuente no registra retiro.

## 3. Guardar evidencia y revisar decisiones

```bash
python3 pset-02/scripts/ejecutar_dbt.py quality-export
```

Se exportan solamente métricas agregadas de DQ_BRONZE_PROFILE a [calidad-bronze.json](calidad-bronze.json). El [resultado del build](dbt-build-bronze.json) contiene estados por nodo y cantidad de fallos. [Conexión](dbt-debug.json) y [parseo](dbt-parse.json) tienen informes separados. Los tiempos son UTC; pueden corresponder al día siguiente respecto de America/Guayaquil.

```bash
python3 pset-02/scripts/resumir_bronze.py
```

Este último comando genera la [tabla problema–evidencia–acción–justificación](calidad-bronze-resultados.md) directamente desde los dos JSON públicos. Se comprobó que el Markdown coincide exactamente con su generador y las métricas. No modificar sus cifras a mano.

Los artefactos completos de dbt, incluidos manifest.json, SQL compilado, run_results.json y logs, quedan en .local/dbt y fuera de Git. El auxiliar imprime solo una lista permitida de campos. Un fallo no se presenta como éxito ni conserva el estado público de una ejecución anterior. No copiar logs completos al repositorio. Las [consultas SQL](../snowflake/05_verificar_bronze.sql) permiten inspeccionar agregados desde Snowflake.

Para repetir únicamente los tests sin reconstruir la instantánea:

```bash
python3 pset-02/scripts/ejecutar_dbt.py test-bronze
```

También se ejecutó por separado: [45 tests aprobados](dbt-test-bronze.json), sin reconstruir modelos.

Si cambió Raw, usar build-bronze para renovar también el perfil de calidad. La repetición crea/reemplaza las vistas y la tabla agregada; no inserta filas en Raw. La ejecución usa cómputo Snowflake; no se ha cuantificado costo monetario.

## Interpretación de calidad

Completitud se mide como ausencias sobre filas de la fuente correspondiente. Validez se comprueba con tipos, dominios y rangos contextualizados. Consistencia se evalúa mediante claves, relaciones y coherencia temporal. Copiar correctamente un CSV prueba fidelidad de ingesta, pero no exactitud respecto de la realidad académica; no tenemos un registro institucional externo para cotejarla.

`repeated_natural_key_excess` es N menos la cantidad de claves matrícula–recurso–día distintas. `repeated_exact_value_excess` añade sum_click a esa clave antes de contar distintos. Son filas adicionales respecto de una representación única; no son número de grupos repetidos ni prueba de que los clics sean erróneos. Las decisiones Silver deben explicitar si suman o excluyen multiplicidad y reconciliar clics.

El cierre de este paso exige build exitoso, métricas exportadas y decisiones documentadas con evidencia. Silver se implementó posteriormente según [silver.md](silver.md). Gold también se implementó según [gold.md](gold.md). Spark cloud y OBT ya se comprobaron según [obt-spark.md](obt-spark.md); orquestación completa ya verificada; ver orquestacion-integral.md.

## Referencias de configuración

- [dbt: variables secretas](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var).
- [dbt: nombres de esquema y advertencia sobre entornos compartidos](https://docs.getdbt.com/docs/build/custom-schemas).
- [dbt Core: conexión Snowflake](https://docs.getdbt.com/docs/core/connect-data-platform/snowflake-setup).

La configuración se contrastó también con SnowflakeCredentials y las opciones CLI de la imagen instalada: Core 1.10.13 y adaptador 1.10.2. La documentación actual no sustituye la prueba de esa versión.
