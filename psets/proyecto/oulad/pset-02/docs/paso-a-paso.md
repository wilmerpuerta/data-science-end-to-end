# Paso a paso del PSet 2

Base: [enunciado](../enunciado.md) y [rúbrica](../rubrica.md). Trabajar en la raíz existente del repositorio. GitHub se aborda únicamente al final. La existencia de archivos de configuración no acredita ejecución: cada paso debe cerrar con evidencia antes de marcarlo verificado.

## 1. Comprobar el entorno y proteger la configuración

Desde la raíz:

```bash
python3 pset-02/scripts/diagnostico.py --output pset-02/docs/diagnostico-local.json
```

El script utiliza la biblioteca estándar, comprueba las cinco entradas contra el manifiesto y consulta versiones y disponibilidad de Docker. No instala paquetes, lee credenciales ni inicia contenedores. Un resultado distinto de cero señala requisitos pendientes; consultar los estados del JSON. Se puede usar `--data-dir` para una ruta autorizada alternativa. El informe describe este equipo, no requisitos mínimos universales.

Si Docker está instalado pero el motor no responde, abrir Docker Desktop, esperar a que el motor termine de iniciar y repetir. Distinguir problemas de permisos de acceso al socket de un motor detenido. No reinstalar Docker por un error de acceso.

La cuenta y conexión del host ya se verificaron. Después se comprobaron conexión y permisos de carga desde Kestra para Raw; dbt cloud y Bronze también se comprobaron posteriormente; Spark cloud también se comprobó; ver obt-spark.md. Guardar secretos únicamente en configuración local excluida de Git. .env.example contendrá nombres y ejemplos ficticios. Las claves privadas se guardarán preferentemente fuera del repositorio y se montarán como solo lectura. No pegar claves, contraseñas ni tokens en Markdown, código, YAML, notebooks, comandos registrados o evidencias. No capturar `env`, `docker inspect` o un Compose expandido con secretos como documentación.

Cierre del paso: hashes coincidentes, motor Docker accesible, Compose disponible y exclusiones Git comprobadas. No se requiere conexión cloud para cerrar este diagnóstico local.

## 2. Fijar arquitectura y versiones compatibles

Arquitectura objetivo: CSV → Kestra → Snowflake Raw → dbt Bronze/Staging → dbt Silver → dbt Gold → Spark OBT → Snowflake.

Usar dbt Core en Docker como decisión de trabajo: código, adaptador y dependencias pueden versionarse junto al proyecto. Compose incluirá Kestra, Spark y los servicios auxiliares que exija la configuración elegida. Resolver compatibilidad entre Spark, Scala, Java, conector Snowflake y JDBC antes de fijar versiones. Registrar versiones e imágenes por digest comprobado; no usar latest ni inventar locks.

El montaje `../datasets` se resolverá desde pset-02 y será de solo lectura. Los contenedores no dependerán de rutas personales. Definir almacenamiento persistente de Kestra y directorios temporales separados de los CSV.

Cierre: Compose real, configuración validada sin divulgar secretos y versiones probadas. No generar un Compose de relleno para aparentar avance.

## 3. Configurar Snowflake y probar autenticación

Preparar un rol del proyecto, warehouse acotado, base y esquemas RAW, BRONZE, SILVER, GOLD y un destino de OBT. Documentar creación, permisos y limpieza como parte de la reproducción cloud. Elegir autenticación compatible con la cuenta y los tres clientes; se propone evaluar par de claves para ejecución desatendida, sujeto a política y permisos reales. No asumir que contraseña sin MFA será válida.

Publicar solamente SQL de aprovisionamiento con parámetros, perfiles con referencias al entorno y ejemplos ficticios. Aplicar auto-suspend y límites de ejecución antes de cargar datos. Primero probar una consulta mínima y registrar éxito sin datos de autenticación.

Cierre: conexión verificada y privilegios mínimos suficientes. La creación de recursos y el consumo cloud se coordinarán cuando este paso esté preparado con configuraciones concretas.

## 4. Levantar y verificar la infraestructura local

Después de implementar Compose, documentar comandos exactos en README para construir imágenes, levantar servicios, comprobar salud, detenerlos y conservar o limpiar volúmenes. Primero validar servicios locales; después probar desde cada cliente la conexión requerida con Snowflake.

Los comandos de arranque y comprobación de infraestructura local ya se verificaron y están en README e infraestructura-local.md. Kestra está disponible en http://localhost:8080. La ingesta Raw se ejecutó y verificó posteriormente; ver ingesta-raw.md. Bronze, Silver y Gold se construyeron después; Spark/OBT ya se ejecutó: [guía](obt-spark.md) y [resultados](obt-resultados.md).

Cierre: Kestra y Spark saludables, persistencia comprobada y datos accesibles en solo lectura desde el contenedor consumidor.

## 5. Implementar Kestra y Raw

Crear carga inicial sin pasos manuales entre archivos. Registrar versión de datos, checksum, run_id, partición módulo–edición, filas y resultado. Conservar Raw fiel al original con linaje de fila/carga; las claves matrícula–recurso–día repetidas de actividad no autorizan eliminar filas silenciosamente.

Implementar trigger, frecuencia y retries para fallos transitorios. OULAD es histórico: una ejecución periódica comprueba cambios y no implica que el proveedor publique datos nuevos. Backfill por particiones con reanudación y control de versiones. Carga repetida de la misma versión/partición debe producir el mismo estado, sin duplicados adicionales.

Cierre: cinco tablas Raw reconciliadas con archivos, reejecución idempotente y evidencia de retry/backfill sin secretos.

## 6. Calidad y transformaciones dbt

Bronze/Staging ya está implementado: seguir la [guía detallada](calidad-bronze.md), con comandos ejecutados y [resultados globales](calidad-bronze-resultados.md). Cinco vistas, una tabla agregada y 45 tests aprobados. Silver también está implementado: [guía de consolidación](silver.md), [resultados](silver-resultados.md), 101 tests Bronze/Silver aprobados. Gold también está construido: [guía y diagrama](gold.md), [resultados](gold-resultados.md). Spark/OBT ya se ejecutó: [guía](obt-spark.md) y [resultados](obt-resultados.md). La orquestación completa y la reproducción limpia también están verificadas; el [memo técnico](memo-tecnico.md) está generado. La conexión usa secretos externos montados como solo lectura; los artefactos completos quedan en .local/dbt, fuera de Git.

Bronze/Staging: tipos y anomalías trazables. Silver: limpieza y reglas justificadas. Usar source() y ref(). Incorporar pruebas not_null, unicidad de claves compuestas, relationships, dominios, fechas contextuales y cardinalidad.

Cuantificar completitud, validez, consistencia y límites de exactitud externa. Registrar problema–evidencia–acción–justificación. Investigar las repeticiones de actividad antes de acordar agregación: conservar filas Raw y reconciliar filas/clics transformados. No convertir nulos de retiro en errores indiscriminadamente ni excluir ceros de actividad.

Cierre: ejecución dbt y pruebas con evidencia, decisiones de limpieza documentadas y anomalías pendientes explícitas.

## 7. Construir Gold con esquema estrella

Implementado y comprobado: cinco dimensiones, dos hechos, dos tablas complementarias y perfil de calidad. El build aprobó 168 tests de las tres capas; los joins conservaron filas y clics, y la población por corte coincide con PSet 1. Seguir [gold.md](gold.md) para ejecutar y reproducir la evidencia.

Aplicar el [contrato](contrato-datos.md) y definir el grano de cada hecho y dimensión. Los atributos del estudiante que varían entre matrículas no deben sobreescribirse como si fueran constantes globales. Agregar actividad antes de unir antecedentes para evitar multiplicaciones.

Cierre: diagrama de la implementación, dimensiones y hechos persistidos en Snowflake, claves y totales reconciliados.

## 8. Construir la OBT con Spark

Implementado y comprobado: [guía detallada](obt-spark.md), [resultados](obt-resultados.md), conexión cloud real y ANALYTICS.OBT_FEATURES con 108.277 filas/35 columnas. Las cuatro poblaciones y ausencias coinciden con PSet 1; lectura de vuelta completa y perturbación de actividad futura aprobadas. Seguir el procedimiento de la guía para reproducir.

Grano matrícula–corte para días 14, 28, 42 y 56. Construir primero elegibilidad, preservar matrículas sin actividad y agregar solo eventos disponibles al corte. Separar resultados finales y fecha futura de retiro de los predictores. Imputación y escalado aprendidos corresponden al futuro entrenamiento, no al ELT global.

Persistir la OBT en Snowflake. Probar igualdad de claves y N antes/después de joins, unicidad, ausencia de fuga y reconciliación de clics. Comparar N por edición con la auditoría del PSet 1, explicando cualquier diferencia justificada de reglas. OBT sirve al modelo; estrella sirve al análisis dimensional reutilizable.

Cierre: trabajo Spark ejecutado, tabla final disponible y evidencia de los tests.

## 9. Demostrar reproducción completa

La cadena integrada ya se ejecutó desde Kestra: [guía de orquestación](orquestacion-integral.md), [resultados](pipeline-resultados.md). SUCCESS con retry controlado, detención tras fallo permanente, 168 tests y OBT publicada. También se comprobó una exportación limpia en otro proyecto Compose: [procedimiento](reproduccion-limpia.md), [resultados](reproduccion-resultados.md). Se usaron volúmenes nuevos y recursos Snowflake existentes; no se afirma clon remoto ni alta de cuenta nueva.

Ejecutar desde una copia limpia con datos de hashes identificados, configuración local y recursos Snowflake documentados. Seguir únicamente README para levantar infraestructura, ejecutar Kestra, dbt y Spark en orden y verificar artefactos. Repetir una partición y simular un fallo recuperable. Documentar tiempos, recursos y consumo observados, sin afirmar gratuidad.

Cierre: instrucciones suficientes para un tercero, versiones resueltas, idempotencia y recuperación comprobadas, logs sanitizados. Batch satisface la revisión quincenal; explicar qué fuente continua y necesidad de baja latencia justificarían streaming, sin implementarlo.

## 10. Preparar entrega y publicar al final

El [memo técnico de seis páginas](memo-tecnico.md) ya está generado desde [Markdown](../memo-pset2.md), con dos diagramas, métricas y limitaciones de la implementación real. Su guía relaciona cada criterio de rúbrica con las páginas correspondientes. La fuente y el PDF se comprueban mediante scripts reproducibles.

Antes de cualquier commit, revisar los archivos concretos que se incluirán. Antes de publicar, revisar además el historial y ejecutar una comprobación de secretos. Si una credencial se incorporó a Git, excluir el archivo después no la borra del historial: revocarla y corregir la historia antes de publicar. Datos originales, .env, claves, caches y salidas voluminosas quedan fuera.

Crear el remoto y subir a GitHub únicamente cuando el paquete esté revisado y el autor indique publicarlo. No se ha creado un remoto en esta etapa.

## Referencias técnicas para implementar

- Kestra, despliegue con Docker Compose y PostgreSQL: https://kestra.io/docs/installation/docker-compose.
- dbt, configuración Snowflake y autenticación: https://docs.getdbt.com/docs/local/connect-data-platform/snowflake-setup.
- Snowflake, instalación y compatibilidad del conector Spark: https://docs.snowflake.com/en/user-guide/spark-connector-install.

Las referencias orientan la selección. Las versiones específicas se fijarán tras resolver y probar compatibilidad en este equipo.
