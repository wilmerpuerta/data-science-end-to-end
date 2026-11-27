# Guion de video - PSet 04

Duración objetivo: **6:35 minutos**, con 25 segundos de margen hasta el máximo de 7:00. Idioma: español. La grabación final dura **6:52,34** y está [publicada en Google Drive](https://drive.google.com/file/d/11P7KdS9zWTNWfUkhNJrOdMeW7uvE2NG6/view?usp=sharing); el enlace figura en el memo. La escaleta original conserva su objetivo de 6:35.

La [guía detallada de grabación](guia_grabacion_demo.md) contiene preparación de OBS, comandos por escena, resultados esperados y solución de problemas.

## Preparación antes de grabar

Usar `proyecto_final/`. Dejar descargadas las imágenes, construidos los ejecutores y disponibles las pestañas de Kestra (8094), MLflow (5004), API (8004), tablero (8504) y GitHub Actions. No mostrar `.env`, claves, archivos privados ni cabeceras de autenticación. No usar `docker compose down -v`.

Grabar una ejecución nueva de `pset4.oulad/ingesta`, `source_file=all`, `force_reload=false`, sin escritores históricos simultáneos. Conservar la grabación íntegra. En la edición acelerar solo esperas, con rótulo de velocidad, y mantener visibles ID, estados, 168 pruebas y OBT. La ejecución histórica validada sirve para ensayar y comparar, no para simular una nueva ejecución.

No ejecutar de nuevo reentrenamiento para obtener un resultado distinto ni reanudar una ejecución terminada. La pausa histórica y el rechazo son evidencia válida del control humano. El cambio 1-2-1 se demuestra aparte con el nombre técnico aislado; no cambia el candidato rechazado.

## Escaleta y narración

### 00:00-00:30 | Infraestructura

**En pantalla:** Terminal: ejecutar Compose; mostrar los nueve servicios healthy. Abrir las pestañas preparadas de Kestra, MLflow, Swagger y tablero.

**Narración:** Este proyecto prioriza apoyo académico durante el período, con datos históricos OULAD. El Compose levanta juntos la orquestación, las capas de datos, el Registry, la API y el tablero. Aquí se observan los nueve servicios saludables. Los cupos son experimentales y las propuestas se confirman con revisión humana; esta demostración no representa tutorías ya realizadas.

### 00:30-01:25 | Ingesta hasta OBT

**En pantalla:** Insertar la grabación completa de una ejecución nueva de ingesta con esperas aceleradas y rótulo x8. Conservar ID, cuatro tareas finales y resultados dbt/Spark. Referencia validada: 2sQlV9Hreu3bWXWi7MtYRE.

**Narración:** Kestra verifica los cinco originales y su manifest, conserva Raw y ejecuta Bronze, Silver y Gold mediante dbt. Se aprobaron veintitrés modelos y ciento sesenta y ocho pruebas. Spark produce ciento ocho mil doscientas setenta y siete filas con treinta y cinco columnas. Comprueba las claves y la lectura de vuelta, y prueba que alterar actividad futura no cambia las features tempranas. Los cuatro hashes coinciden con el PSet dos. Las esperas están aceleradas; el ID y el historial completo permanecen disponibles.

### 01:25-02:15 | Solicitud válida e inválida

**En pantalla:** Servicio aislado en 8010: enviar semana2 y consultar respuesta resumida; enviar JSON con studied_credits omitido y mostrar 422. Enseñar registro de la misma respuesta al repetir.

**Narración:** Esta solicitud contiene cuarenta matrículas de una cohorte sintética completa. La API carga el modelo de semana dos desde el Registry y devuelve riesgo, decisión, versión y run. Reserva una propuesta inicial; la semana cuatro puede añadir tres bajo el mismo presupuesto. Si falta studied credits, devuelve cuatrocientos veintidós antes de asignar cupos. Reenviar la solicitud válida conserva sus identificadores y su versión. Estos ejemplos están en otro SQLite y no se cargan a las tablas de negocio.

### 02:15-02:50 | Deriva y alerta

**En pantalla:** Tablero: seleccionar escenario sintético, mostrar L06/L07 y alerta; abrir el CSV de alertas o logs Kestra, con ventana y destinatario.

**Narración:** En el escenario sintético se alteraron L seis y L siete: se permutaron vectores completos dentro de la edición y se añadieron ciento veinte créditos, conservando resultados, IDs y cupos. El monitor registra el cambio y la pérdida de detección. Los controles también pueden alertar, por lo que no atribuimos todo aviso a la inducción. Solo cuando llegan etiquetas maduras se evalúa desempeño; un cambio de entradas por sí solo no promueve ni reentrena.

### 02:50-03:50 | Reentrenamiento y pausa humana

**En pantalla:** Kestra: ejecución histórica 6lcaE9ak8kGv4myx06ZMMw. Mostrar historial PAUSED de aprobacion y sus inputs de reanudación, luego comparación y rechazo final. No reanudar ni entrenar otra vez.

**Narración:** La caída persistente de L siete maduro inició el ciclo real. Se entrenó con datos ya etiquetados, la misma preparación y los hiperparámetros congelados. La reserva L ocho quedó fuera por persona. La tarea de aprobación se detuvo realmente en pausa, como muestra el historial. Con ciento cuarenta y siete cupos, el candidato obtuvo ochenta y un Fail frente a setenta y siete del modelo vigente. La regla exigía al menos siete adicionales y solo añadió cuatro. Wilmer Puerta confirmó el rechazo, se registró el motivo y el modelo operativo permaneció en versión uno.

### 03:50-04:40 | Cambio de versión y rollback aislado

**En pantalla:** API aislada con referencia de prueba: mostrar versión 1, cambiar solo el alias del nombre técnico a 2, enviar cohorte nueva; volver a 1 y enviar otra. Mantener contenedor/imagen.

**Narración:** Para demostrar la recarga y el rollback sin forzar una promoción, uso un nombre técnico aislado con dos versiones de los mismos pesos. La API observa uno, luego dos, y vuelve a uno sin reconstruir la imagen ni cambiar el contenedor. Los lotes previos conservan su versión. Esto prueba la mecánica, no una mejora predictiva del duplicado. El candidato real sigue rechazado y los aliases operativos no se modifican.

### 04:40-05:20 | Interruptor de respaldo

**En pantalla:** Preparar cohorte nueva de respaldo. Recrear solo el contenedor aislado con PSET4_FORCE_FALLBACK=1; mostrar flags y propuesta. Volver a 0 al terminar.

**Narración:** Al habilitar el interruptor, una cohorte nueva recibe una cola administrativa para revisión. La respuesta indica respaldo y que no existe puntuación individual. El cero técnico del Dummy no significa riesgo cero. La validación y los cupos siguen vigentes; una entrada inválida continúa siendo rechazada. Al reactivar el modelo se sirven lotes nuevos normalmente y se conservan las respuestas históricas. Solo recreé el servicio de prueba.

### 05:20-06:05 | Negocio y acceso

**En pantalla:** Tablero o presentación: 420/314 a 920; tabla por lote con L07/L08; grupo discapacidad L06 y escenario presupuestario.

**Narración:** Con los mismos novecientos veinte cupos, el longitudinal prioriza cuatrocientos veinte Fail frente a trescientos catorce del estático: ciento seis casos netos, una mejora relativa del treinta y tres coma setenta y seis por ciento. Son matrículas y no reprobaciones evitadas. La mejora global no elimina riesgos: en L seis existe una brecha de acceso de ocho coma veinte puntos para discapacidad declarada. El adelanto del treinta por ciento es un escenario que dejaría seiscientos cuarenta y seis cupos futuros, no un ahorro demostrado.

### 06:05-06:35 | Trazabilidad y recomendación

**En pantalla:** Mostrar run/version/snapshot/Gold en un registro y concluir. Pestaña GitHub Actions Success e imagen publicada preparada.

**Narración:** Cada predicción conserva modelo, versión, run, snapshot y fuente Gold. El código se publica tras superar las pruebas; cambiar un modelo requiere una decisión humana. 2014J ya se había consultado: los resultados son retrospectivos. Recomiendo un piloto con cohortes nuevas, revisión de acceso y medición de aceptación, costos e impacto antes de escalar.

## Comandos para infraestructura y consulta

```sh
docker compose up -d --no-build --pull never --wait
docker compose ps
# Solo consultas; no cambian aliases ni consumen cupos.
curl -s http://127.0.0.1:8004/salud
curl -s "http://127.0.0.1:8004/modelo?corte_dias=14"
```

## API aislada y sesión de ensayo

Desde `proyecto_final/`, ejecutar `source src/demo_video.sh`. El script recupera la sesión privada e inicia el puerto 8010 si hace falta. Al abrir otra Terminal, volver a cargarlo antes de usar las funciones. Los nueve servicios Compose no incluyen este contenedor adicional.

La [guía de grabación](guia_grabacion_demo.md) contiene los comandos por escena: `demo_enviar normal 14`, solicitud inválida 422, `demo_alias 1`, `demo_alias 2`, regreso a `1`, respaldo con `demo_iniciar 1` y reactivación con `demo_iniciar 0`. Todos los ejemplos se guardan en el SQLite de la sesión, sin carga a Snowflake.

El nombre técnico de recarga conserva dos versiones con los mismos pesos. Una cohorte nueva por versión permite observar 1→2→1 sin recrear el contenedor durante esa escena. La escena del interruptor sí recrea exclusivamente la API de ensayo. No ejecutar rollback sobre el ciclo rechazado ni modificar aliases operativos. Al terminar, restaurar el alias técnico a `1` y ejecutar `demo_detener`.

## Pausa, rechazo y trazabilidad sin reabrir el ciclo

Abrir en Kestra la ejecución `6lcaE9ak8kGv4myx06ZMMw`. Mostrar el historial de estados de `aprobacion` con PAUSED y su reanudación, no solo la etiqueta SUCCESS final. Complementar con `docs/reentrenamientos.csv`: cuatro eventos y `decision=rechazar`, responsable Wilmer Puerta, motivo +4 frente a +7 requeridos. No volver a reanudar la ejecución ni inventar una aprobación.

La demo diferencia dos evidencias: ciclo real con rechazo y recarga/rollback mecánico en otro nombre con pesos idénticos. El candidato no cumple la regla y no se fuerza un cambio operativo para completar el video. No hay un período posterior con un candidato promovido.

## Cierre y publicación

Revisar que la grabación final dure como máximo 7:00, que los números y los textos sean legibles y que no aparezcan secretos. Mantener los rótulos «espera acelerada», «cohorte sintética», «prueba de recarga con pesos idénticos» y «escenario presupuestario» cuando corresponda. No simular una ejecución o una pausa que no ocurrió.

El video final está publicado en el enlace indicado al inicio y en el memo. Se verificó el acceso sin autenticación el 27-nov-2026. La grabación dura 6:52,34; los siete notebooks conservan sus salidas de ejecución completa. Para una nueva edición, comprobar otra vez duración, permisos y coherencia del enlace antes de sustituir la entrega.
