# Estado y evidencia de ejecución

Actualizado el 13-nov-2026. Se distingue comprobación local de resultados comunicados por el autor desde Snowflake. La prueba inicial del host la ejecutó el autor; después se ejecutó desde Kestra la conexión y carga cloud con configuración privada montada, sin imprimirla.

| Comprobación | Estado | Evidencia y límite |
|---|---|---|
| Docker y Compose disponibles | Verificado localmente | diagnostico-local.json, motor accesible |
| Cinco CSV originales | Verificado localmente | Coinciden con bytes y SHA-256 del manifiesto |
| Base PSET2_OULAD y cinco esquemas | Confirmado mediante resultado aportado por el autor | SHOW SCHEMAS muestra ANALYTICS, BRONZE, GOLD, RAW y SILVER dentro de PSET2_OULAD, propietario SYSADMIN |
| Contexto de esquema RAW | Confirmado en el resultado aportado | is_current=Y para RAW; no acredita por sí solo el rol activo |
| Rol activo PSET2_PIPELINE | Confirmado por captura del autor | CURRENT_ROLE() devuelve PSET2_PIPELINE; no prueba todos los grants de ejecución |
| Warehouse: existencia, estado y tamaño | Confirmado por captura del autor | PSET2_WH, SUSPENDED, STANDARD, X-Small |
| Suspensión y reanudación automáticas | Confirmadas por captura del autor | auto_suspend=60 y auto_resume=true; is_current=N indica que no está seleccionado como warehouse actual de la sesión |
| Timeout del warehouse | Pendiente de evidencia específica | Timeout=600 aún no se muestra en las capturas recibidas; los permisos de ejecución sí se comprobaron después con Raw, dbt y Spark |
| Generación de claves | Confirmada por el autor | Archivos generados localmente según confirmación; no se leyeron claves ni frase de cifrado desde el agente |
| Asignación de rol al usuario de servicio | Confirmada mediante resultado aportado por el autor | SHOW GRANTS muestra PSET2_PIPELINE asignado a PSET2_SVC por SECURITYADMIN; no prueba autenticación con la clave |
| Autenticación externa | Confirmada por ejecución del autor e informe local | conexion-snowflake.json: status=ok, conector 4.7.4, 12-nov-2026 21:30:28 UTC; expected_session_context_verified=true. Usuario PSET2_SVC, rol PSET2_PIPELINE y contexto esperados; no acredita cargas ni ejecución de dbt/Spark |
| Cliente Python de diagnóstico | Instalado y comprobado localmente | CPython 3.11.16, conector 4.7.4, dependencias fijadas; importación real y tres comprobaciones aisladas sin red ni claves reales |
| Preparación de autenticación | Implementada localmente | scripts/preparar_claves.py y guía autenticacion-local.md; usuario SERVICE dedicado, sin alterar claves personales |
| Infraestructura local | Implementada y comprobada | docker-compose.yml: PostgreSQL, Kestra y Spark saludables; flujo Kestra SUCCESS, persistencia tras stop/up y API autenticada |
| Interfaz Kestra | Acceso confirmado por el autor | Ingreso a la interfaz local comprobado por el usuario |
| Configuración privada para ingesta | Preparada por el autor | configuracion-cloud.json status=ok; cuenta/frase fuera del repositorio, .env.cloud solo rutas locales |
| Conexión cloud desde Kestra | Comprobada | Ejecución 6Se60WiFEd3vbAndnh6E0J SUCCESS; contexto esperado verificado desde contenedor |
| Spark local | Trabajo real comprobado | Spark 3.5.6/Java 17, suma de rango y 32.593 matrículas; cinco checksums y montaje de solo lectura verificados |
| dbt Core en Docker | Instalación comprobada | Core 1.10.13/adaptador Snowflake 1.10.2; conexión real, cinco vistas Bronze y perfil agregado; 45 tests aprobados |
| Raw con Kestra | Implementado y comprobado | Cinco fuentes, 10.726.852 filas; reconciliación, cinco NOOP, retry controlado y backfill courses.csv |
| Calendario Raw | Configurado, desactivado | Días 1 y 15, 09:00 America/Guayaquil; disparo periódico no probado ni activado |
| Bronze/Staging y calidad | Implementados y comprobados | dbt-build-bronze.json y calidad-bronze.json; cinco vistas, una tabla agregada, 45 tests aprobados |
| Silver y consolidación | Implementados y comprobados | Siete tablas; 8.459.320 claves diarias, 39.605.099 clics; 101 tests Bronze/Silver aprobados en dos builds y 27 métricas idénticas. Ver dbt-build-silver.json, calidad-silver.json y repeticion-silver.json |
| Gold dimensional | Implementado y comprobado | Cinco dimensiones, dos hechos, retiro/resultados separados y perfil de calidad; 168 tests Bronze/Silver/Gold aprobados en dos builds y 26 métricas idénticas; población por corte coincide con PSet 1. Ver dbt-build-gold.json, calidad-gold.json y repeticion-gold.json |
| Spark cloud y OBT | Implementados y comprobados | OBT_FEATURES: 108.277 filas, 35 columnas; siete casos sintéticos y cuatro perturbaciones reales; lectura completa de vuelta igual. Dos runs con cuatro huellas de contenido idénticas. Ver spark-conexion.json, obt-verificacion.json y repeticion-obt.json |
| Orquestación integral | Implementada y comprobada | oulad_pipeline SUCCESS; Raw → dbt → Spark → verificación. Fallo permanente detiene downstream, retry transitorio recuperado e API rechaza comandos libres; ver pipeline-resultados.md |
| Reproducción limpia | Verificada | Exportación de 214 archivos, volúmenes y contraseñas nuevos, imágenes propias sin cache; cinco CSV LOADED, 168 tests y OBT idéntica. Ver reproduccion-limpia.json |
| Memo técnico | Generado | [PDF de seis páginas](../output/pdf/PSet2_memo_Puerta_Wilmer.pdf), [fuente](../memo-pset2.md) e [informe de coherencia](memo-verificacion.json) |
| Revisión del paquete | Documentada | [Comprobaciones previas a publicación](revision-paquete.md) e [informe](paquete-verificacion.json) |
| Cierre del pipeline | Pendiente | Costo monetario sin cuantificar y decisión de publicación GitHub |

Comandos y límites: [infraestructura-local.md](infraestructura-local.md). Evidencia: [infraestructura-verificacion.json](infraestructura-verificacion.json). Los cinco servicios cloud se dejaron saludables: PostgreSQL, Kestra, Spark, dbt-runner y spark-runner. Los clientes dbt/Spark se ejecutan como trabajos puntuales dentro de sus ejecutores.

PUBLIC e INFORMATION_SCHEMA aparecen además como esquemas estándar; no sustituyen las cinco capas del proyecto. No se almacenan nombres de usuario, claves ni credenciales como evidencia.

Incidencia de aprovisionamiento: la asignación original mediante SET con CURRENT_USER() produjo `assignment from non-constant source expression`. Se sustituyó por variables locales de Snowflake Scripting en 01_aprovisionar.sql. El resultado posterior confirma que los esquemas existen; no se infiere de él que todas las demás verificaciones estén completas.

Incidencia de conexión resuelta: el primer intento (21:27:58 UTC) devolvió 290404/08001, equivalente a HTTP 404 en el conector instalado. Al corregir el identificador de cuenta introducido en la terminal, la siguiente prueba (21:30:28 UTC) terminó correctamente. El usuario del cliente se mantuvo fijo en PSET2_SVC. No fue necesario cambiar claves ni grants. Se conserva la causa y la solución sin guardar identificadores privados ni mensajes completos del conector.

Carga y evidencias: [ingesta-raw.md](ingesta-raw.md) y [verificación Raw](ingesta-raw-verificacion.json). Backfill por fichero completo, no por módulo–edición. Retry probado con fallo inyectado antes de conectar, no con una caída real del proveedor. Las pruebas usaron el warehouse sin cuantificar costo monetario.
