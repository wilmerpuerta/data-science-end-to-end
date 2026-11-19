# Revisión del paquete antes de publicar

La revisión cubre el repositorio completo, con sus entregables PSet 1 y PSet 2. El [informe verificable](paquete-verificacion.json) registra comprobaciones, huellas y alcance. No crea commits, remotos, publicaciones ni recursos cloud. La elección del destino GitHub queda pendiente de las consultas del autor.

## Repetir la revisión

Desde la raíz, con Docker Desktop iniciado y la configuración privada local ya preparada:

```bash
.venv/bin/python pset-02/scripts/verificar_paquete.py --entregables --infra
```

El entorno .venv debe tener instaladas las dependencias de [PSet 1](../../pset-01/scripts/requirements.txt), que incluyen las necesarias para verificar ambos documentos. En otra máquina se prepara así:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r pset-01/scripts/requirements.txt
```

Sin --infra se omite la consulta a Docker y los servicios. Sin --entregables se omite relanzar los verificadores de documentos; el informe indica qué comprobaciones se ejecutaron. La instalación requiere red; una vez preparado el entorno, la revisión no descarga dependencias ni conecta con Snowflake.

## Qué se comprobó

- PSet 1: 69 comprobaciones de correspondencia Markdown, notebook, PDF, PowerPoint, enlaces y originales OULAD.
- PSet 2: 31 comprobaciones de fuente Markdown y memo de seis páginas, cifras frente a JSON, diagramas y resúmenes generados.
- Todos los candidatos que Git incluiría: archivos privados y CSV originales excluidos, ausencia de enlaces simbólicos, tamaños, JSON válidos, sintaxis Python y enlaces Markdown locales.
- Contenido candidato: patrones de claves privadas, tokens conocidos, JWT, URLs con autenticación, destinos de cuenta y rutas personales. PDF y PPTX se inspeccionan mediante texto; para PPT se revisan cadenas legibles y las comprobaciones existentes de PowerPoint.
- Reglas de exclusión probadas contra rutas de .env, claves, entornos, logs privados, temporales y datos crudos. Los valores privados no se imprimen ni se leen para compararlos.
- dbt: 23 modelos, referencias literales resueltas a modelos/fuentes y grafo sin ciclos. Docker: bases por digest, instalación Python con hashes y contextos de construcción con lista de archivos permitidos.
- Código de carga y transformación comparado con la instantánea de reproducción limpia: sin cambios en los archivos de ejecución contrastados. La documentación y herramientas de cierre posteriores se identifican por separado.
- Compose validado y cinco servicios saludables mediante consultas locales. No se volvió a cargar Raw, reconstruir Gold ni ejecutar Spark cloud durante esta revisión.

El único ejemplo de ruta personal detectado pertenece a la instrucción «Nunca codifiques» del prompt original. Es una prohibición con puntos suspensivos, no una ruta de entrada ni material de autenticación. Se conserva el encargo intacto y se clasifica explícitamente esa excepción en el informe.

Los detectores de patrones no garantizan identificar cualquier secreto posible. Al no existir todavía commits ni remotos en esta revisión inicial, no hay historial publicado que inspeccionar. Cualquier cambio posterior requiere repetir la revisión sobre los archivos concretos antes de publicar; si se añaden commits, también se debe revisar su historial.

## Correcciones y límites que permanecen

Se añadió al README un recorrido único desde una copia nueva, con preparación del cliente Python, autenticación, construcción de imágenes y ejecución integral. Se actualizaron las menciones antiguas a permisos de transformación aún pendientes: Raw, dbt y Spark sí los comprobaron. El timeout del warehouse sigue sin evidencia específica.

La cadena se reprodujo desde una exportación limpia con recursos Snowflake existentes, no desde una cuenta vacía ni un clon remoto. Calendarios desactivados, backfill por fichero, escritor único coordinado, cobertura y exactitud externa desconocidas, costo monetario sin cuantificar y sincronización Colab de PSet 1 pendiente permanecen documentados. No se presenta un modelo predictivo entrenado ni impacto educativo medido.

El informe de esta revisión y el inventario general se excluyen de package_sha256 para evitar una referencia circular. Este campo identifica el contenido de los demás candidatos inspeccionados. Con --entregables, el inventario general se actualiza después de cerrar el informe, conservando su checksum vigente. No certifica futuras modificaciones ni el resultado de un despliegue en GitHub.
