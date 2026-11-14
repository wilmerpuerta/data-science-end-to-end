# Paso 9B: reproducción desde una exportación limpia

La prueba crea otra carpeta de trabajo, otro proyecto Compose, otros puertos, nuevos volúmenes PostgreSQL/Kestra y contraseñas locales recién generadas. Ejecuta la cadena sin .venv, .local, cachés ni salidas heredadas del PSet 2. Los datos y la configuración Snowflake son dependencias externas explícitas.

## 1. Alcance que se comprueba

La fuente es una exportación de archivos versionables seleccionados por Git desde el árbol de trabajo. Se omiten secretos, entornos, caches, binarios JAR y output/ del PSet 2. Se conservan código, Dockerfiles, locks, Markdown y los entregables públicos previos, incluido el manifiesto y la auditoría de PSet 1 usada como referencia independiente.

No es un clon remoto ni prueba el alta de una cuenta Snowflake nueva. El repositorio aún no se ha publicado. La cuenta, rol, warehouse y esquemas Snowflake existentes se reutilizan. La carga Raw se fuerza para reconstruir los cinco originales, seguida de dbt y OBT; no se demuestra la ingesta aprovechando cinco NOOP.

Las imágenes propias se reconstruyen con --no-cache, descargando las dependencias fijadas por hash. Las capas base de Docker siguen disponibles y se identifican por digest; no se afirma un daemon Docker vacío ni una máquina nueva. El aislamiento comprobado corresponde al directorio, estado de servicios, volúmenes, configuración local y ejecución.

## 2. Preparar la copia

Desde la raíz original, con Docker disponible y la configuración externa ya preparada:

```bash
python3 pset-02/scripts/reproduccion_limpia.py prepare
```

La orden devuelve un run_id, nombre de proyecto, puertos y huellas de exportación/código. Antes de copiar, verifica bytes y SHA-256 de los cinco CSV. Por defecto los toma de datasets/; --data-dir permite otra carpeta identificada. Los CSV no se duplican: la prueba los monta como solo lectura desde la carpeta externa seleccionada.

La copia queda bajo tmp/reproduccion-<run_id>/repo, excluido de Git. Se comprueba que no existan .venv, .local, .env.infra, .env.cloud ni output del PSet 2 antes de configurarla. Se genera .env.infra nuevo; no se copia el archivo de contraseñas original. .env.cloud se reconstruye con las dos rutas externas autorizadas, sin leer ni copiar el contenido de la clave o del JSON privado.

Los puertos predeterminados de la prueba son 18080/18081; --port elige el primero de otro par libre. El proyecto usa un nombre único pset2repro_<run_id>. La configuración admite PSET2_COMPOSE_PROJECT_NAME, PSET2_KESTRA_PORT y PSET2_KESTRA_MANAGEMENT_PORT; los defaults del stack principal siguen siendo pset2 y 8080/8081. Los clientes HTTP leen el puerto del archivo privado local, sin depender de 8080 fijo.

## 3. Ejecutar y restaurar

Usar el ID devuelto por prepare:

```bash
python3 pset-02/scripts/reproduccion_limpia.py run --run-id ID_PREPARADO
```

El auxiliar realiza, en orden:

1. Detiene temporalmente el stack principal, conservando contenedores, volúmenes y configuración.
2. Valida Compose y obtiene imágenes fijadas; reconstruye las tres imágenes propias sin cache de capas propias.
3. Arranca el proyecto aislado con volúmenes nuevos y espera salud de sus cinco servicios.
4. Crea y ejecuta infra_smoke en el Kestra nuevo y comprueba rechazo de acceso sin autenticación.
5. Despliega Raw e integral en esa instancia, sin reutilizar el estado de flujos de la original.
6. Ejecuta oulad_pipeline con force_reload=true, defaults de fallos=false, y exige SUCCESS con verificación completa.
7. Detiene la reproducción y restaura el stack principal con espera de salud, también al salir ante un fallo.

Los logs completos y el estado del auxiliar permanecen en .local/reproduction, fuera de Git. No incluyen valores privados en los informes públicos. La prueba no se relanza silenciosamente con un ID iniciado: revisar la causa y preparar otra copia si falla. La restauración de servicios también se registra; un fallo en ese cierre impide certificar la reproducción.

La recarga modifica únicamente las tablas gestionadas del proyecto, con la misma versión de datos. Snowflake no está aislado en otra cuenta/base; por eso el stack principal se detiene y no deben iniciarse operaciones manuales mientras dura la prueba. La atomicidad sigue siendo por carga/modelo/publicación OBT.

## 4. Recoger y comparar evidencia

```bash
python3 pset-02/scripts/reproduccion_limpia.py collect --run-id ID_PREPARADO
python3 pset-02/scripts/resumir_reproduccion.py
```

collect exige cinco fuentes LOADED, 10.726.852 filas Raw reconciliadas, 168 pruebas dbt aprobadas y OBT publicada de 108.277 filas. Comprueba que el código copiado permanezca intacto y que las cuatro huellas de contenido OBT coincidan con la ejecución anterior. Copia únicamente los informes agregados nuevos a output/reproduction/<run_id>/ y genera docs/reproduccion-limpia.json.

El resumen Markdown se genera desde ese JSON y la verificación nueva. Sus tiempos son UTC; el relato de la prueba utiliza America/Guayaquil. Los informes no publican rutas personales, credenciales, logs ni CSV. La huella de exportación identifica la instantánea probada; los informes finales y esta explicación pueden añadirse posteriormente sin cambiar el código del pipeline que se ejecutó.

La reproducción queda detenida, con su copia y volúmenes conservados para poder inspeccionar la evidencia local; no se ejecuta down -v ni se borran volúmenes originales. El stack principal queda restaurado. La tabla Snowflake final contiene la reconstrucción validada más reciente. El histórico de la instancia original de Kestra se conserva en sus propios volúmenes; la ejecución aislada se consulta mediante sus informes o volviendo a levantar esa instancia con su configuración privada.

## 5. Interpretación y cierre

Una prueba exitosa acredita que el código exportado arranca con estado local nuevo y reconstruye los mismos datos finales usando dependencias identificadas. No acredita permisos administrativos en otra cuenta, precio contractual de créditos, compatibilidad ARM ni una descarga independiente de otra versión OULAD. El SQL de aprovisionamiento, datos y claves continúan siendo prerrequisitos para un tercero.

Después de esta comprobación se generó el [memo de seis páginas](memo-tecnico.md). Quedan la cuantificación de costo monetario cuando haya acceso a la información de consumo/precio y la revisión final antes de GitHub. No hay entrenamiento ni publicación remota automática como parte de esta prueba.
