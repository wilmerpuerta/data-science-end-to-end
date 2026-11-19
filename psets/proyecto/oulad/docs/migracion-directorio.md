# Cambio de directorio: verificación del 16-nov-2026

Nueva raíz: `MSDS_6003_CD_Erick_Naunay/Proyecto CD/psets`.

## Correcciones

Se repararon 84 lanzadores y archivos de activación de `.venv`, `pset-02/.venv` y `pset-03/.venv`. Solo se sustituyó el prefijo absoluto anterior en archivos de texto; se conservaron permisos, intérpretes externos y paquetes instalados. No fue necesario descargar ni reinstalar dependencias. El respaldo de cada archivo está en la carpeta `backup_directory` del [informe JSON](migracion-directorio.json), bajo tmp/ y excluida de Git.

Se actualizó el destino del estado privado de la reproducción limpia y su referencia OULAD_DATA_DIR. No se alteraron sus evidencias públicas ni su código exportado. Los contenedores históricos de `pset2repro_849681d33298` siguen detenidos con sus metadatos originales; para reutilizar ese entorno hay que recrearlo desde el destino actualizado, conservando volúmenes. No usar `docker start` directamente sobre esos contenedores antiguos. Una nueva reproducción genera una nueva exportación con rutas actuales.

Se recrearon los cinco servicios activos de PSet 2 y el servidor MLflow usando las imágenes ya instaladas y los mismos nombres de proyecto/volúmenes. Se comprobó antes que no hubiera ejecuciones Kestra ni trabajos de runners activos. No se regeneraron contraseñas ni claves. Las rutas de los dos archivos privados Snowflake están fuera del directorio renombrado y siguen siendo válidas.

## Verificación

- Los tres entornos pasan uv pip check; Jupyter, JupyterLab, MLflow y el conector Snowflake se ejecutan desde la nueva ruta.
- Un kernel Jupyter real usa el intérprete nuevo, importa src/pipeline.py y ajusta/predice con datos exclusivamente sintéticos. Notebook de comprobación privado en tmp/migracion-kernel.ipynb.
- Los PDF del PSet 1 son legibles y su notebook conserva estructura válida. El código y los notebooks del proyecto no requirieron sustituciones de rutas.
- Los seis servicios están healthy, sus montajes de host existen y los archivos de código/datos montados se leen dentro de los contenedores. Docker Desktop puede mostrar el prefijo interno /host_mnt; se traduce a la ruta del host para verificarlo.
- Los nombres de los volúmenes coinciden antes/después. Kestra conserva su flujo y rechaza acceso sin autenticación. MLflow conserva la misma corrida, el artefacto con su SHA-256 y el modelo sintético recuperable.

La verificación comprueba funcionamiento local después del cambio. No implica reejecutar todo el pipeline, entrenar modelos, generar de nuevo entregables ni consultar/reconstruir Snowflake. El importe de las dependencias Snowflake sí se comprobó sin abrir conexión.

## Uso desde el IDE

Abrir la carpeta nueva `psets` como raíz. Cerrar terminales que estuvieran activadas antes del cambio y abrir otras desde esa carpeta; una terminal ya abierta puede conservar VIRTUAL_ENV/PATH antiguos. Reiniciar kernels que estuvieran ejecutándose. Para PSet 3 seleccionar `pset-03/.venv/bin/python`; para auxiliares PSet 2, `pset-02/.venv/bin/python`; para documentos PSet 1, `.venv/bin/python`. No se ha cambiado la selección global de intérprete del editor.

Si hay accesos directos o recientes del IDE hacia la carpeta anterior, abrir la nueva ruta. Los espacios restantes en «Proyecto CD» y «Documents - MacBook» funcionaron en las comprobaciones actuales; mantener siempre las rutas entre comillas en comandos manuales.
