# Paso 9A: ejecución integral desde Kestra

El flujo `pset2.oulad/oulad_pipeline` coordina Fuente → Raw → dbt Bronze/Silver/Gold → Spark → OBT → verificación. Una sola ejecución padre controla el orden; no requiere lanzar manualmente dbt o Spark después de Raw. La publicación GitHub sigue reservada para el cierre.

## 1. Servicios y despliegue

Con Docker abierto, datos de hashes identificados y configuración privada preparada:

```bash
python3 pset-02/scripts/infra.py build --cloud
python3 pset-02/scripts/infra.py validate --cloud
python3 pset-02/scripts/infra.py up --cloud
python3 pset-02/scripts/infra.py status --cloud
python3 pset-02/scripts/ejecutar_pipeline.py --deploy
```

El Compose cloud añade dbt-runner y spark-runner. Reutilizan exactamente las imágenes y dependencias ya probadas; no crean un cuarto entorno de transformación dentro de Kestra. Son servicios internos sin puertos publicados, sin socket Docker y con código/archivos privados montados como solo lectura. No se guardan contraseñas, claves ni tokens en YAML o inputs del flujo. Los secretos solo los leen los clientes dentro del ejecutor correspondiente.

Los ejecutores usan una API HTTP mínima de la red Compose. Solo aceptan un execution_id válido; el tipo de servicio determina el único trabajo permitido: dbt build-gold con exportaciones de calidad, o Spark build-obt. No aceptan comandos, rutas, credenciales ni argumentos libres. Este es un despliegue local de un autor: la red Docker es la frontera de confianza; no se presenta como un servicio multiusuario expuesto a Internet. Kestra conserva su autenticación y sus puertos localhost.

Cada ejecutor mantiene una cola de un trabajo a la vez. Un POST repetido para una ejecución QUEUED, RUNNING o SUCCESS devuelve el mismo job_id e intento. Si el trabajo terminó FAILED, una nueva petición inicia el siguiente intento. Así una respuesta perdida no inicia una segunda construcción simultánea. Los estados y logs completos se guardan en .local/orchestration, fuera de Git; solo informes agregados se escriben en output/pipeline/<execution_id>/.

Al reiniciar un ejecutor, sus trabajos que quedaron RUNNING/QUEUED pasan a FAILED por interrupción; no se presume que terminaron correctamente. Un reintento posterior reconstruye con las mismas reglas idempotentes. Las pruebas de esta etapa validan duplicación de peticiones, fallo inyectado y retry; no acreditan recuperación frente a todas las modalidades de caída del proveedor o del equipo.

## 2. Ejecutar la cadena

```bash
python3 pset-02/scripts/ejecutar_pipeline.py
```

En la interfaz Kestra, elegir namespace pset2.oulad y flujo oulad_pipeline. Defaults: source_file=all, force_reload=false y ambas pruebas de fallo=false. La secuencia es:

1. **raw:** llama al subflujo oulad_raw y espera su finalización. Un fallo se transmite al padre. Conserva checksum, idempotencia, publicación por fichero y backfill ya implementados.
2. **gate:** confirma que se puede avanzar; normalmente no introduce cambios. Permite probar fallos controlados antes de transformar.
3. **dbt:** envía un trabajo fijo al ejecutor, espera su resultado y exige todos los modelos/tests correctos. Refresca las métricas de las tres capas. Build y exportaciones tienen un límite conjunto de 15 minutos; Kestra permite hasta tres intentos con espera exponencial.
4. **spark:** inicia build-obt y espera publicación validada. Conserva población, pruebas temporales y lectura de vuelta del paso 8. El trabajo tiene límite de 20 minutos y hasta dos intentos de tarea Kestra.
5. **verificar:** reconcilia los informes de esta ejecución, las fuentes seleccionadas, el orden temporal de etapas, las 168 pruebas dbt, población Gold/PSet 1, columnas permitidas y OBT publicada.

La clave de correlación es la ejecución padre. Raw tiene su propio execution_id de subflujo; dbt y Spark registran padre, job_id e intento. La OBT conserva su marcador de contrato y run_id de Spark. El informe de verificación exige que las etapas correspondan al mismo padre y estén en orden.

Concurrency limit=1, behavior=QUEUE, serializa este flujo padre. No ejecutar cargas o transformaciones manuales paralelas: sus comandos independientes no comparten una transacción ni un bloqueo global con el padre. Los límites de contenedor son los documentados; dbt y Spark trabajan secuencialmente. Dos ejecutores adicionales en espera no significan dos trabajos pesados simultáneos.

El calendario padre está configurado para días 1 y 15 a las 09:00 America/Guayaquil y permanece desactivado. El calendario del subflujo Raw también permanece desactivado. Si se decide automatizar el calendario al cerrar operación, activar solo el padre para evitar disparos independientes de Raw. OULAD es un histórico estático; la frecuencia no crea nuevos datos ni implica actualización del proveedor. No se ha observado un disparo horario automático.

## 3. Backfill y consulta de una ejecución

```bash
python3 pset-02/scripts/ejecutar_pipeline.py --file courses.csv --force-reload
python3 pset-02/scripts/ejecutar_pipeline.py --resume-execution ID_DE_EJECUCION
```

El backfill se particiona por fichero/checksum, conforme a la implementación Raw. Después reconstruye las capas y la OBT completas para mantener consistencia; no es backfill incremental por módulo–edición. El ejemplo es el comando disponible, no evidencia de que se haya ejecutado ese backfill integral. El backfill Raw de courses.csv ya tenía su evidencia separada.

resume-execution consulta y registra un flujo existente; no relanza ni reinicia sus tareas. Si el cliente agota la espera, comprobar esa ejecución antes de crear otra. Para recuperarse de un flujo realmente FAILED, corregir la causa y crear una ejecución nueva: Raw reevalúa los hashes y las capas se reconstruyen. Los reportes permiten distinguir intentos y ejecuciones.

La atomicidad sigue siendo por fichero Raw, materialización dbt y publicación OBT. Un fallo posterior no revierte automáticamente todas las tablas previas. No consumir una ejecución incompleta como si fuera un snapshot integral válido; revisar SUCCESS más verification.json. Una interrupción forzada puede dejar una tabla provisional de construcción, que requiere revisión antes de retirarla; el código no elimina objetos ajenos al contrato.

## 4. Probar detención y recuperación

Fallo permanente controlado después de Raw:

```bash
python3 pset-02/scripts/ejecutar_pipeline.py --fail-after-raw
```

Ese comando debe finalizar con código distinto de cero. Raw puede completar antes del fallo; dbt y Spark no deben iniciarse. La prueba realizada usó source_file=all y force_reload=false y obtuvo cinco NOOP; no se fuerza una recarga para demostrar la detención. El FAILED deliberado se conserva como evidencia y no se confunde con una ejecución productiva exitosa.

Fallo transitorio controlado una vez:

```bash
python3 pset-02/scripts/ejecutar_pipeline.py --retry-probe
```

gate falla una vez, se reintenta y después permite continuar. No hay entrenamiento, edición de credenciales ni modificación artificial de tablas cloud para inyectar esos fallos. Las pruebas no reproducen una caída real de Snowflake.

El sondeo API comprueba HTTP 400 ante campos de comando libre y que no se cree un trabajo. Con un trabajo válido ya existente, repite POST y exige mismo job_id/intento. La evidencia queda en api-probe.json; no se envían opciones de conexión a la API.

## 5. Publicar evidencia y regenerar Markdown

Solo después de un padre SUCCESS con verification.json válido:

```bash
python3 pset-02/scripts/publicar_evidencia_pipeline.py ID_EXITOSO
python3 pset-02/scripts/resumir_raw.py
python3 pset-02/scripts/resumir_bronze.py
python3 pset-02/scripts/resumir_silver.py
python3 pset-02/scripts/resumir_gold.py
python3 pset-02/scripts/resumir_obt.py
python3 pset-02/scripts/resumir_pipeline.py
```

El publicador actualiza el build Gold, las métricas de las tres capas y el informe OBT desde los reportes curados de ese padre. Las comprobaciones standalone previas siguen siendo evidencia histórica; el informe integral enlaza la ejecución nueva y sus tiempos. Los resúmenes Markdown se generan desde JSON, no se editan cifras a mano.

resumir_pipeline.py exige las evidencias del fallo deliberado, éxito con retry, sondeo API y verificación. No marca un flujo correcto únicamente porque haya tablas en Snowflake. Los checks de repetición previos solo se atribuyen al build/run correspondiente; para comparar la cadena nueva con una ejecución anterior, guardar checkpoints Gold/OBT antes del flujo y ejecutar sus verificadores después de publicar evidencia.

Consultas y tablas siguen siendo las de los pasos Raw, dbt y OBT. No copiar .env, logs, planes, claves o respuestas privadas de API al repositorio. El pipeline utiliza cómputo y almacenamiento Snowflake; todavía no se ha cuantificado costo monetario.

## Cierre y límites

Esta etapa prueba la cadena integrada y sus controles. La reproducción desde una exportación limpia ya se verificó: [procedimiento](reproduccion-limpia.md), [resultados](reproduccion-resultados.md). El [memo técnico de seis páginas](memo-tecnico.md) ya está generado; queda la revisión final para publicar GitHub. Los CSV originales, la configuración privada y los recursos Snowflake son dependencias explícitas: Compose por sí solo no reproduce una cuenta Snowflake.

Referencias: [Kestra Subflow y transmisión de estado](https://kestra.io/plugins/core/flow/io.kestra.plugin.core.flow.subflow), [salidas y espera del subflujo](https://kestra.io/docs/workflow-components/subflows). La compatibilidad efectiva se comprueba con Kestra v1.0.0 instalado, además de consultar la documentación actual.
