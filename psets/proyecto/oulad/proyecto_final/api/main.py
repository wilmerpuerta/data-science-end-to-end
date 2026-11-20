"""API de inferencia batch con priorización y registro transaccional.

Los manifiestos y las asignaciones previas deben proceder del almacenamiento
confiable del servicio, nunca de un cliente que pueda inventar su propia cuota.
"""
from fractions import Fraction
import json
from .esquemas import Candidato, PoliticaCupos, CORTES_PERMITIDOS, UNIDAD_CUPO, priorizar_cohorte, evaluar_meta

# Servicio HTTP: el proveedor y el almacén se pueden sustituir en pruebas.
from contextlib import asynccontextmanager
from pathlib import Path
from threading import RLock
from time import perf_counter
from uuid import NAMESPACE_URL, uuid5
import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from threadpoolctl import threadpool_limits
from .esquemas import SolicitudLote
from src.datos import ROOT, Almacen, ahora, identidad, sha256
from src.pipeline import CATEGORICAS

FIXTURES = ROOT / 'tests/fixtures'


class ProveedorModelos:
    def __init__(self, referencia, modo='mlflow', forzar_respaldo=False):
        self.referencia = referencia
        self.modo = modo
        self.forzar_respaldo = forzar_respaldo
        self.cache = {}
        self.estados = {}
        self.lock = RLock()
        if modo not in {'mlflow', 'fixture', 'sin_modelo'}:
            raise ValueError('Modo de modelo desconocido')
        if referencia['pipeline_sha256'] != sha256(ROOT / 'src/pipeline.py'):
            raise ValueError('La preparación no coincide con la referencia')

    def obtener(self, corte):
        meta = dict(self.referencia['modelos'][str(corte)])
        try:
            if self.forzar_respaldo or self.modo == 'sin_modelo':
                raise RuntimeError('respaldo_solicitado')
            import mlflow
            import mlflow.sklearn
            with self.lock:
                if self.modo == 'mlflow':
                    client = mlflow.MlflowClient(tracking_uri=os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5001'))
                    version = client.get_model_version_by_alias(meta['nombre'], 'champion')
                    run = client.get_run(version.run_id)
                    if (run.data.params.get('cutoff_day') != str(corte)
                            or run.data.params.get('pipeline_sha256') != self.referencia['pipeline_sha256']):
                        raise ValueError('corte_de_modelo_incompatible')
                    meta.pop('ci_ap_fail', None)
                    for campo, nombre_metrica in [('cv_ap_fail_mean', 'ap_fail_mean'), ('cv_ap_fail_std', 'ap_fail_std'), ('cv_coverage_mean', 'coverage_mean'), ('cv_coverage_std', 'coverage_std')]:
                        meta[campo] = run.data.metrics.get(nombre_metrica, run.data.metrics.get(campo))
                    meta.update(version=str(version.version), run_id=version.run_id,
                                snapshot_id=run.data.params.get('snapshot_id', meta['snapshot_id']),
                                split_id=run.data.params.get('split_id', meta['split_id']))
                    uri = f'models:/{meta["nombre"]}/{meta["version"]}'
                    mlflow.set_tracking_uri(client.tracking_uri)
                else:
                    uri = str(FIXTURES / f'semana{corte // 7}')
                    for name, expected in self.referencia['files_sha256'].items():
                        if name.startswith(f'semana{corte // 7}/') and sha256(FIXTURES / name) != expected:
                            raise ValueError('fixture_alterada')
                key = (corte, meta['version'], meta['run_id'])
                if key not in self.cache:
                    self.cache[key] = mlflow.sklearn.load_model(uri)
                model = self.cache[key]
                encoder = model.named_steps['preparacion'].named_transformers_['cat'].named_steps['codificar']
                meta['categorias'] = dict(zip(CATEGORICAS, [[str(x) for x in values if x != '__MISSING__'] for values in encoder.categories_]))
            meta.update(puntuacion_individual=True, criterio_priorizacion='riesgo_fail', respaldo=False, origen=self.modo, uri_solicitada=f'models:/{meta["nombre"]}@champion')
            self.estados[corte] = dict(meta)
            return model, meta
        except Exception as exc:
            baseline = dict(self.referencia['baseline'])
            baseline.update(puntuacion_individual=False, criterio_priorizacion='orden_administrativo_matricula',
                            respaldo=True, origen='baseline_pset3', cutoff_day=corte,
                            categorias=meta['categorias'], error_carga=type(exc).__name__,
                            uri_solicitada=f'models:/{meta["nombre"]}@champion')
            self.estados[corte] = dict(baseline)
            return None, baseline


def crear_app(*, ruta_db=None, modo=None, forzar_respaldo=None, politica=None, proveedor=None):
    referencia = json.loads((FIXTURES / 'referencia.json').read_text())
    modo = modo or os.environ.get('PSET4_MODEL_MODE', 'mlflow')
    if forzar_respaldo is None:
        forzar_respaldo = os.environ.get('PSET4_FORCE_FALLBACK', '0') == '1'
    if politica is None:
        politica = PoliticaCupos(
            version=os.environ.get('PSET4_POLICY_VERSION', 'preventiva-prototipo-0.1'),
            capacidad=Fraction(os.environ.get('PSET4_CAPACITY', '0.10')),
            fraccion_semana2=Fraction(os.environ.get('PSET4_WEEK2_SHARE', '0.25')))
    fuente = proveedor or ProveedorModelos(referencia, modo, forzar_respaldo)
    almacen = Almacen(ruta_db or os.environ.get('PSET4_DB_PATH', str(ROOT / '.local/operacion.sqlite')))
    politica_id = identidad({'version': politica.version, 'capacidad': str(politica.capacidad), 'fraccion_semana2': str(politica.fraccion_semana2)})

    @asynccontextmanager
    async def lifespan(application):
        for cut in CORTES_PERMITIDOS:
            fuente.obtener(cut)
        yield

    application = FastAPI(title='Apoyo académico preventivo', version='0.2.0', lifespan=lifespan)
    application.state.almacen = almacen
    application.state.proveedor = fuente

    @application.exception_handler(RequestValidationError)
    async def entrada_invalida(request, exc):
        # Se conserva campo/tipo/mensaje; valores inválidos como NaN no se serializan.
        errores = [{k: e[k] for k in ['loc', 'msg', 'type']} for e in exc.errors()]
        return JSONResponse(status_code=422, content={'detail': errores})

    @application.middleware('http')
    async def medir(request: Request, call_next):
        if request.url.path != '/predecir':
            return await call_next(request)
        inicio = perf_counter()
        plan = request.headers.get('X-Pset4-Plan')
        lote = request.headers.get('X-Pset4-Lote')
        ejecucion = request.headers.get('X-Pset4-Ejecucion')
        if plan not in ['oulad-2014j-control-v1', 'oulad-2014j-deriva-v1'] or lote not in [f'L{i:02}' for i in range(1,9)]:
            plan = lote = ejecucion = None
        if ejecucion is not None and (len(ejecucion)>128 or not all(c.isalnum() or c in '_-' for c in ejecucion)):
            ejecucion = None
        try:
            response = await call_next(request)
        except Exception:
            almacen.registrar_peticion(500, (perf_counter() - inicio) * 1000, plan, lote, ejecucion)
            raise
        tiempo = (perf_counter() - inicio) * 1000
        almacen.registrar_peticion(response.status_code, tiempo, plan, lote, ejecucion)
        if getattr(request.state, 'nuevo_lote', False):
            with almacen.transaccion() as db:
                db.execute('UPDATE predicciones SET latencia_ms=? WHERE cohorte_id=? AND corte=?',
                           (tiempo, request.state.cohorte, request.state.corte))
        return response

    @application.get('/salud')
    def salud():
        estados = [fuente.estados.get(c, {'respaldo': True}) for c in CORTES_PERMITIDOS]
        cargados = all(not m['respaldo'] for m in estados)
        return {'estado': 'ok' if cargados else 'respaldo', 'modelo_cargado': cargados,
                'respaldo_disponible': True, 'cortes_disponibles': list(CORTES_PERMITIDOS)}

    @application.get('/modelo')
    def modelo(corte_dias: int | None = None):
        if corte_dias is not None and corte_dias not in CORTES_PERMITIDOS:
            raise HTTPException(422, 'corte_dias debe ser 14 o 28')
        cuts = [corte_dias] if corte_dias else CORTES_PERMITIDOS
        return {'modelos': [{k: v for k, v in fuente.obtener(c)[1].items() if k != 'categorias'} for c in cuts]}

    @application.get('/metricas')
    def metricas():
        return almacen.metricas()

    @application.post('/predecir')
    def predecir(lote: SolicitudLote, request: Request):
        started = perf_counter()
        contenido = lote.model_dump(mode='json')
        contenido['matriculas'].sort(key=lambda r: r['matricula'])
        huella = identidad(contenido)
        with almacen.transaccion() as db:
            registered = db.execute('SELECT contenido FROM cohortes WHERE cohorte_id=?', (lote.cohorte_id,)).fetchone()
            if registered is None:
                raise HTTPException(404, 'La cohorte debe registrarse desde una fuente confiable')
            cohorte = json.loads(registered['contenido'])
            previo = db.execute('SELECT huella,respuesta FROM lotes WHERE cohorte_id=? AND corte=?', (lote.cohorte_id, lote.corte_dias)).fetchone()
            if previo:
                if previo['huella'] != huella:
                    raise HTTPException(409, 'El corte ya tiene un lote distinto; no se reasignan sus cupos')
                return json.loads(previo['respuesta'])
            anterior = db.execute('SELECT respuesta FROM lotes WHERE cohorte_id=? AND corte=14', (lote.cohorte_id,)).fetchone()
            historia = json.loads(anterior['respuesta']) if anterior else None
            if historia and historia['politica_id'] != politica_id:
                raise HTTPException(409, 'La cohorte conserva la política con que inició')
            if lote.corte_dias == 28 and politica.fraccion_semana2 > 0 and historia is None:
                raise HTTPException(409, 'Debe completarse primero la ronda de semana 2')
            esperados = cohorte['elegibles'][str(lote.corte_dias)]
            claves = [r.matricula for r in lote.matriculas]
            if len(claves) != len(set(claves)) or set(claves) != set(esperados):
                raise HTTPException(422, 'matriculas: lote incompleto, duplicado o adicional')
            for r in lote.matriculas:
                if esperados[r.matricula] != r.edicion or cohorte['personas'][r.matricula] != r.persona:
                    raise HTTPException(422, 'matriculas: identificadores incompatibles con la cohorte')
            model, meta = fuente.obtener(lote.corte_dias)
            for i, r in enumerate(lote.matriculas):
                for name in CATEGORICAS:
                    value = getattr(r.features, name)
                    if value is not None and value not in meta['categorias'][name]:
                        raise HTTPException(422, [{'loc': ['body', 'matriculas', i, 'features', name], 'msg': 'Categoría no admitida por el modelo', 'type': 'value_error'}])
            x = pd.DataFrame([r.features.model_dump() for r in lote.matriculas])
            for name in x:
                if name in CATEGORICAS:
                    x[name] = x[name].astype(object).where(x[name].notna(), np.nan)
                else:
                    x[name] = x[name].astype(float)
            try:
                if model is None:
                    scores = np.full(len(x), meta['probabilidad_fail'])
                else:
                    with threadpool_limits(limits=2):
                        p = model.predict_proba(x)
                    if p.shape != (len(x), 3) or not np.isfinite(p).all() or (p < 0).any() or (p > 1).any() or not np.allclose(p.sum(axis=1), 1):
                        raise ValueError('probabilidades_invalidas')
                    scores = p[:, list(model.classes_).index('Fail')]
            except Exception as exc:
                meta = {**dict(referencia['baseline']), 'respaldo': True, 'origen': 'baseline_pset3',
                        'cutoff_day': lote.corte_dias, 'error_carga': type(exc).__name__,
                        'puntuacion_individual': False, 'criterio_priorizacion': 'orden_administrativo_matricula'}
                scores = np.full(len(x), meta['probabilidad_fail'])
            seleccionados = {r['matricula']: r['edicion'] for r in historia['predicciones'] if r['consume_cupo_nuevo']} if historia else {}
            candidatos = [Candidato(r.matricula, r.edicion, r.persona, float(score)) for r, score in zip(lote.matriculas, scores)]
            result = priorizar_cohorte(candidatos, cohorte_base=cohorte['base'], elegibles_actuales=esperados,
                                      seleccionados_previos=seleccionados, corte_dias=lote.corte_dias, politica=politica)
            public_meta = {k: v for k, v in meta.items() if k not in {'categorias', 'signature'}}
            result.update(cohorte_id=lote.cohorte_id, politica_id=politica_id, modelo=public_meta,
                          respaldo=meta['respaldo'], modo='experimental', momento=ahora())
            if meta['respaldo']:
                result['mensaje_operativo'] = ('Respaldo activo: el orden administrativo no estima el riesgo individual. '
                                               'Revisar necesidades antes de proponer una tutoría.')
                for row in result['predicciones']:
                    row['accion'] = ('revision_humana_de_respaldo' if row['decision'] != 'seguimiento'
                                     else 'mantener_canal_de_apoyo_sin_estimacion_individual')
            entradas = {r.matricula: r.features.model_dump(mode='json') for r in lote.matriculas}
            for row in result['predicciones']:
                row['id_prediccion'] = uuid5(NAMESPACE_URL, '|'.join([lote.cohorte_id, str(lote.corte_dias), row['matricula'], politica_id, meta['nombre'], str(meta['version']), meta['run_id']])).hex
                row['version_modelo'] = meta['version']
                row['run_id'] = meta['run_id']
                row['respaldo'] = meta['respaldo']
                db.execute('INSERT INTO predicciones VALUES (?,?,?,?,?,?,?,?,?)',
                           (row['id_prediccion'], lote.cohorte_id, lote.corte_dias, row['matricula'], result['momento'],
                            json.dumps(entradas[row['matricula']], allow_nan=False), json.dumps(row), json.dumps(public_meta), (perf_counter() - started) * 1000))
            db.execute('INSERT INTO lotes VALUES (?,?,?,?)', (lote.cohorte_id, lote.corte_dias, huella, json.dumps(result, allow_nan=False)))
        request.state.nuevo_lote = True
        request.state.cohorte = lote.cohorte_id
        request.state.corte = lote.corte_dias
        return result

    return application


app = crear_app()
