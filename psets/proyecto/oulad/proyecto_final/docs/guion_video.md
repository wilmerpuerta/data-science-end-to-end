# Guion de video - PSet 04

Duración objetivo: **6:35 minutos**, con 25 segundos de margen hasta el máximo de 7:00. Idioma: español. El archivo es un guion; el video y su enlace todavía no están publicados.

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

**Narración:** Cada predicción conserva su versión, run, snapshot, política y fuente Gold; el código se publica después de aprobar las pruebas. La decisión de cambiar el modelo permanece separada y humana. Recomiendo ajustar y validar en un piloto supervisado: revisar acceso, acordar capacidad y medir aceptación, costos e impacto antes de escalar. Los documentos y el repositorio contienen la evidencia y las limitaciones.

## Comandos para infraestructura y consulta

```sh
docker compose up -d --no-build --pull never --wait
docker compose ps
# Solo consultas; no cambian aliases ni consumen cupos.
curl -s http://127.0.0.1:8004/salud
curl -s "http://127.0.0.1:8004/modelo?corte_dias=14"
```

## API aislada: preparación y llamadas

El montaje siguiente queda en `.local/demo-video/api`, sin Snowflake. El contenedor nuevo usa los mismos modelos por alias, pero un SQLite separado. Si ya existe un contenedor con ese nombre, revisar su origen antes de retirarlo; estos comandos no administran los servicios Compose.

```sh
DEMO_IMAGE=$(python3 -c 'from pathlib import Path; print(next(l.split("=",1)[1] for l in Path(".env").read_text().splitlines() if l.startswith("PSET4_API_IMAGE=")))')
DEMO_ROOT="$PWD/.local/demo-video/api"
mkdir -p "$DEMO_ROOT"
docker run --rm --mount "type=bind,source=$DEMO_ROOT,target=/app/.local" \
  "$DEMO_IMAGE" python -m src.datos --ejemplo /app/.local/normal \
  --cohorte-id video-normal
docker run -d --name pset4-video-api --network proyecto-final_default \
  --memory 1536m -p 127.0.0.1:8010:8000 \
  --mount "type=bind,source=$DEMO_ROOT,target=/app/.local" \
  -e MLFLOW_TRACKING_URI=http://mlflow:5000 -e PSET4_MODEL_MODE=mlflow \
  -e PSET4_DB_PATH=/app/.local/operacion.sqlite "$DEMO_IMAGE"
# Esperar modelo_cargado=true.
curl -s http://127.0.0.1:8010/salud
curl -s -X POST http://127.0.0.1:8010/predecir \
  -H "Content-Type: application/json" \
  --data-binary @.local/demo-video/api/normal/semana2.json > .local/demo-video/valida.json
python3 - <<'PYCODE'
from pathlib import Path
import json
p=Path(".local/demo-video/api/normal/semana2.json")
v=json.loads(p.read_text());del v["matriculas"][0]["features"]["studied_credits"]
Path(".local/demo-video/invalida.json").write_text(json.dumps(v))
r=json.loads(Path(".local/demo-video/valida.json").read_text())
print({k:r[k] for k in ["respaldo","nuevas_propuestas"]})
print(r["predicciones"][0])
PYCODE
curl -s -o .local/demo-video/422.json -w "%{http_code}\n" \
  -X POST http://127.0.0.1:8010/predecir -H "Content-Type: application/json" \
  --data-binary @.local/demo-video/invalida.json
```

Reenviar el mismo archivo válido devuelve su respuesta guardada. Para enseñar semana 4, usar el archivo `normal/semana4.json`; deben verse tres propuestas nuevas, no cuatro nuevas. El ejemplo completo usado para el memo está en `docs/ejemplo_api.json` y distingue IDs sintéticos de valores de features de desarrollo.

## Recarga y rollback mecánicos sin promover el candidato

El Registry verificado contiene `oulad-apoyo-academico-recarga-cd-semana2`, versiones 1 y 2 con el mismo run/artefacto, creado para esta prueba en la etapa CD. Comprobar antes que ambas versiones siguen apuntando al run `a6c0b65d4e354ceaabfc565c88bfa0c2`. **Si falta ese nombre o sus pesos difieren, detener el ensayo y revisar; no usar un modelo operativo como sustituto.**

Preparar una referencia y un servidor aislados:

```sh
python3 - <<'PYCODE'
from pathlib import Path
import json
p=Path(".local/demo-video/api")
r=json.loads(Path("tests/fixtures/referencia.json").read_text())
r["modelos"]["14"]["nombre"]="oulad-apoyo-academico-recarga-cd-semana2"
(p/"referencia.json").write_text(json.dumps(r))
(p/"servicio.py").write_text("from pathlib import Path\nimport json,os,uvicorn\nfrom api.main import crear_app,ProveedorModelos\np=Path('/app/.local')\nr=json.loads((p/'referencia.json').read_text())\napp=crear_app(ruta_db=p/'operacion.sqlite',proveedor=ProveedorModelos(r,modo='mlflow',forzar_respaldo=os.environ.get('PSET4_FORCE_FALLBACK','0')=='1'))\nuvicorn.run(app,host='0.0.0.0',port=8000)\n")
PYCODE
# Retira exclusivamente el contenedor aislado que acabamos de crear.
docker rm -f pset4-video-api
docker run -d --name pset4-video-api --network proyecto-final_default \
  --memory 1536m -p 127.0.0.1:8010:8000 \
  --mount "type=bind,source=$DEMO_ROOT,target=/app/.local" \
  -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
  "$DEMO_IMAGE" python /app/.local/servicio.py
```

Cambiar solo el alias técnico con este comando, usando sucesivamente `1`, `2` y `1` en `v`. No editar el nombre constante. Consultar `/modelo?corte_dias=14` después de cada cambio y enviar una cohorte nueva generada con `--ejemplo` y nombres `video-v1`, `video-v2`, `video-rollback` (como en la preparación normal). No reutilizar un lote guardado para pretender que cambió su versión.

```sh
docker compose exec -T monitoreo python - <<'PYCODE'
import mlflow
name="oulad-apoyo-academico-recarga-cd-semana2"
v="1"  # Secuencia de la grabación: 1, después 2, finalmente 1.
assert v in {"1","2"}
c=mlflow.MlflowClient()
versions=[c.get_model_version(name,n) for n in ["1","2"]]
assert all(m.run_id=="a6c0b65d4e354ceaabfc565c88bfa0c2" for m in versions)
c.set_registered_model_alias(name,"champion",v)
print({"modelo_aislado":name,"version":v})
PYCODE
curl -s "http://127.0.0.1:8010/modelo?corte_dias=14"
docker inspect pset4-video-api --format '{{.Id}} {{.Image}}'
```

Registrar el ID e imagen antes y después: deben ser iguales. Restaurar siempre el alias técnico a `1` al terminar. Los aliases `oulad-apoyo-academico-semana2-modelo` y `oulad-apoyo-academico-semana4-modelo` permanecen en 1. La prueba histórica validada produjo 120 predicciones; los pesos iguales explican que las probabilidades no cambien. No llamar a `--reentrenar rollback` sobre el ciclo rechazado: exige una promoción humana previa y no corresponde a este caso.

## Interruptor en la API aislada

Preparar una cohorte nueva `video-respaldo` con `--ejemplo /app/.local/respaldo`. Recrear solo `pset4-video-api` con los mismos argumentos del servidor aislado y añadir `-e PSET4_FORCE_FALLBACK=1`. Esperar su inicio y enviar la cohorte nueva. Deben verse `respaldo=true`, `puntuacion_individual=false`, cola administrativa y cupos 1+3. El mensaje aclara que el score constante no es riesgo individual. Repetir el lote normal demuestra que no se reescribe su respuesta.

Recrear la API aislada con `PSET4_FORCE_FALLBACK=0` y enviar una tercera cohorte nueva para mostrar reactivación. La recreación es necesaria porque el proceso lee el interruptor al iniciar; no afirmar que basta con editar un archivo. Al acabar: `docker rm -f pset4-video-api`. No aplicar el interruptor ni borrar SQLite en los servicios operativos.

## Pausa, rechazo y trazabilidad sin reabrir el ciclo

Abrir en Kestra la ejecución `6lcaE9ak8kGv4myx06ZMMw`. Mostrar el historial de estados de `aprobacion` con PAUSED y su reanudación, no solo la etiqueta SUCCESS final. Complementar con `docs/reentrenamientos.csv`: cuatro eventos y `decision=rechazar`, responsable Wilmer Puerta, motivo +4 frente a +7 requeridos. No volver a reanudar la ejecución ni inventar una aprobación.

La demo diferencia dos evidencias: ciclo real con rechazo y recarga/rollback mecánico en otro nombre con pesos idénticos. El candidato no cumple la regla y no se fuerza un cambio operativo para completar el video. No hay un período posterior con un candidato promovido.

## Cierre y publicación

Revisar que la grabación final dure como máximo 7:00, que los números y los textos sean legibles y que no aparezcan secretos. Mantener los rótulos «espera acelerada», «cohorte sintética», «prueba de recarga con pesos idénticos» y «escenario presupuestario» cuando corresponda. No simular una ejecución o una pausa que no ocurrió.

Publicar el video en una ubicación accesible al profesor, comprobar el enlace con un usuario sin permisos del autor e insertar la URL real en el memo y su fuente. Hasta entonces el documento conserva el texto «pendiente de publicación». El video no sustituye los notebooks finales Restart/Run All.
