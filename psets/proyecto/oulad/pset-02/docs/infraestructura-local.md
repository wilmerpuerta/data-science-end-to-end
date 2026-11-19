# Infraestructura local: arranque y comprobación

Estado: Compose implementado y probado el 12-nov-2026 en Docker Desktop x86_64. PostgreSQL, Kestra y Spark saludables; dbt Core instalado en una imagen construida con dependencias fijadas. Esta guía conserva la infraestructura inicial. Raw se cargó posteriormente usando el [Compose cloud y su guía](ingesta-raw.md); Bronze se ejecutó después según [calidad-bronze.md](calidad-bronze.md); Silver ya está construido según [silver.md](silver.md); Gold también está construido según [gold.md](gold.md); Spark/OBT ya se ejecutó: [guía](obt-spark.md) y [resultados](obt-resultados.md). Ver infraestructura-verificacion.json.

## 1. Requisitos y preparación

Docker Desktop debe estar iniciado con Compose disponible. Python 3 ejecuta los comandos auxiliares sin dependencias adicionales. Entorno probado: motor con 4 CPU y aproximadamente 7,8 GiB. Los límites de contenedor suman 512 MiB para PostgreSQL, 2304 MiB para Kestra y 2304 MiB para Spark; dbt tiene un límite de 1536 MiB y solo se inicia para comandos puntuales. Son límites de diseño, no memoria medida ni mínimos universales. Ejecutar los trabajos por etapas.

Los cinco originales y manifest.json deben estar en datasets/ en la raíz. Los montajes resuelven ../datasets desde pset-02 y son de solo lectura. OULAD_DATA_DIR permite otra carpeta que contenga esos archivos y un manifiesto coherente. El modo --local-only no monta claves; la extensión cloud posterior monta configuración y clave en Kestra como solo lectura. Ver ingesta-raw.md.

Todos los comandos siguientes se ejecutaron desde la raíz. infra.py calcula las rutas desde su ubicación, sin depender del directorio de trabajo accidental.

```bash
python3 pset-02/scripts/infra.py prepare
python3 pset-02/scripts/infra.py validate
python3 pset-02/scripts/infra.py pull
python3 pset-02/scripts/infra.py build
python3 pset-02/scripts/infra.py up
python3 pset-02/scripts/infra.py status
```

prepare crea .env.infra con contraseñas aleatorias locales y permisos 0600; si ya existe lo conserva sin leerlo ni sobrescribirlo. El archivo está excluido de Git y no contiene credenciales Snowflake. Mantenerlo junto a los volúmenes del proyecto: generar otro password no cambia el que ya inicializó PostgreSQL. Si se pierde, recuperar la configuración privada antes de reiniciar volúmenes existentes.

validate ejecuta docker compose config --quiet: no imprime secretos interpolados. pull descarga los servicios externos y build construye la imagen dbt. up espera salud hasta 240 segundos. status muestra solo servicio, estado y salud, sin etiquetas, rutas ni entorno privado.

build usa docker build con contexto relativo, en lugar de Compose/Bake: la prueba de Compose build en este Mac encontró una diferencia de normalización Unicode en la ruta del proyecto y solicitó una autorización de archivos incompatible con esa ruta. El comando Docker directo construyó correctamente el mismo Dockerfile/contexto y evita esa diferencia de rutas sin cambiar permisos ni desactivar verificaciones.

## 2. Acceder a Kestra

Abrir http://localhost:8080. Usuario local: admin@psets.local. Consultar únicamente en el editor local el campo PSET2_KESTRA_PASSWORD de pset-02/.env.infra para entrar; no copiarlo a documentación, commits ni chat. La API rechaza peticiones sin autenticación, comprobado con respuesta 401. La gestión de salud utiliza 8081. Ambos puertos están ligados a 127.0.0.1; PostgreSQL y Spark no publican puertos al host.

No se montó el socket Docker. El Compose cloud posterior añade un ejecutor Process y credenciales montadas en solo lectura para la ingesta Raw. Las capas dbt y OBT todavía no forman un flujo end-to-end completo.

## 3. Ejecutar una prueba real de Kestra

```bash
python3 pset-02/scripts/comprobar_kestra.py --seed
python3 pset-02/scripts/comprobar_kestra.py --execute --check-auth
```

seed crea el flujo pset2.local/infra_smoke si falta, desde kestra/infra_smoke.yml. execute lanza ese flujo y espera SUCCESS. Su única tarea es un log interno, sin mensajes externos ni acceso cloud. check-auth verifica 401 sin credenciales y acceso correcto con las credenciales locales. El auxiliar lee .env.infra internamente y no imprime su contenido.

Prueba de persistencia ejecutada: stop, up y comprobación del flujo sin seed. El flujo siguió disponible después del reinicio de PostgreSQL y Kestra; la definición y metadatos se conservan en el volumen PostgreSQL, mientras Kestra conserva su almacenamiento en otro volumen.

## 4. Ejecutar Spark

```bash
python3 pset-02/scripts/infra.py spark-test
```

Se ejecuta spark-submit --master 'local[2]' --driver-memory 1g dentro del contenedor. smoke_test.py verifica que datasets sea de solo lectura, recalcula cinco SHA-256, comprueba suma 0…9 = 45 y cuenta 32.593 filas de studentInfo.csv. No escribe datos ni se conecta a Snowflake. En comandos de shell directos, citar 'local[2]' para evitar expansión de corchetes en zsh.

El servicio Spark mantiene un contenedor ejecutor disponible mediante sleep infinity; cada trabajo arranca su propio driver local y termina. No representa un clúster Spark master/worker. Es suficiente para esta infraestructura batch local; la construcción de OBT se añadirá como otro trabajo spark-submit.

## 5. Ejecutar el cliente dbt

```bash
python3 pset-02/scripts/infra.py dbt-version
```

Este comando inicia un contenedor puntual y lo elimina al terminar. Se comprobó Core 1.10.13 y adaptador Snowflake 1.10.2. La imagen usa Python 3.11.13 y 75 dependencias resueltas para Linux con hashes verificados al instalar. El conector Snowflake de esa resolución es 3.18.1, distinto del cliente de diagnóstico local 4.7.4; son entornos aislados. El aviso de versiones más recientes no significa que se haya actualizado ni probado otra combinación.

dbt-version acredita instalación. El proyecto, perfil cloud y Bronze se añadieron y comprobaron posteriormente: consultar [calidad-bronze.md](calidad-bronze.md) para parse, debug, build-bronze, test-bronze y exportación de métricas. No hay paquetes dbt externos que descargar. Silver también se ejecutó; consultar [silver.md](silver.md). Gold también se ejecutó; consultar [gold.md](gold.md).

## 6. Detener y volver a levantar

```bash
python3 pset-02/scripts/infra.py stop
python3 pset-02/scripts/infra.py up
```

stop detiene los servicios conservando contenedores y volúmenes. down elimina contenedores y red, conservando también volúmenes; no pasa -v. No se incluye una operación de borrado de volúmenes. La prueba inicial dejó tres servicios saludables. La composición cloud actual añade dbt-runner y spark-runner: cinco servicios saludables, sin puertos adicionales publicados.

Las imágenes externas están fijadas por versión y digest linux/amd64 en docker-compose.yml. La imagen propia dbt se reproduce con Dockerfile base fijado y requirements.txt con hashes; no está publicada en un registro remoto. El alcance probado es x86_64. En ARM se necesitará emulación o una resolución de imágenes y dependencias validada para esa arquitectura.

## Evidencia y siguientes pasos

infraestructura-verificacion.json registra las comprobaciones locales y sus límites. La conexión Snowflake del host y la del ejecutor Kestra ya funcionan; los cinco CSV se cargaron a Raw y se verificó idempotencia. Ver ingesta-raw.md e ingesta-raw-verificacion.json. Bronze y Silver también se ejecutaron con sus tests; Gold también está ejecutado; Spark/OBT también está ejecutado; la orquestación completa ya está verificada; la reproducción desde exportación limpia también está verificada; el memo técnico ya está generado según [guía](memo-tecnico.md); queda la revisión final.

Referencias de implementación: Compose del tag Kestra v1.0.0 (https://raw.githubusercontent.com/kestra-io/kestra/v1.0.0/docker-compose.yml), registro oficial Docker para PostgreSQL y Spark, y paquetes dbt-core/dbt-snowflake en PyPI. Se adaptó la configuración al proyecto y se comprobaron los servicios; no se copiaron contraseñas de ejemplos oficiales.
