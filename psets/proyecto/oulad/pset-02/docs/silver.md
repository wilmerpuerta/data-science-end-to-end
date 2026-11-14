# Paso 6B: consolidación y reglas Silver

Este paso convierte Bronze en tablas Silver reproducibles mediante dbt. Separa antecedentes, registro y resultados retrospectivos; consolida la actividad diaria con una política explícita y cuantifica sus límites. Gold se implementó después según [gold.md](gold.md); Spark/OBT ya se ejecutó según [obt-spark.md](obt-spark.md); la orquestación completa ya verificada; ver orquestacion-integral.md.

## 1. Preparar y ejecutar

Desde la raíz, con la infraestructura y la configuración privada existentes:

```bash
python3 pset-02/scripts/ejecutar_dbt.py parse
python3 pset-02/scripts/ejecutar_dbt.py build-silver
python3 pset-02/scripts/ejecutar_dbt.py quality-export-silver
python3 pset-02/scripts/resumir_silver.py
```

`parse` valida el proyecto sin consultar datos. `build-silver` equivale a `dbt build --select tag:bronze tag:silver`: reconstruye Bronze y Silver y ejecuta sus pruebas. Incluir Bronze permite volver a validar los datos de entrada antes de consumirlos. No reconstruye Raw ni necesita volver a cargar los CSV. Los modelos usan ref() y las fuentes Bronze ya usan source().

`quality-export-silver` consulta únicamente DQ_SILVER_PROFILE y escribe métricas agregadas en docs/calidad-silver.json. `resumir_silver.py` genera el Markdown de resultados desde el build y las métricas; no se editan cifras a mano. El informe del build, no la mera existencia de las tablas, determina si el paso pasó sus pruebas.

Se utilizan las imágenes y secretos existentes: no hay nuevas credenciales ni dependencias Python. Los comandos completos y logs siguen en .local/dbt, fuera de Git. Los informes públicos contienen solo campos permitidos. Ejecutar un único escritor: no hacer backfill Raw mientras se construyen capas. Las tablas Silver son instantáneas; si cambia Raw, repetir build antes de exportar sus métricas.

El build real aprobó **101 pruebas: 45 de Bronze y 56 de Silver**. Se construyeron siete tablas Silver; [resultados y decisiones](silver-resultados.md), [build](dbt-build-silver.json) y [métricas](calidad-silver.json). Los informes usan UTC; las pruebas iniciales fueron el 12-nov local y la cadena integral se verificó después el 13-nov local.

## 2. Tablas, grano y limpieza

| Tabla en PSET2_OULAD.SILVER | Grano | Regla aplicada |
|---|---|---|
| SLV_EDITIONS | Módulo–edición | Conservar duración validada y linaje; no inventar fechas de calendario |
| SLV_RESOURCES | Módulo–edición–recurso | Conservar semanas y marcar IS_SCHEDULE_UNKNOWN si falta alguna |
| SLV_ENROLLMENTS | Matrícula | Lista explícita de antecedentes, sin resultado ni retiro; IS_IMD_MISSING señala IMD ausente |
| SLV_REGISTRATION | Matrícula | Mantener fechas y clasificar registro inicial mediante reglas deterministas |
| SLV_OUTCOMES | Matrícula | Resultado original y target de tres clases, con banderas retrospectivas de inconsistencia |
| SLV_ACTIVITY_DAILY | Matrícula–recurso–día | Sumar clics de todas las filas fuente y guardar multiplicidad y linaje |
| DQ_SILVER_PROFILE | Dataset–métrica | Instantánea agregada para reconciliación y decisiones |

Todas las matrículas permanecen en Silver, incluidas las que no tienen actividad. SLV_ENROLLMENTS se construye desde studentInfo, sin inner join con eventos. No se cruzan atributos personales entre ediciones como si fueran constantes globales. Las claves incluyen módulo y edición; los antecedentes siguen ligados a su matrícula.

El tipado y la conversión de vacíos a NULL ya ocurrieron en Bronze y se heredan. Silver no hace imputación estadística, escalado, selección de variables ni entrenamiento. Las semanas desconocidas no se convierten en cero. Un retiro no registrado no se convierte en una fecha artificial.

## 3. Decisión sobre repeticiones de actividad

El grano diario esperado es matrícula–recurso–día, pero la copia auditada tiene múltiples filas por esa clave. La política principal es aditiva: `click_count = SUM(sum_click)` y `source_row_count = COUNT(*)`. Por ejemplo, dos filas con 3 y 5 clics generan una fila diaria de 8 clics y multiplicidad 2. Dos filas con 3 y 3 generan 6 clics; no se elige una arbitrariamente.

Esto garantiza una clave diaria única y conserva la cantidad total de clics registrada. No demuestra que cada observación fuente represente un hecho diferente: el significado de las repeticiones sigue sin poder cotejarse con logs institucionales. La [publicación original de OULAD](https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/) describe date y sum_click, pero no justifica cómo corregir estas repeticiones concretas.

La tabla de calidad calcula además los clics que resultarían de colapsar filas idénticas, incluidos sus valores sum_click. Dentro de cada clave diaria, SUM(DISTINCT sum_click) representa esa operación; luego se suman los grupos. Es un escenario mecánico para cuantificar sensibilidad, no una corrección aplicada. La tabla principal conserva todas las contribuciones; la alternativa no se ofrece como predictor en SLV_ENROLLMENTS.

Linaje agregado: SHA-256 fuente, cantidad de versiones, mínimo/máximo de número de fila y multiplicidad. Los extremos de fila no describen un intervalo continuo ni enumeran todas las contribuciones. Para reconstruirlas, unir Bronze por la clave completa y el SHA; Raw conserva la fila original. DISTINCT_SOURCE_VALUE_COUNT mide cuántos valores sum_click diferentes hay dentro del grupo, no número de eventos reales.

Se conservan días negativos y día cero. Más adelante las ventanas 1–14, 15–28, 29–42 y 43–56 los tratarán como antecedentes separados, conforme al contrato. No se recortan fechas usando semanas de recursos con cobertura desconocida.

## 4. Registro, elegibilidad y resultados separados

Registro inicial tiene tres categorías mutuamente excluyentes:

- missing_registration: fecha de registro desconocida;
- registered_after_start: fecha > 0;
- registered_by_start: fecha <= 0.

IS_REGISTERED_AT_START representa solamente registro conocido hasta el inicio. No es todavía elegibilidad para un corte. Para la futura OBT, se exigirá además que no exista retiro conocido <= cutoff_day. Una matrícula con retiro posterior a un corte sigue elegible en ese corte; esa fecha posterior no será predictor. Los registros desconocidos y tardíos permanecerán en Silver, y sus exclusiones posteriores deberán contarse.

SLV_OUTCOMES conserva final_result y define target_class: Fail, Withdrawn o Approved (Pass + Distinction). TARGET_FAIL es retrospectivo. Las banderas de resultado Withdrawn sin fecha y otro resultado con retiro también son retrospectivas: no se copian a antecedentes, no fijan elegibilidad y no se usan para completar fechas. El problema de retiro sin fecha limita la reconstrucción histórica; una evaluación futura deberá declarar la incertidumbre y realizar sensibilidad sin usar la etiqueta para la selección operativa.

La separación de tablas y el test de columnas previenen inclusiones accidentales en este modelo, pero no son una separación de permisos: el rol del pipeline puede leer todas las capas. La OBT ya tiene su lista permitida y pruebas de actividad futura según obt-spark.md; la evaluación predictiva sigue pendiente.

## 5. Qué prueban los tests

Se validan claves únicas y no nulas según cada grano; relaciones por matrícula, recurso y edición; igualdad bidireccional de claves antes/después de las transformaciones; preservación de resultados por edición; categorías y política de registro; dominios de actividad y una sola versión de archivo por grupo. Un test de lista permitida impide agregar columnas de resultados o retiro a SLV_ENROLLMENTS.

Para actividad se comparan, por cada edición, número de claves diarias, filas fuente representadas y suma de clics. Además, MINUS en ambas direcciones comprueba que no aparecieron ni desaparecieron claves completas: la igualdad del total por sí sola no basta. Las reducciones de filas se deben a consolidación y se reconcilian mediante SOURCE_ROW_COUNT, no a eliminación silenciosa.

dbt reemplaza tablas completas; no añade filas incrementalmente en esta versión. Esto evita acumulación por reejecución. La atomicidad es por materialización dbt, no una transacción de todas las capas: si hay un fallo, detener el consumo posterior, revisar el informe y reconstruir después de corregirlo. No se declara exitoso un build con nodos fallidos o saltados.

Para repetir solo las pruebas de Silver sobre las tablas actuales:

```bash
python3 pset-02/scripts/ejecutar_dbt.py test-silver
```

Si cambió Raw, usar build-silver en su lugar. Las consultas se ejecutan en PSET2_WH con dos hilos dbt. La capa diaria ocupa almacenamiento adicional y usa cómputo Snowflake; no se ha cuantificado costo monetario. Las tablas actuales del proyecto no se eliminan como parte de este paso.

Para comprobar repetición después de un build y exportación exitosos:

```bash
python3 pset-02/scripts/comprobar_repeticion_silver.py checkpoint
python3 pset-02/scripts/ejecutar_dbt.py build-silver
python3 pset-02/scripts/ejecutar_dbt.py quality-export-silver
python3 pset-02/scripts/comprobar_repeticion_silver.py verify
python3 pset-02/scripts/resumir_silver.py
```

El checkpoint guarda solo evidencia agregada pública en output/silver/repetition-baseline.json. verify exige dos builds distintos con tests aprobados y compara todas las métricas, no tiempos ni metadatos de ejecución. El [informe de repetición](repeticion-silver.json) acredita los invariantes comprobados; no debe ejecutarse la carga Raw entre ambas mediciones. El resumen solo marca repetición comprobada cuando el informe corresponde al build actual; en un clon nuevo puede generarse antes y dejar esa comprobación pendiente.

## Límites y continuación

La exactitud externa sigue sin estar demostrada. No se garantiza cobertura completa de logs por matrícula; ausencia de actividad no acredita automáticamente cero actividad real. Se conservan esas matrículas para que la futura OBT no las pierda mediante joins. Las anomalías se señalan y se miden, no se ocultan porque los tests estructurales pasen.

Los resultados finales de esta etapa deben leerse en los informes generados y en el README actualizado tras ejecutar. Gold ya está construido con grano explícito en hechos y dimensiones: [guía](gold.md) y [resultados](gold-resultados.md). La OBT se construyó después según [obt-spark.md](obt-spark.md); aún no hay evaluación predictiva.
