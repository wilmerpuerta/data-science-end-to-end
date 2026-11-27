# Guía para grabar la demo del proyecto final

El video mostrará el servicio desplegado en Docker, una ingesta nueva y las evidencias del monitoreo y la decisión humana. La duración objetivo es **6:35**, con límite de **7:00**. Conviene grabar por escenas y unirlas después: el tiempo de preparación y la ejecución completa de la ingesta no tienen que caber en siete minutos.

Esta es una demostración local del despliegue con datos históricos OULAD. Los ejemplos de llamadas HTTP usan matrículas sintéticas, la misma imagen de la API y un almacenamiento separado. No representan atención real a estudiantes.

El [guion de narración](guion_video.md) contiene el texto de cada escena. Esta guía añade la secuencia de preparación, comandos y resultados que debes comprobar. Los comandos que aparecen aquí se ejecutan cuando prepares la grabación; no se han iniciado servicios ni alterado aliases al redactar esta guía.

**Grabación final publicada:** [ver demo](https://drive.google.com/file/d/11P7KdS9zWTNWfUkhNJrOdMeW7uvE2NG6/view?usp=sharing), 6:52,34. Acceso por enlace verificado el 27-nov-2026. Las instrucciones siguientes sirven para reproducir la grabación.

## 1 Preparar OBS y una prueba de veinte segundos

1. Abrir [OBS Studio](https://obsproject.com/) y ejecutar el asistente de configuración para grabación.
2. En el menú de OBS, abrir **Review App Permissions / Revisar permisos de la aplicación** y habilitar pantalla y micrófono. Accesibilidad permite usar atajos con otra ventana activa. Cámara solo hace falta si decides mostrarte. [Permisos oficiales](https://obsproject.com/kb/macos-permissions-guide).
3. Crear una escena llamada `Demo PSet4`. En **Fuentes → +**, añadir **Captura de pantalla de macOS** y elegir la pantalla de trabajo. Permite capturar navegador y Terminal al alternar ventanas. [Captura en macOS](https://obsproject.com/kb/macos-screen-capture-source).
4. En **Ajustes → Audio**, seleccionar el micrófono y verificar que se mueve su medidor al hablar. Evitar que el mismo micrófono aparezca dos veces. Para esta demo basta tu voz; no necesitas reproducir audio del sistema. [Inicio de OBS](https://obsproject.com/kb/quick-start-guide).
5. Como configuración inicial para el ensayo, usar **1920 × 1080 y 30 fps**. Aumentar el tamaño de letra de Terminal a unos 18–20 puntos y el navegador a 125–150 %, sin ocultar los datos importantes. Si el Mac pierde fluidez con Docker abierto, ajustar en la prueba antes de grabar las escenas finales.
6. Guardar las grabaciones fuera del repositorio, por ejemplo en `Películas/PSet4_demo`. Usar **MKV** para la captura y convertir después mediante **Archivo → Remux Recordings / Convertir grabaciones** a MP4 para editar o entregar. [Guía de grabación de OBS](https://obsproject.com/kb/standard-recording-output-guide).
7. Grabar veinte segundos cambiando entre navegador y Terminal, hablando y moviendo el cursor. Detener, reproducir y confirmar tres cosas: voz comprensible, texto legible y ambas ventanas visibles. Minimizar OBS durante la captura evita mostrar su vista repetida.

Activar No molestar, cerrar correo y mensajería, y autenticar Kestra antes de empezar. No abrir `.env`, claves, conexiones cloud ni pantallas con contraseñas durante la grabación.

## 2 Levantar el proyecto antes de grabar

Abrir Docker Desktop y esperar a que esté disponible. En una Terminal, entrar a la carpeta real:

```sh
cd "/Users/wilmer.puerta/Documents/Documents - MacBook/MCD-USFQ/MSDS_6003_CD_Erick_Naunay/Proyecto CD/psets/proyecto_final"
docker info >/dev/null
docker compose config --quiet
docker compose up -d --no-build --pull never --wait
docker compose ps
```

El comando reutiliza las imágenes preparadas y conserva volúmenes e historial. **Resultado esperado:** nueve servicios iniciados y saludables. Si faltan imágenes, configuración o acceso cloud, resolverlo con el [README](../README.md) antes de grabar. No usar `docker compose down -v` para resolverlo: los volúmenes contienen evidencia.

Abrir estas pestañas en el navegador y dejarlas ordenadas:

| Pestaña | Dirección | Qué se mostrará |
|---|---|---|
| Kestra | <http://localhost:8094> | Ingesta nueva e historial de pausa/rechazo. |
| MLflow propio | <http://localhost:5004> | Modelos, versión y run. |
| API operativa | <http://localhost:8004/docs> | Servicio desplegado y modelos activos. |
| Tablero | <http://localhost:8504> | Monitoreo, alertas y negocio por escenario. |
| API de demostración | <http://localhost:8010/docs> | Solicitudes y cambios aislados; se prepara en el paso 3. |
| GitHub Actions | <https://github.com/wilmerpuerta/data-science-end-to-end/actions> | Una ejecución efectivamente aprobada y su commit. |

Comprobar los modelos operativos:

```sh
curl -fsS 'http://127.0.0.1:8004/modelo?corte_dias=14' | python3 -m json.tool
curl -fsS 'http://127.0.0.1:8004/modelo?corte_dias=28' | python3 -m json.tool
curl -fsS http://127.0.0.1:8004/salud | python3 -m json.tool
```

Esperar `modelo_cargado: true`, `respaldo: false` en los modelos y versión `1` en ambos cortes. El puerto 5001 corresponde al servicio histórico: para esta demo usar el Registry propio en 5004. Si el estado difiere, revisar la causa; no modificar los modelos para que la pantalla coincida con el guion.

## 3 Preparar las herramientas de la demo

El puerto 8010 corresponde a un contenedor adicional: `docker compose up` levanta los nueve servicios del proyecto, pero no crea por sí solo esta API de ensayo. Desde `proyecto_final/`, ejecutar:

```sh
source src/demo_video.sh
```

El comando verifica el Registry sin modificar aliases, recupera o crea una sesión local, prepara las cohortes sintéticas e inicia la API con la imagen del servicio operativo. Espera la carga y muestra `API de ensayo disponible: http://localhost:8010/docs`.

Comprobar antes de grabar:

```sh
curl -fsS http://127.0.0.1:8010/salud | python3 -m json.tool
curl -fsS 'http://127.0.0.1:8010/modelo?corte_dias=14' | python3 -m json.tool
```

Se espera `modelo_cargado: true`, nombre técnico `oulad-apoyo-academico-recarga-cd-semana2`, versión `1` y `respaldo: false`. Semana 4 consulta el modelo vigente. El nombre técnico tiene dos versiones con el mismo artefacto; sus cambios posteriores se hacen explícitamente mediante `demo_alias`.

La sesión guarda solicitudes y respuestas en `.local/demo-video/video-<fecha-hora>/`, con SQLite separado. El archivo privado `.local/demo-video/sesion.env` permite retomar sus variables. **Si cierras Terminal, vuelve a entrar a `proyecto_final/` y ejecuta `source src/demo_video.sh`.** Recuperará la sesión y cargará de nuevo `demo_enviar`, `demo_alias`, `demo_iniciar` y `demo_detener`. El script no reinicia un contenedor de ensayo que ya está corriendo.

Continuar en esa misma Terminal con las escenas. No enviar todavía `normal`, `version1`, `version2`, `rollback`, `respaldo` o `reactivado`. Para ensayar sin consumir las solicitudes previstas para la grabación:

```sh
demo_generar ensayo
demo_enviar ensayo 14
```

Si un comando devuelve error, resolverlo antes de continuar. El script verifica la identidad del contenedor antes de retirarlo y no administra los servicios Compose. Si al recuperar una sesión el respaldo estaba activado, sus funciones quedan cargadas; usar `demo_iniciar 0` y esperar el modelo para volver al estado normal.

## 4 Preparar y grabar la ingesta nueva

Esta escena escribe la auditoría de carga y reconstruye dbt/Spark en Snowflake. Comprobar que no esté ejecutándose la ingesta histórica de `pset_2/` ni otra carga manual sobre las mismas tablas.

1. Abrir Kestra → **Flows / Flujos** → namespace `pset4.oulad` → flujo `ingesta`.
2. Iniciar la grabación de esta escena en OBS.
3. Pulsar **Execute / Ejecutar** e indicar `source_file=all` y `force_reload=false`.
4. Mostrar el identificador nuevo de ejecución y seguir las tareas `raw`, `dbt`, `spark` y `verificar` hasta el resultado final.
5. Abrir los logs de dbt y Spark/verificación y dejar visibles los conteos relevantes.
6. Detener OBS. Anotar el ID nuevo junto al archivo grabado, por ejemplo en una nota dentro de `DEMO_ROOT`.

**Debe verse:** SUCCESS, 23 modelos y 168 pruebas dbt, OBT de 108.277 filas × 35 columnas y conciliación de los cuatro cortes. Raw puede informar NOOP porque los archivos coinciden con los ya cargados; explicarlo como prevención de recargas duplicadas. La ejecución `2sQlV9Hreu3bWXWi7MtYRE` es la referencia histórica, no el ID de esta nueva grabación.

Conservar la captura completa. En edición acelerar solo las esperas, con rótulo `Espera acelerada ×8` o la velocidad realmente utilizada. Mantener legibles el ID, los estados y los resultados. Si aparece un error, conservar la evidencia y resolverlo antes de preparar la versión final del video.

## 5 Grabar las nueve escenas

La ingesta se graba por separado porque su duración depende del entorno. Las demás escenas pueden grabarse en secuencia o en clips. Antes de cada clip, dejar abierta la ventana correcta, iniciar OBS, esperar dos segundos y comenzar la explicación. Escribir o pegar los comandos preparados sin narrar cada carácter.

| Escena | Tiempo final | Acción principal |
|---|---|---|
| 01 | 00:00–00:30 | Infraestructura y servicio desplegado. |
| 02 | 00:30–01:25 | Ingesta nueva y controles. |
| 03 | 01:25–02:15 | Solicitud válida, reenvío y 422. |
| 04 | 02:15–02:50 | Deriva y alerta. |
| 05 | 02:50–03:50 | Entrenamiento histórico, pausa real y rechazo. |
| 06 | 03:50–04:40 | Versión técnica 1 → 2 → 1 sin recrear servicio. |
| 07 | 04:40–05:20 | Respaldo y reactivación en API aislada. |
| 08 | 05:20–06:05 | Negocio, errores y acceso. |
| 09 | 06:05–06:35 | Trazabilidad, limitación y siguiente decisión. |

### Escena 01 Infraestructura

Mostrar `docker compose ps`, los nueve servicios y una consulta a `/salud` del puerto 8004. Pasar brevemente por Kestra, MLflow y el tablero. La API adicional del puerto 8010 es de demostración y no cuenta como uno de los nueve servicios Compose.

Decir: «El servicio prioriza apoyo académico en semanas dos y cuatro. Los nueve componentes están desplegados juntos. La API propone contactos según una capacidad limitada; la coordinación confirma la atención».

### Escena 02 Ingesta

Insertar la grabación del paso 4. Explicar la secuencia originales → Raw → dbt → Spark → OBT y los conteos verificados. Usar la narración del guion mientras se muestran resultados a velocidad normal; acelerar solo los tramos de espera.

### Escena 03 Solicitud y errores

Mostrar en pantalla el rótulo `API aislada · cohorte sintética · misma imagen desplegada`. Ejecutar:

```sh
demo_enviar normal 14
```

**Debe verse:** 40 respuestas, una propuesta nueva, versión `1` y `respaldo: false`.

Comprobar que reenviar conserva exactamente la respuesta:

```sh
curl -fsS -X POST http://127.0.0.1:8010/predecir \
  -H 'Content-Type: application/json' \
  --data-binary "@$DEMO_ROOT/normal/semana2.json" \
  -o "$DEMO_ROOT/normal/repetida.json"
python3 - "$DEMO_ROOT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])/'normal'
assert json.loads((p/'respuesta-14.json').read_text())==json.loads((p/'repetida.json').read_text())
print('Respuesta idéntica: mismos IDs, versión y propuestas; sin consumir cupos adicionales.')
PY
```

Preparar y enviar una solicitud incompleta:

```sh
python3 - "$DEMO_ROOT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);r=json.loads((p/'normal/semana2.json').read_text())
del r['matriculas'][0]['features']['studied_credits']
(p/'invalida.json').write_text(json.dumps(r))
PY
curl -sS -o "$DEMO_ROOT/error-422.json" -w 'HTTP %{http_code}\n' \
  -X POST http://127.0.0.1:8010/predecir -H 'Content-Type: application/json' \
  --data-binary "@$DEMO_ROOT/invalida.json"
python3 -m json.tool "$DEMO_ROOT/error-422.json"
```

**Debe verse:** HTTP 422 y `studied_credits` como campo faltante. No se asignan nuevos cupos por esa llamada.

Para mostrar la segunda ronda, si cabe en los cincuenta segundos:

```sh
demo_enviar normal 28
```

**Debe verse:** tres propuestas nuevas, cuatro en total entre ambas rondas. Si no cabe, conservarlo en el ensayo y explicar el reparto en la narración. No decir que la semana 4 añade cuatro cupos nuevos.

### Escena 04 Deriva

1. Abrir el tablero y elegir `oulad-2014j-deriva-v1` en **Escenario**.
2. Mostrar **Capacidad de focalización**, con la caída de L06/L07.
3. Mostrar **Cambios en los datos** y luego **Alertas y versiones**.
4. Identificar una alerta con umbral, ventana, destinatario y acción. Expandir **Disponibilidad de resultados y diagnóstico** durante el ensayo para distinguir revisiones sin etiquetas de revisiones maduras.

Decir: «La prueba alteró artificialmente las entradas de L06 y L07. El monitoreo detecta cambios y pérdida de desempeño. Una alerta de datos exige revisión; el candidato se solicita por deterioro persistente con resultados finales disponibles».

No sumar control y escenario alterado. Los controles también presentan alertas.

### Escena 05 Pausa y rechazo reales

En Kestra buscar la ejecución `6lcaE9ak8kGv4myx06ZMMw` del flujo `reentrenamiento`. Mostrar el historial de la tarea `aprobacion`, incluyendo PAUSED, su reanudación y el estado final SUCCESS. Usar los inputs/outputs que registran la decisión; no pulsar Reanudar, Reiniciar o Ejecutar de nuevo.

Como apoyo legible, mostrar esta consulta al CSV:

```sh
python3 - <<'PY'
import csv
with open('docs/reentrenamientos.csv') as f:
    for r in csv.DictReader(f):
        print(r['evento'], '| estado:',r['estado'], '| decisión:',r['decision'],
              '| vigente:',r['tp_champion'], '| candidato:',r['tp_challenger'])
PY
```

Explicar: «El candidato usó etiquetas ya disponibles y excluyó las personas de L08. Con 147 cupos detectó 81 Fail frente a 77 del vigente. Solo añadió cuatro; la regla exigía al menos siete. La pausa permitió revisión humana, se rechazó el reemplazo y la versión uno continuó activa».

Si no aparece la pausa en la vista principal, abrir el historial de la tarea; SUCCESS es el estado final del flujo, no significa que el candidato haya sido aprobado.

### Escena 06 Recarga y rollback técnicos

El nombre técnico tiene dos versiones de los mismos pesos. La prueba demuestra que la API sigue el alias, no una ganancia predictiva. En esta escena no ejecutar `demo_iniciar`: el contenedor debe permanecer igual.

```sh
demo_alias 1
demo_enviar version1 14
demo_alias 2
demo_enviar version2 14
demo_alias 1
demo_enviar rollback 14
```

**Debe verse:** versiones `1`, `2`, `1` en las tres respuestas nuevas. Las probabilidades pueden ser iguales porque se usa el mismo artefacto. Comprobar el contenedor:

```sh
docker inspect "$DEMO_CONTAINER" --format '{{.Id}} {{.Image}}' > "$DEMO_ROOT/contenedor-final.txt"
diff "$DEMO_ROOT/contenedor-inicial.txt" "$DEMO_ROOT/contenedor-final.txt" \
  && echo 'Mismo contenedor e imagen durante 1 → 2 → 1.'
```

El `diff` no debe mostrar diferencias. El cambio de alias solo afecta al nombre técnico; los modelos operativos siguen en versión 1. No usar un lote antiguo para demostrar cambio de versión: una respuesta guardada conserva su versión original.

### Escena 07 Interruptor

Ahora sí se recrea el contenedor de demostración, porque el interruptor se lee al iniciar. Ejecutar:

```sh
demo_iniciar 1
```

Esperar a que responda y consultar el modelo:

```sh
curl -fsS 'http://127.0.0.1:8010/modelo?corte_dias=14' | python3 -m json.tool
demo_enviar respaldo 14
demo_enviar respaldo 28
```

**Debe verse:** `respaldo: true`, `puntuacion_individual: false` y cupos 1+3. `/salud` puede indicar `estado: respaldo` y `modelo_cargado: false`: es lo esperado mientras el interruptor está activo. El score constante del Dummy no estima riesgo individual.

Para comprobar también 422 bajo respaldo, repetir la llamada inválida de la escena 03. Debe continuar rechazándola.

Reactivar y enviar una cohorte nueva:

```sh
demo_iniciar 0
```

Esperar la carga del modelo y ejecutar:

```sh
demo_enviar reactivado 14
```

**Debe verse:** `respaldo: false` y puntuación individual. Una respuesta histórica de respaldo conserva sus flags aunque ahora el modelo esté activo. En el video se pueden acelerar los arranques, identificando esa espera; no afirmar que el interruptor cambió sin reiniciar el proceso.

### Escena 08 Negocio y acceso

1. Volver al tablero y seleccionar **`oulad-2014j-control-v1`**.
2. Mostrar **Valor de negocio frente al estático**: 420 frente a 314, con los mismos 920 cupos; 106 matrículas netas adicionales y +33,76 % relativo.
3. Mostrar la tabla por lote. Las filas de semana 4 ya incluyen propuestas de semana 2: no sumar ambas.
4. Abrir la página 10 del memo para la brecha de acceso de L06: −8,20 puntos de cobertura para discapacidad declarada.
5. Mostrar la página 12 solo si cabe: el adelanto hipotético del 30 % permite 274 cupos y deja 646 futuros. Es un escenario presupuestario, no ahorro observado.

Decir: «Mejora la detección con igual capacidad, pero no se ha medido el efecto de las tutorías. Hay falsas alertas y una brecha de acceso que exige revisión. La ampliación del presupuesto necesita una evaluación institucional».

### Escena 09 Trazabilidad y cierre

Mostrar los campos relevantes de una predicción, sin imprimir el JSON completo de las cuarenta matrículas:

```sh
python3 - "$DEMO_ROOT/normal/respuesta-14.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));m=r['modelo']
print(json.dumps({'modelo':m.get('nombre'),'version':m.get('version'),
 'run_id':m.get('run_id'),'snapshot_id':m.get('snapshot_id'),
 'split_id':m.get('split_id'),'politica_id':r['politica_id'],
 'id_prediccion':r['predicciones'][0]['id_prediccion']},indent=2))
PY
```

En MLflow, localizar el run correspondiente y su procedencia; los registros históricos de `docs/predicciones.csv` conservan además Gold. Mostrar una ejecución aprobada real de GitHub Actions con su commit visible. No asociarla a otro commit ni presentar una revisión documental como un despliegue comprobado.

Cerrar: «Cada predicción conserva su modelo, versión, run y procedencia. Cambiar el modelo requiere una decisión humana. 2014J ya se había consultado: los resultados son retrospectivos. El siguiente paso es un piloto con cohortes nuevas, revisión de acceso y medición de costos e impacto».

## 6 Terminar la sesión técnica

Después de capturar las escenas:

```sh
demo_alias 1
demo_detener
curl -fsS 'http://127.0.0.1:8004/modelo?corte_dias=14' | python3 -m json.tool
curl -fsS 'http://127.0.0.1:8004/modelo?corte_dias=28' | python3 -m json.tool
```

Ambos modelos operativos deben seguir en `1`, sin respaldo forzado. Conservar `DEMO_ROOT`: contiene solicitudes, respuestas y las dos comprobaciones del contenedor. Es evidencia local excluida de Git. No borrar los volúmenes ni el historial de Kestra para limpiar la grabación.

## 7 Editar y exportar

1. Convertir los MKV a MP4 desde OBS y conservar los originales.
2. Importar los clips en el editor y ordenarlos según la tabla de nueve escenas. En iMovie se puede ajustar la velocidad desde el control de velocidad del clip. [Instrucciones de Apple](https://support.apple.com/en-ae/guide/imovie/mov6c442b2eb/mac).
3. Acelerar los tramos de espera de ingesta/arranque. Añadir el rótulo con la velocidad real. Mantener la voz a velocidad normal; puedes narrar los resultados después sobre el clip editado.
4. Mantener rótulos breves donde correspondan: `Cohorte sintética`, `Historial real de pausa y rechazo`, `Recarga con pesos idénticos` y `Presupuesto hipotético`.
5. Revisar el video completo: texto y números legibles, audio sin eco, solicitudes con sus respuestas, pausa histórica identificada, rechazo explícito, secuencia 1→2→1 y respaldo/reactivación visibles.
6. Exportar como `PSet4_demo_Puerta_Wilmer.mp4`, preferentemente en 1080p. La duración debe ser como máximo 7:00; apuntar a 6:35 deja margen. Guardar el archivo fuera del repositorio.
7. Subirlo al medio de entrega o alojamiento elegido y comprobar el enlace en una ventana privada o con otra cuenta sin tus permisos de propietario. La configuración debe permitir acceso al profesor.
8. Incorporar la URL real al memo y su fuente editable. Hasta contar con ese enlace, conservar el pendiente de publicación. El video no necesita guardarse como binario dentro de GitHub.

## 8 Resolver problemas durante el ensayo

| Problema | Acción |
|---|---|
| Docker no conecta | Abrir Docker Desktop y esperar; comprobar `docker info`. |
| Kestra no muestra ejecuciones anteriores | Revisar que usas puerto 8094 y los volúmenes del proyecto. No crear una pausa ficticia ni borrar el historial. |
| API 8010 no responde tras iniciar | Esperar y consultar logs del contenedor aislado. Si 8010 está ocupado por otro servicio, revisar su origen antes de retirarlo. |
| API responde en respaldo sin haberlo solicitado | Revisar conexión con MLflow y el nombre técnico. No grabarlo como inferencia normal. |
| Error 404 de cohorte | Generar esa cohorte con `demo_generar` en la misma sesión/directorio del contenedor. |
| Error 409 al enviar semana 4 | Completar semana 2 de esa misma cohorte; no cambiar su contenido ni su política. |
| Al cambiar alias aparece la versión anterior | Usar una cohorte nueva para la predicción. Las respuestas antiguas deben conservar su versión. |
| Tablero no muestra 420/314 | Elegir el control original y revisar los agregados privados de negocio según README; no completar números manualmente. |
| El video supera siete minutos | Recortar navegación repetida y acelerar esperas señaladas; conservar las demostraciones y resultados exigidos. |

La revisión de esta guía es de comandos, código y coherencia con el proyecto. El ensayo en vivo debe confirmar la disponibilidad de Docker, las imágenes, el Registry, Kestra y Snowflake en el momento de grabar.


## 9 Encontrar una ejecución nueva en GitHub Actions

Encender Docker o consultar Swagger no dispara GitHub Actions. Los workflows se ejecutan por eventos de GitHub: CI admite push, pull request y ejecución manual; CD se publica por push a `main` después de las pruebas.

Abrir **Actions → proyecto-final-ci** y localizar el commit que se está mostrando. Para la ejecución manual, usar **Run workflow** y seleccionar **main**, cuando el botón esté disponible. Si la interfaz no muestra el botón por estar consultando la rama predeterminada histórica `master`, revisar el workflow de `main`; el disparo por API sobre `main` permite comprobar esa revisión sin sobrescribir `master`.

En una corrida, abrir el job `api` y los pasos de pruebas e imagen. Esperar **Success** antes de presentarlo como aprobado. Los pasos sin desplegar muestran logs de CI; las peticiones locales de la demo quedan en el contenedor aislado y no aparecen en los logs de GitHub. El commit, la corrida y la imagen publicada deben identificarse por separado.
