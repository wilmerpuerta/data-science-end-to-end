# Preparar la configuración privada de ingesta

Estado: configuración privada preparada por el autor según configuracion-cloud.json. Después se comprobó conexión desde Kestra y se cargó Raw. Este documento conserva el procedimiento de configuración; ver [ingesta-raw.md](ingesta-raw.md) para resultados y comandos actuales.

## Crear la configuración local

Desde la raíz, en la terminal de VS Code:

```bash
pset-02/.venv/bin/python pset-02/scripts/configurar_cloud.py
```

Introducir el identificador de cuenta que funcionó, la ruta de la privada (Enter para la predeterminada) y su frase de cifrado oculta. El asistente utiliza los mismos parámetros de conexión que probar_conexion.py y valida PSET2_SVC, PSET2_PIPELINE, PSET2_OULAD, RAW y PSET2_WH mediante funciones de contexto. No hace cargas ni modifica tablas.

Para permitir ejecución sin prompts, guarda **cuenta y frase de cifrado** en `~/.config/psets/snowflake/pset2-connection.json`, fuera del repositorio, con permisos 0600. Es un archivo privado local que contiene la frase; no es una segunda capa de cifrado. La privada rsa_key.p8 sigue cifrada y no se copia. Mantener acceso restringido al equipo y a la carpeta. No compartir archivos, capturas o selecciones del editor que contengan esos valores.

El archivo pset-02/.env.cloud contiene solamente las rutas locales del JSON y de la privada, sin el identificador ni la frase. También se excluye de Git. Los futuros servicios montarán ambos archivos como solo lectura; no se incrustarán secretos en YAML, parámetros de flujo ni código. El asistente no aplica montajes por sí solo; el Compose cloud posterior los utiliza para el ejecutor Kestra.

El script no lee ni reemplaza configuraciones existentes. Si indica que ya existe una, detenerse y revisarla localmente antes de cambiarla. Si el JSON llegó a crearse pero no .env.cloud, conserva el archivo y comunica solo ese mensaje para resolverlo sin exponer su contenido.

Resultado esperado:

```text
Configuración privada preparada y conexión comprobada.
```

docs/configuracion-cloud.json se genera únicamente al finalizar correctamente y registra fecha, estado y alcance, sin valores privados. El asistente se comprobó con dobles de conexión antes de que el autor lo ejecutara en su terminal. La conexión posterior desde Kestra utiliza los archivos privados montados, sin imprimir ni copiar sus contenidos a documentación.

## Continuación

Con esa configuración se comprobó el acceso desde Kestra y se cargó Raw conservando linaje, checksum y run_id. La [verificación Raw](ingesta-raw-verificacion.json) separa esas ejecuciones de la prueba inicial del host. Bronze dbt se ejecutó posteriormente según [calidad-bronze.md](calidad-bronze.md); Silver también se ejecutó según [silver.md](silver.md); Gold también se ejecutó según [gold.md](gold.md); Spark/OBT ya se ejecutó: [guía](obt-spark.md) y [resultados](obt-resultados.md).
