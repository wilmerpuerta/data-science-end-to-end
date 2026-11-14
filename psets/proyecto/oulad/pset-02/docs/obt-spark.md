# Paso 8: OBT con Spark y persistencia en Snowflake

La OBT tiene una fila por matrícula elegible y cutoff_day en {14,28,42,56}. Spark lee Gold, construye primero la población, agrega solo actividad disponible hasta el corte y une esas agregaciones mediante left join. La salida de features se mantiene separada de OUTCOME_ENROLLMENT.

## 1. Imagen y conexión privada

Desde la raíz, con Gold construido y los archivos privados ya preparados:

```bash
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/ejecutar_spark.py check-connection
```

La imagen propia conserva Spark 3.5.6, Scala 2.12.18 y Java 17. El conector es spark-snowflake_2.12 3.2.3-spark_3.5; JDBC 4.4.1; parquet-avro 1.13.1. Commons Lang se actualiza a 3.18.0, versión provided en el POM del conector. Los cuatro JAR se descargan durante build con URLs exactas, bytes y SHA-256 de jars.lock.json. Las dependencias Python se fijan por hashes, reutilizando la combinación Python 3.10/conector 4.7.4 ya resuelta para ingesta. No se guardan binarios JAR en Git.

La variante 3.2.3 para Scala 2.12 lleva sufijo spark_3.5 en Maven; el artefacto sin ese sufijo no existe. Las versiones, POM y límites probados se registran en [spark-dependencias.json](spark-dependencias.json). Esta combinación se prueba en linux/amd64; no se declara compatibilidad ARM sin validarla.

Compose monta código y los dos archivos privados como solo lectura. Como dbt, el cliente cloud puntual usa root para leer los archivos 0600 del host; no se cambia el permiso de las claves. No tiene socket Docker, puertos publicados ni interfaz Spark UI. El original cifrado permanece fuera del repositorio. Python descifra la clave solamente en memoria y proporciona pem_private_key dinámicamente al conector. Nunca se guarda una copia privada sin cifrar ni se pasa la clave como argumento CLI.

La sesión usa PSET2_SVC/PSET2_PIPELINE, PSET2_WH y el esquema ANALYTICS. Este esquema ya permite crear stages para la transferencia del conector. Las lecturas nombran explícitamente PSET2_OULAD.GOLD; no se amplían privilegios sobre Gold ni se usa un rol administrador. El [informe de conexión](spark-conexion.json) acredita contexto y cliente reales, sin escribir tablas.

## 2. Probar reglas antes de publicar

```bash
python3 pset-02/scripts/ejecutar_spark.py test-features
```

Son casos sintéticos, no resultados OULAD: retiro exactamente en el corte, registro tardío/desconocido, ventanas 1–14 y 15–28, cambio, recencia, matrícula sin actividad, IMD ausente y modificación de eventos futuros. El [informe](spark-pruebas.json) distingue este alcance de la construcción real.

La regla de población exige registro conocido <= 0 y retiro no registrado o > cutoff_day. Un retiro exactamente en el corte excluye la matrícula; uno posterior no la excluye en ese corte. La fecha posterior no se copia a features. No se usa final_result para reconstruir elegibilidad. Persisten las 93 matrículas Withdrawn sin fecha y su incertidumbre histórica.

## 3. Construir desde Gold y publicar la OBT

```bash
python3 pset-02/scripts/ejecutar_spark.py build-obt
python3 pset-02/scripts/resumir_obt.py
```

El auxiliar ejecuta spark-submit local[2] en un contenedor puntual de la imagen propia. No requiere un clúster master/worker. El montaje de datasets sigue siendo de solo lectura, aunque las observaciones se leen de Gold. Se comprueba que las cinco huellas de linaje Gold coincidan con el manifiesto; no se mezclan versiones silenciosamente.

La extracción de actividad usa únicamente columnas necesarias y días <= 56. Esa poda reduce transferencia; las agregaciones y joins se ejecutan en Spark con autopushdown=off por DataFrame. Cada cálculo vuelve a filtrar <= su corte. Los inputs se cachean en disco y los cuatro cortes se procesan secuencialmente, con dos hilos, driver de 1 GiB y 16 particiones de shuffle adaptativo. Son parámetros probados de este equipo, no mínimos universales. Los temporales y Parquet derivados quedan en .local/spark y fuera de Git.

Para cada corte se comprueba igualdad bidireccional de claves contra una referencia SQL de elegibilidad calculada independientemente desde Gold, no solo igualdad de conteos. El resumen compara además filas y ausencia de actividad con la auditoría del PSet 1.

## 4. Contrato de variables

La [lista de columnas y roles](../spark/feature-contract.json) es explícita: identificadores para joins/partición, antecedentes estáticos, actividad y campos de auditoría. IDs y códigos no se convierten automáticamente en predictores. No hay notas de assessments, resultados finales, probabilidades, fecha de retiro ni banderas retrospectivas en la tabla de features.

| Grupo | Definición |
|---|---|
| Estáticas | Género, región, educación, IMD, edad agrupada, intentos previos, créditos, discapacidad, indicador IMD, duración y días de registro antes del inicio |
| Acumulados | Clics y días activos registrados <= corte, recursos distintos y tipos de recurso distintos |
| Preinicio y cero | Clics con día < 0 y clics del día 0, separados; el acumulado total los incluye explícitamente |
| Desde día 1 | clicks_since_start suma días 1..corte; completa la reconciliación preinicio + cero + desde día 1 = total |
| Ventana actual | Clics/días activos en corte-13..corte; clics forumng y oucontent en ese mismo intervalo |
| Ventana anterior | Clics en corte-27..corte-14, solo desde corte 28; en corte 14 queda NULL |
| Cambio y razón | Actual menos anterior; razón actual/anterior cuando anterior > 0. NULL si no hay comparación definida |
| Recencia | Corte menos último día con interacción registrada <= corte; NULL cuando no hay actividad registrada |
| Cobertura | has_recorded_activity señala presencia de registros; log_coverage_known permanece false por falta de evidencia de cobertura completa |

Los contadores de registros se rellenan con cero tras el left join: expresan ausencia de registros en la fuente, no certeza de cero actividad académica real. La recencia permanece desconocida en esos casos. No se usa un sentinel numérico ni se aprende una imputación globalmente. La futura política operativa de recencia deberá fijar cómo ordenar esos casos desconocidos antes de evaluar.

IMD conserva NULL y su bandera. No se escalan variables, ajustan codificadores, seleccionan predictores ni entrenan modelos. Esas transformaciones aprendidas corresponderán al entrenamiento, con particiones por alumno y tiempo y sin utilizar prueba final para ajustarlas.

## 5. Pruebas temporales y lectura de vuelta

En cada corte real se modifican masivamente clics posteriores y se inserta una contribución de cutoff+1 para una matrícula elegible. Se vuelven a calcular features y se exige igualdad completa en ambas direcciones. Es una prueba de aislamiento de actividad futura para la transformación implementada; no demuestra que todos los atributos históricos de OULAD tengan disponibilidad institucional comprobada.

También se verifica unicidad matrícula–corte, conservación tras joins, recencia no negativa, ausencia de día posterior al corte y ventanas actuales de máximo 14 días. La primera diferencia quincenal debe ser NULL. Se generan huellas SHA-256 por corte sobre filas JSON con columnas y nulos explícitos, ordenando sus hashes para independizar la comparación del orden de ejecución.

Spark escribe primero una tabla OBT_FEATURES_BUILD_<run_id> en ANALYTICS. Se lee de vuelta y compara contra el DataFrame completo, en ambas direcciones, con tipos alineados. Solo entonces se publica OBT_FEATURES mediante rename inicial o swap atómico de tablas. Un marcador de contrato protege un destino homónimo ajeno al proyecto. Se conserva el último destino válido si falla una comprobación anterior a la publicación. La tabla provisional de construcción se retira al finalizar; los stages de transferencia son gestionados por el conector.

La atomicidad se refiere a la publicación de esta tabla; no es una transacción de Raw, dbt y Spark juntos. Ejecutar un único escritor y no reconstruir Gold durante la OBT. La tabla final tiene solo las columnas permitidas; metadata de ejecución y huellas se guardan en el informe y en el comentario de contrato.

## 6. Evidencia, repetición y operación

El [informe OBT](obt-verificacion.json) registra ejecución, población por corte, pruebas temporales, lectura de vuelta y huellas. El resumen Markdown se genera desde ese informe, el contrato y la auditoría previa. No copiar logs completos ni planes con opciones cloud al repositorio. Los auxiliares publican estados y agregados; diagnósticos completos permanecen en .local/spark, excluido de Git.

Repetir build-obt vuelve a construir y reemplazar el destino validado, sin append. Las huellas por corte permiten comparar el contenido de dos ejecuciones. No modificar Gold entre ellas. Los archivos de trabajo locales no se versionan y pueden retirarse después de verificar la evidencia.

Procedimiento para comprobar repetición después de un build exitoso:

```bash
python3 pset-02/scripts/comprobar_repeticion_obt.py checkpoint
python3 pset-02/scripts/ejecutar_spark.py build-obt
python3 pset-02/scripts/comprobar_repeticion_obt.py verify
python3 pset-02/scripts/resumir_obt.py
```

El checkpoint guarda solo campos agregados públicos y huellas en output/spark/repetition-baseline.json. verify exige dos runs distintos publicados y compara filas, claves, esquema, población, métricas y las cuatro huellas de contenido; el resumen acredita esa prueba solo si corresponde al run actual.

Se ejecutaron dos construcciones completas: 108.277 filas y 35 columnas en cada una, cuatro perturbaciones reales y lectura de vuelta aprobadas. Las cuatro huellas canónicas coinciden. [Informe de repetición](repeticion-obt.json) y [resultados](obt-resultados.md). Las ejecuciones standalone iniciales fueron el 12-nov local; la ejecución integral posterior terminó el 13-nov local. Los informes actuales conservan tiempos UTC. Los siete casos sintéticos pasaron por separado.

La estrella Gold sirve para análisis dimensional reutilizable. OBT_FEATURES sirve para consumo predictivo por matrícula–corte; las etiquetas se consultarán aparte desde OUTCOME_ENROLLMENT. Los acumulados de distintos cortes no se suman como si fueran eventos diferentes.

Este paso usa transferencia, cómputo y almacenamiento Snowflake; no se ha cuantificado costo monetario. La infraestructura conserva auto-suspend y trabajos puntuales; no se afirma gratuidad. La cadena completa ya se integró y verificó con Kestra: [guía](orquestacion-integral.md), [resultados](pipeline-resultados.md). La reproducción desde exportación limpia también se verificó: [guía](reproduccion-limpia.md), [resultados](reproduccion-resultados.md). El [memo técnico de seis páginas](memo-tecnico.md) ya está generado y verificado. La publicación GitHub sigue reservada para el cierre.

Referencias: [Snowflake: uso del conector y clave dinámica](https://docs.snowflake.com/en/user-guide/spark-connector-use), [instalación y compatibilidad](https://docs.snowflake.com/en/user-guide/spark-connector-install), [release notes 2026 y dependencia JDBC](https://docs.snowflake.com/en/release-notes/clients-drivers/spark-connector-2026). La combinación instalada y la ejecución se verifican en los informes del proyecto.
