#!/usr/bin/env zsh
# Cargar desde proyecto_final: source src/demo_video.sh
# Únicamente crea la API de ensayo y sus datos privados; no cambia aliases.

# Una cohorte nueva por prueba. El SQLite queda exclusivamente en DEMO_ROOT.
demo_generar() {
  docker run --rm --mount "type=bind,source=$DEMO_ROOT,target=/app/.local" \
    "$DEMO_IMAGE" python -m src.datos \
    --ejemplo "/app/.local/$1" --cohorte-id "$DEMO_RUN-$1"
}

# Retira únicamente el contenedor que esta sesión identificó como propio.
demo_detener() {
  local marca
  if docker container inspect "$DEMO_CONTAINER" >/dev/null 2>&1; then
    marca=$(docker inspect "$DEMO_CONTAINER" --format '{{index .Config.Labels "oulad.demo"}}')
    if [ "$marca" != "$DEMO_RUN" ]; then
      echo 'Nombre ocupado por otro contenedor; detener y revisar.'
      return 1
    fi
    docker rm -f "$DEMO_CONTAINER"
  fi
}

# Argumento: 0 = modelo; 1 = respaldo. Solo recrea el contenedor aislado.
demo_iniciar() {
  case "$1" in 0|1) ;; *) echo 'Usar 0 o 1'; return 1 ;; esac
  demo_detener || return 1
  docker run -d --name "$DEMO_CONTAINER" --label "oulad.demo=$DEMO_RUN" \
    --network "$DEMO_NETWORK" --memory 1536m -p 127.0.0.1:8010:8000 \
    --mount "type=bind,source=$DEMO_ROOT,target=/app/.local" \
    -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
    -e MLFLOW_HTTP_REQUEST_TIMEOUT=10 -e MLFLOW_HTTP_REQUEST_MAX_RETRIES=0 \
    -e PSET4_MODEL_MODE=mlflow -e PSET4_DB_PATH=/app/.local/operacion.sqlite \
    -e PSET4_CAPACITY=0.10 -e PSET4_WEEK2_SHARE=0.25 \
    -e PSET4_FORCE_FALLBACK="$1" \
    "$DEMO_IMAGE" python /app/.local/servicio.py
}

# Muestra solo los campos necesarios; la respuesta íntegra se guarda.
demo_enviar() {
  local semana
  case "$2" in 14) semana=2 ;; 28) semana=4 ;; *) echo 'Usar corte 14 o 28'; return 1 ;; esac
  curl -fsS -X POST http://127.0.0.1:8010/predecir \
    -H 'Content-Type: application/json' \
    --data-binary "@$DEMO_ROOT/$1/semana$semana.json" \
    -o "$DEMO_ROOT/$1/respuesta-$2.json" || return 1
  python3 - "$DEMO_ROOT/$1/respuesta-$2.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); m=r['modelo']
print(json.dumps({'cohorte':r['cohorte_id'], 'respuestas':len(r['predicciones']),
  'nuevas_propuestas':r['nuevas_propuestas'], 'respaldo':r['respaldo'],
  'modelo':m.get('nombre'), 'version':m.get('version'), 'run_id':m.get('run_id'),
  'puntuacion_individual':m.get('puntuacion_individual')},ensure_ascii=False,indent=2))
print(json.dumps(r['predicciones'][0],ensure_ascii=False,indent=2))
PY
}

# Cambia exclusivamente el alias del nombre técnico de prueba.
demo_alias() {
  case "$1" in 1|2) ;; *) echo 'Usar versión 1 o 2'; return 1 ;; esac
  docker compose exec -T -e DEMO_VERSION="$1" monitoreo python - <<'PY'
import os,mlflow
name='oulad-apoyo-academico-recarga-cd-semana2'
c=mlflow.MlflowClient()
a,b=[c.get_model_version(name,v) for v in ['1','2']]
assert a.run_id==b.run_id=='a6c0b65d4e354ceaabfc565c88bfa0c2'
assert a.source==b.source, 'Los artefactos de prueba deben coincidir'
real=['oulad-apoyo-academico-semana2-modelo','oulad-apoyo-academico-semana4-modelo']
antes={n:str(c.get_model_version_by_alias(n,'champion').version) for n in real}
assert set(antes.values())=={'1'}, 'Revisar el estado operativo antes de grabar'
v=os.environ['DEMO_VERSION']; assert v in {'1','2'}
c.set_registered_model_alias(name,'champion',v)
assert antes=={n:str(c.get_model_version_by_alias(n,'champion').version) for n in real}
print({'nombre_tecnico':name,'version':v,'modelos_operativos_sin_cambios':antes})
PY
}

_demo_preparar() {
  local sesion estado intento
  if [ ! -f docker-compose.yml ] || [ ! -f tests/fixtures/referencia.json ]; then
    echo 'Ejecutar desde proyecto_final: source src/demo_video.sh'; return 1
  fi
  docker info >/dev/null 2>&1 || { echo 'Abrir Docker Desktop antes de continuar.'; return 1; }
  mkdir -p .local/demo-video
  sesion="$PWD/.local/demo-video/sesion.env"
  if [ -f "$sesion" ]; then
    source "$sesion"
    case "$DEMO_ROOT" in "$PWD"/.local/demo-video/video-*) ;; *) echo 'Ruta de sesión incompatible'; return 1 ;; esac
    case "$DEMO_CONTAINER" in pset4-video-*) ;; *) echo 'Contenedor de sesión incompatible'; return 1 ;; esac
  else
    DEMO_RUN="video-$(TZ=America/Guayaquil date +%Y%m%d-%H%M%S)"
    DEMO_ROOT="$PWD/.local/demo-video/$DEMO_RUN"
    DEMO_CONTAINER="pset4-$DEMO_RUN"
  fi
  DEMO_IMAGE=$(docker inspect "$(docker compose ps -q api)" --format '{{.Image}}') || return 1
  DEMO_NETWORK=$(docker inspect "$(docker compose ps -q mlflow)" --format '{{json .NetworkSettings.Networks}}' | python3 -c 'import json,sys; n=json.load(sys.stdin); assert len(n)==1; print(next(iter(n)))') || return 1
  mkdir -p "$DEMO_ROOT"
  # Verificación de lectura: el arranque no modifica ningún alias.
  docker compose exec -T monitoreo python - <<'PYCODE'
import mlflow
c=mlflow.MlflowClient(); name='oulad-apoyo-academico-recarga-cd-semana2'
a,b=[c.get_model_version(name,v) for v in ['1','2']]
assert a.run_id==b.run_id=='a6c0b65d4e354ceaabfc565c88bfa0c2' and a.source==b.source
for n in ['oulad-apoyo-academico-semana2-modelo','oulad-apoyo-academico-semana4-modelo']:
    assert str(c.get_model_version_by_alias(n,'champion').version)=='1', 'Revisar estado operativo'
print('Registry verificado; modelos operativos en versión 1; aliases sin cambios.')
PYCODE
  if [ "$?" -ne 0 ]; then echo 'Revisar Registry antes de iniciar la API de ensayo.'; return 1; fi
python3 - "$DEMO_ROOT" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1])
r=json.loads(Path('tests/fixtures/referencia.json').read_text())
r['modelos']['14']['nombre']='oulad-apoyo-academico-recarga-cd-semana2'
(p/'referencia.json').write_text(json.dumps(r))
(p/'servicio.py').write_text("""from pathlib import Path
import json,os,uvicorn
from api.main import crear_app,ProveedorModelos
p=Path('/app/.local')
r=json.loads((p/'referencia.json').read_text())
provider=ProveedorModelos(r,modo='mlflow',forzar_respaldo=os.environ.get('PSET4_FORCE_FALLBACK','0')=='1')
app=crear_app(ruta_db=p/'operacion.sqlite',proveedor=provider)
uvicorn.run(app,host='0.0.0.0',port=8000)
""")
PY

  if [ "$?" -ne 0 ]; then return 1; fi
  python3 - "$sesion" "$DEMO_RUN" "$DEMO_ROOT" "$DEMO_CONTAINER" <<'PYCODE'
from pathlib import Path
import shlex,sys
names=['DEMO_RUN','DEMO_ROOT','DEMO_CONTAINER']
Path(sys.argv[1]).write_text(''.join(n+'='+shlex.quote(v)+'\n' for n,v in zip(names,sys.argv[2:])))
PYCODE
  if [ "$?" -ne 0 ]; then return 1; fi
  for estado in normal version1 version2 rollback respaldo reactivado; do
    if [ ! -f "$DEMO_ROOT/$estado/cohorte.json" ]; then demo_generar "$estado" || return 1; fi
  done
  estado=$(docker inspect "$DEMO_CONTAINER" --format '{{.State.Running}}' 2>/dev/null)
  if [ "$estado" != true ]; then demo_iniciar 0 || return 1; fi
  for intento in {1..30}; do
    if curl --max-time 3 -fsS http://127.0.0.1:8010/salud 2>/dev/null | python3 -c 'import json,sys; assert json.load(sys.stdin)["modelo_cargado"]' 2>/dev/null; then
      if [ ! -f "$DEMO_ROOT/contenedor-inicial.txt" ]; then docker inspect "$DEMO_CONTAINER" --format '{{.Id}} {{.Image}}' > "$DEMO_ROOT/contenedor-inicial.txt"; fi
      echo 'API de ensayo disponible: http://localhost:8010/docs'
      echo "Sesión: $DEMO_RUN. Funciones demo_enviar, demo_alias, demo_iniciar y demo_detener cargadas."
      return 0
    fi
    sleep 2
  done
  echo "No se confirmó la carga normal; revisar: docker logs --tail 40 $DEMO_CONTAINER"
  return 1
}

_demo_preparar
