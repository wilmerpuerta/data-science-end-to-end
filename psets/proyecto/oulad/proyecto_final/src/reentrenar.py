"""Preparación reproducible del servicio con modelos existentes, sin repetir tuning.

Incluye preparación, reentrenamiento con parámetros congelados y comparación
de negocio. La promoción exige reanudación humana de la pausa de Kestra.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import shutil
from importlib.metadata import version as version_instalada
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits
from .datos import ROOT, desarrollo_temprano, sha256
from .pipeline import CATEGORICAS, columnas

FUENTES = {14: 'a6c0b65d4e354ceaabfc565c88bfa0c2', 28: '048df6920ba747d28d957b052e685666'}
NOMBRES = {14: 'oulad-apoyo-academico-semana2-modelo', 28: 'oulad-apoyo-academico-semana4-modelo'}
BASELINE = 'dcb91965644a479baa7a0f08555df32e'
FIXTURES = ROOT / 'tests/fixtures'


def entrada(frame):
    numericas, categoricas = columnas()
    names = [n for n in numericas if n not in ['log1p_clicks_current_14d', 'clicks_per_active_day_14d']] + categoricas
    x = frame[names].copy()
    for name in names:
        if name in categoricas:
            x[name] = x[name].astype(object).where(x[name].notna(), np.nan)
        else:
            x[name] = x[name].to_numpy(dtype=float, na_value=np.nan)
    return x


def categorias(modelo):
    encoder = modelo.named_steps['preparacion'].named_transformers_['cat'].named_steps['codificar']
    return dict(zip(CATEGORICAS, [[str(c) for c in values if c != '__MISSING__'] for values in encoder.categories_]))


def preparar(origen_local):
    import mlflow
    import mlflow.sklearn
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5001'))
    client = mlflow.MlflowClient()
    anterior = client.get_model_version_by_alias('oulad-apoyo-academico-v2-modelo', 'champion')
    FIXTURES.mkdir(parents=True, exist_ok=True)
    previo_path = FIXTURES / 'referencia.json'
    previo = json.loads(previo_path.read_text()) if previo_path.exists() else {}
    referencia = {'data_source': {'dataset': 'OULAD', 'source': 'https://research.stem.open.ac.uk/ouanalyse/dataset/', 'license': 'CC BY 4.0', 'publication_doi': 'https://doi.org/10.1038/sdata.2017.171', 'derivation': 'Fixed development rows, stratified sampling; original identifiers removed; feature values unchanged'}, 'status': 'prepared', 'pipeline_sha256': sha256(ROOT / 'src/pipeline.py'),
                  'reference_run_id': None, 'modelos': {}, 'ci_scope': 'Fixed development sample; reproduction only, not independent validation',
                  'tolerance': 1e-10, 'policy_status': 'experimental; institutional capacity and week split unconfirmed'}
    base_model = mlflow.sklearn.load_model(f'runs:/{BASELINE}/pipeline')
    dummy = base_model.named_steps['modelo']
    if dummy.strategy != 'most_frequent':
        raise ValueError('El respaldo debe coincidir con el Dummy del PSet 03')
    fail_index = list(base_model.classes_).index('Fail')
    fail_probability = float(int(np.argmax(dummy.class_prior_)) == fail_index)
    if fail_probability != 0:
        raise ValueError('La regla de respaldo esperada ha cambiado')
    baseline_run = client.get_run(BASELINE)
    referencia['baseline'] = {'snapshot_id': baseline_run.data.params['snapshot_id'],
                              'split_id': baseline_run.data.params['split_id'], 'gold': 'PSET2_OULAD.GOLD', 'nombre': 'dummy-pset3', 'version': 'baseline-v1', 'alias': 'respaldo',
                              'run_id': BASELINE, 'corte_entrenamiento': 56, 'probabilidad_fail': fail_probability,
                              'regla': 'most_frequent; empate determinista por matrícula para asignación al cupo'}
    for cut, source_run in FUENTES.items():
        run = client.get_run(source_run)
        if run.info.status != 'FINISHED' or run.data.params['cutoff_day'] != str(cut) or run.data.params['pipeline_sha256'] != referencia['pipeline_sha256']:
            raise ValueError('El modelo no coincide con su corte o preparación')
        frame, snapshot = desarrollo_temprano(origen_local, cut)
        if snapshot['id'] != run.data.params['snapshot_id']:
            raise ValueError('La muestra debe proceder del snapshot de entrenamiento registrado')
        # Selección reproducible y estratificada, solo de desarrollo; sin IDs reales publicados.
        indices = []
        for target in ['Approved', 'Fail', 'Withdrawn']:
            indices.extend(frame.loc[frame.target_class.eq(target)].sample(n=20, random_state=3400 + cut).index.tolist())
        sample = frame.loc[sorted(indices)].reset_index(drop=True)
        x = entrada(sample)
        uri = f'runs:/{source_run}/pipeline'
        modelo = mlflow.sklearn.load_model(uri)
        with threadpool_limits(limits=2):
            scores = modelo.predict_proba(x)[:, list(modelo.classes_).index('Fail')]
            base_scores = base_model.predict_proba(x)[:, fail_index]
        if not np.all(base_scores == fail_probability):
            raise ValueError('El respaldo no reproduce el baseline original')
        versions = client.search_model_versions(f"name='{NOMBRES[cut]}'")
        existing = next((v for v in sorted(versions, key=lambda v: int(v.version)) if v.run_id == source_run), None)
        version = existing or mlflow.register_model(uri, NOMBRES[cut])
        aliases = client.get_registered_model(NOMBRES[cut]).aliases
        if 'champion' not in aliases:
            client.set_registered_model_alias(NOMBRES[cut], 'champion', version.version)
        else:
            active = client.get_model_version_by_alias(NOMBRES[cut], 'champion')
            if active.run_id != source_run:
                raise ValueError('Existe otro champion temprano; no se reemplaza automáticamente')
        client.set_model_version_tag(NOMBRES[cut], version.version, 'cutoff_day', str(cut))
        client.set_model_version_tag(NOMBRES[cut], version.version, 'uso', 'servicio_experimental_pset4')
        info = mlflow.models.get_model_info(uri)
        folder = FIXTURES / f'semana{cut // 7}'
        if folder.exists():
            import yaml
            saved_info = yaml.safe_load((folder/'MLmodel').read_text())
            if saved_info['flavors']['python_function'].get('predict_fn') != 'predict_proba':
                shutil.rmtree(folder)
        if not folder.exists():
            mlflow.sklearn.save_model(modelo, str(folder), signature=info.signature, input_example=x.iloc[:1], pyfunc_predict_fn='predict_proba',
                                     pip_requirements=[f'{name}=={version_instalada(name)}' for name in ['mlflow','scikit-learn','numpy','pandas','scipy','cloudpickle','joblib','threadpoolctl']])
        fixture = mlflow.sklearn.load_model(str(folder))
        with threadpool_limits(limits=2):
            check = fixture.predict_proba(x)[:, list(fixture.classes_).index('Fail')]
        if not np.array_equal(scores, check):
            raise ValueError('La fixture no coincide con el modelo fuente')
        serializable = json.loads(x.to_json(orient='records'))
        sample_content = {'scope': referencia['ci_scope'], 'rows': [{'features': a, 'target': str(b)} for a, b in zip(serializable, sample.target_class)], 'expected_p_fail': scores.tolist()}
        (FIXTURES / f'muestra_semana{cut // 7}.json').write_text(json.dumps(sample_content, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        meta = {'nombre': NOMBRES[cut], 'version': str(version.version), 'alias': 'champion', 'run_id': source_run,
                'snapshot_id': snapshot['id'], 'split_id': run.data.params['split_id'], 'gold': 'PSET2_OULAD.GOLD',
                'cutoff_day': cut, 'categorias': categorias(modelo), 'signature': info.signature.to_dict(),
                'ci_ap_fail': float(average_precision_score(sample.target_class.eq('Fail'), scores)),
                'cv_ap_fail_mean': run.data.metrics['ap_fail_mean'], 'cv_ap_fail_std': run.data.metrics['ap_fail_std'],
                'cv_coverage_mean': run.data.metrics['coverage_mean'], 'cv_coverage_std': run.data.metrics['coverage_std']}
        referencia['modelos'][str(cut)] = meta
    baseline_folder = FIXTURES / 'baseline'
    if baseline_folder.exists():
        import yaml
        saved = yaml.safe_load((baseline_folder/'MLmodel').read_text())
        if saved['flavors']['python_function'].get('predict_fn') != 'predict_proba':
            shutil.rmtree(baseline_folder)
    if not baseline_folder.exists():
        base_info = mlflow.models.get_model_info(f'runs:/{BASELINE}/pipeline')
        mlflow.sklearn.save_model(base_model, str(baseline_folder), signature=base_info.signature, pyfunc_predict_fn='predict_proba')
    referencia['files_sha256'] = {p.relative_to(FIXTURES).as_posix(): sha256(p) for p in FIXTURES.rglob('*') if p.is_file() and p.name not in ['referencia.json', '.gitkeep']}
    if previo.get('reference_run_id') and all(previo.get(k) == v for k, v in referencia.items() if k != 'reference_run_id'):
        referencia['reference_run_id'] = previo['reference_run_id']
    (FIXTURES / 'referencia.json').write_text(json.dumps(referencia, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    current = client.get_model_version_by_alias('oulad-apoyo-academico-v2-modelo', 'champion')
    if (current.version, current.run_id) != (anterior.version, anterior.run_id):
        raise ValueError('El champion histórico fue alterado')
    print('Modelos tempranos y fixtures preparados; champion histórico preservado; cero entrenamientos nuevos.')


def registrar_referencia():
    import mlflow
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for path in [*ROOT.joinpath('src').glob('*.py'), *ROOT.joinpath('api').glob('*.py'), ROOT/'requirements.txt']:
        if subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)], cwd=ROOT, capture_output=True).returncode:
            raise ValueError('Fuente sin versionar: ' + path.name)
    dirty = subprocess.run(['git', 'diff', 'HEAD', '--exit-code', '--', 'src', 'api', 'requirements.txt'], cwd=ROOT, capture_output=True)
    if dirty.returncode:
        raise ValueError('Versionar el código antes de registrar la referencia de servicio')
    path = FIXTURES / 'referencia.json'
    ref = json.loads(path.read_text())
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5001'))
    if ref.get('reference_run_id'):
        print('La referencia ya está registrada: ' + ref['reference_run_id']); return
    mlflow.set_experiment('oulad-apoyo-academico-operacion')
    with mlflow.start_run(run_name='referencia-ci-servicio-temprano') as run:
        mlflow.set_tags({'fase': 'preparacion_servicio', 'git_commit': source, 'new_training': 'false', 'scope': ref['ci_scope']})
        for cut, meta in ref['modelos'].items():
            mlflow.log_param('source_run_id_dia' + cut, meta['run_id'])
            mlflow.log_metric('ci_ap_fail_dia' + cut, meta['ci_ap_fail'])
        mlflow.log_param('snapshot_id', ref['modelos']['14']['snapshot_id'])
        mlflow.log_param('pipeline_sha256', ref['pipeline_sha256'])
        ref['reference_run_id'] = run.info.run_id
        mlflow.log_dict(ref, 'referencia_ci.json')
    path.write_text(json.dumps(ref, ensure_ascii=False, indent=2) + '\n')
    print('Referencia CI registrada sin entrenamiento: ' + ref['reference_run_id'])


def exportar_corridas():
    import mlflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5001'))
    nombres = ['oulad-apoyo-academico-v2', 'oulad-apoyo-academico-operacion']
    experiments = [mlflow.get_experiment_by_name(name) for name in nombres]
    ids = [exp.experiment_id for exp in experiments if exp is not None]
    runs = mlflow.search_runs(experiment_ids=ids)
    path = ROOT / 'docs/corridas.csv'
    runs.to_csv(path, index=False)
    print(f'Exportadas {len(runs)} corridas, incluidas preparación y fallos históricos.')



# Política congelada antes de ajustar el challenger o consultar su comparación.
CICLO = 'reentrenamiento-28-deriva-v1'
PROTOCOLO_REENTRENAMIENTO = {
    'version': 'reentrenamiento-1', 'corte': 28, 'plan': 'oulad-2014j-deriva-v1', 'lote_disparador': 'L07',
    'ventana': 'Histórico de desarrollo del PSet 03 más matrículas recientes etiquetadas del mismo plan y corte; una fila por matrícula.',
    'pesos': 'Igual peso por matrícula; sin repetición de tuning ni cambio de hiperparámetros.',
    'reserva': 'Último lote etiquetado del mismo corte, elegido por día de predicción. Excluir toda su cohorte y sus personas del entrenamiento, de otros cortes y de ambos escenarios.',
    'metrica_primaria': 'Cobertura acumulada de Fail de la base día 14, con cupos y propuestas de semana 2 comunes al champion y challenger.',
    'capacidad': '1/10', 'fraccion_semana2': '1/4', 'sigmas_promocion': 1,
    'regla': 'Promover solo si la ganancia de cobertura supera estrictamente una desviación estándar de la misma política histórica OOF, con iguales cupos y aprobación humana.',
    'referencia_variacion': 'Cinco folds históricos agrupados por estudiante, ambos cortes OOF y módulos del lote de comparación. No es un intervalo de confianza.',
    'meta_10': 'Reportar +10 % relativo frente al predictor estático con la misma política de dos rondas; no sustituye la comparación challenger-champion.',
    'limitacion': 'Reevaluación retrospectiva de un benchmark ya inspeccionado. No demuestra beneficio causal ni una validación prospectiva nueva.',
}
RECURSOS = ROOT/'.local/reentrenamiento/recursos.json'
REF_REENTRENO = FIXTURES/'referencia_reentrenamiento.json'


def politica_reentrenamiento():
    from fractions import Fraction
    from api.esquemas import PoliticaCupos
    return PoliticaCupos(capacidad=Fraction(PROTOCOLO_REENTRENAMIENTO['capacidad']),
                         fraccion_semana2=Fraction(PROTOCOLO_REENTRENAMIENTO['fraccion_semana2']))


def seleccionar(frame, riesgos, base, corte, previos=None):
    from api.esquemas import Candidato, priorizar_cohorte
    candidatos = [Candidato(str(r.matricula),str(r.edicion),str(r.persona),float(p)) for r,p in zip(frame.itertuples(),riesgos)]
    resultado = priorizar_cohorte(candidatos,cohorte_base=base,elegibles_actuales=dict(zip(frame.matricula,frame.edicion)),
        seleccionados_previos=previos or {},corte_dias=corte,politica=politica_reentrenamiento())
    nuevas = {r['matricula']:r['edicion'] for r in resultado['predicciones'] if r['consume_cupo_nuevo']}
    return {**(previos or {}), **nuevas}, resultado


def metricas_negocio(seleccionadas, labels, base):
    if not set(base) <= set(labels) or not set(seleccionadas) <= set(base):
        raise ValueError('Evaluación exige todas las etiquetas de la base y selecciones válidas')
    fail = sum(labels[k]=='Fail' for k in base)
    tp = sum(labels[k]=='Fail' for k in seleccionadas)
    return {'cupos':len(seleccionadas),'fail_base':fail,'tp':tp,'fp':len(seleccionadas)-tp,
            'cobertura':tp/fail if fail else None,'precision':tp/len(seleccionadas) if seleccionadas else None}


def regla_promocion(champion, challenger, sigma):
    from math import floor
    if sigma<0 or not np.isfinite(sigma):raise ValueError('Variación de referencia inválida')
    if champion['cupos']!=challenger['cupos'] or champion['fail_base']!=challenger['fail_base']:
        raise ValueError('Comparar con iguales cupos y denominador')
    fail = champion['fail_base'];delta = challenger['tp']-champion['tp']
    minimo = floor(fail*sigma+1e-12)+1 if fail else None
    elegible = bool(fail and delta>=minimo)
    return {'metrica':'cobertura_fail','ganancia_tp':delta,'ganancia_cobertura':delta/fail if fail else None,
            'sigma_politica':float(sigma),'ganancia_tp_minima':minimo,'elegible_promocion':elegible,
            'aprobacion_humana_requerida':True,'recomendacion':'aprobar' if elegible else 'rechazar'}


def preparar_recursos(origen_local):
    """Datos privados y CV histórica de política; nunca ajusta un modelo."""
    from .datos import identidad
    origen_local = Path(origen_local)
    assignments = pd.read_csv(origen_local/'anticipacion/assignments.csv')[['enrollment_key','cv_fold']]
    frames = {}
    fuentes = {}
    for cut in [14,28]:
        frame,snapshot = desarrollo_temprano(origen_local,cut)
        frame = frame.merge(assignments,on='enrollment_key',validate='one_to_one')
        path = origen_local/'anticipacion'/f'boosting-{cut}-longitudinal-oof.parquet'
        frame = frame.merge(pd.read_parquet(path),on='enrollment_key',validate='one_to_one')
        frame['matricula'] = frame.enrollment_key.map(lambda v:'m_'+identidad(str(v))[:40])
        frame['persona'] = frame.id_student.map(lambda v:'p_'+identidad(str(v))[:40])
        frame['edicion'] = frame.edition_key.astype(str)
        frames[cut] = frame;fuentes[str(cut)] = sha256(path)
    ref = {'protocolo':PROTOCOLO_REENTRENAMIENTO,'snapshot_id':snapshot['id'],
           'pipeline_sha256':sha256(ROOT/'src/pipeline.py'),'oof_sha256':fuentes,
           'assignments_sha256':sha256(origen_local/'anticipacion/assignments.csv'),'cv_politica':{}}
    for modulo in sorted(frames[14].code_module.unique()):
        vals=[]
        for fold in range(5):
            a=frames[14].loc[frames[14].code_module.eq(modulo)&frames[14].cv_fold.eq(fold)]
            b=frames[28].loc[frames[28].code_module.eq(modulo)&frames[28].cv_fold.eq(fold)]
            base=dict(zip(a.matricula,a.edicion));labels=dict(zip(a.matricula,a.target_class))
            early,_=seleccionar(a,a.p_fail,base,14)
            all_selected,_=seleccionar(b,b.p_fail,base,28,early)
            vals.append(metricas_negocio(all_selected,labels,base)['cobertura'])
        ref['cv_politica'][modulo] = {'folds':vals,'media':float(np.mean(vals)),'std':float(np.std(vals,ddof=1))}
    ref['id'] = identidad(ref)
    REF_REENTRENO.write_text(json.dumps(ref,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    folder=RECURSOS.parent;folder.mkdir(parents=True,exist_ok=True)
    historico=frames[28].drop(columns=['p_fail']).copy()
    path=folder/'historico.parquet';historico.to_parquet(path,index=False)
    estaticos={str(c):json.loads((origen_local/'anticipacion'/f'boosting-{c}-estatico.json').read_text())['run_id'] for c in [14,28]}
    codigo={str(p.relative_to(ROOT)):sha256(p) for p in [ROOT/'src/reentrenar.py',ROOT/'src/pipeline.py',ROOT/'api/esquemas.py',ROOT/'requirements.txt',ROOT/'api/Dockerfile']}
    info={'referencia_id':ref['id'],'snapshot_id':snapshot['id'],'historico_sha256':sha256(path),
          'filas_historico':len(historico),'estaticos':estaticos,'codigo_sha256':codigo,
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    RECURSOS.write_text(json.dumps(info,indent=2)+'\n')
    return {'referencia_id':ref['id'],'filas_historico':len(historico),'nuevos_entrenamientos':0}


def registrar_contratos_reentrenamiento():
    from .datos import TABLAS_OPERACION,CLAVES_OPERACION
    TABLAS_OPERACION.update({
        'REENTRENAMIENTOS':{'ID_EVENTO':'VARCHAR','CICLO_ID':'VARCHAR','PLAN_ID':'VARCHAR','ESTADO':'VARCHAR','CONTENIDO':'VARIANT','HUELLA':'VARCHAR'},
    })
    CLAVES_OPERACION['REENTRENAMIENTOS']=['ID_EVENTO']


def evento(repo,estado,contenido):
    from .datos import identidad,PLAN_DERIVA
    repo.insertar('REENTRENAMIENTOS',[{'ID_EVENTO':identidad([CICLO,estado]),'CICLO_ID':CICLO,
        'PLAN_ID':PLAN_DERIVA,'ESTADO':estado,'CONTENIDO':contenido}])


def leer_evento(repo,estado):
    from .datos import ESQUEMA_OPERACION
    with repo.conn.cursor() as cur:
        rows=cur.execute(f'SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.REENTRENAMIENTOS WHERE CICLO_ID=%s AND ESTADO=%s',(CICLO,estado)).fetchall()
    if len(rows)>1:raise ValueError('Evento de reentrenamiento duplicado')
    return json.loads(rows[0][0]) if rows else None


def preparar_ventana(historico,lotes,labels,comparacion,dia):
    """Una fila por matrícula; reserva completa y exclusión por persona."""
    reservadas=set(comparacion['manifiesto']['base'])
    personas=set(comparacion['manifiesto']['personas'].values())
    previo=len(historico)
    historico=historico.loc[~historico.persona.isin(personas)&~historico.matricula.isin(reservadas)].copy()
    recientes=[]
    for lote in lotes:
        if lote['corte']!=28:continue
        for row in lote['solicitud']['matriculas']:
            if row['matricula'] in reservadas or row['persona'] in personas:continue
            label=labels.get(row['matricula'])
            if label is None or label['dia']>dia:continue
            recientes.append({**row['features'],'matricula':row['matricula'],'persona':row['persona'],'edicion':row['edicion'],
                              'target_class':label['target'],'origen':'reciente'})
    reciente=pd.DataFrame(recientes)
    if reciente.empty:raise ValueError('Sin matrículas recientes etiquetadas para reentrenar')
    historico['origen']='historico'
    fields=list(entrada(historico).columns)+['matricula','persona','edicion','target_class','origen']
    train=pd.concat([historico[fields],reciente[fields]],ignore_index=True).sort_values('matricula').reset_index(drop=True)
    # La unión conserva los valores con los tipos de la firma del modelo.
    normalizado=entrada(train)
    for campo in normalizado:
        train[campo]=normalizado[campo]
    if train.matricula.duplicated().any() or set(train.persona)&personas or set(train.matricula)&reservadas:
        raise ValueError('Fuga o duplicación en la ventana')
    if train.target_class.isna().any() or not set(train.target_class)<={'Approved','Fail','Withdrawn'}:
        raise ValueError('Etiquetas incompletas')
    return train,{'historico':len(historico),'reciente':len(reciente),'excluidas_historico':previo-len(historico),
                  'matriculas_reservadas':len(reservadas),'personas_reservadas':len(personas),'solapamiento_personas':0}


def riesgos(modelo,frame):
    with threadpool_limits(limits=2):p=modelo.predict_proba(entrada(frame))
    if p.shape!=(len(frame),3) or not np.isfinite(p).all() or (p<0).any() or (p>1).any() or not np.allclose(p.sum(axis=1),1):
        raise ValueError('Probabilidades inválidas')
    return p[:,list(modelo.classes_).index('Fail')]


def _frame_lote(lote):
    return pd.DataFrame([{**r['features'],'matricula':r['matricula'],'persona':r['persona'],'edicion':r['edicion']} for r in lote['solicitud']['matriculas']])


def preparar_ciclo(repo,execution_id):
    import mlflow
    import mlflow.sklearn
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedGroupKFold
    from .datos import identidad,PLAN_DERIVA,ESQUEMA_OPERACION
    from api.esquemas import evaluar_meta
    previo=leer_evento(repo,'COMPARADO')
    if previo:return {**previo,'repeticion':True}
    ref=json.loads(REF_REENTRENO.read_text());recursos=json.loads(RECURSOS.read_text())
    if ref['id']!=identidad({k:v for k,v in ref.items() if k!='id'}) or ref['protocolo']!=PROTOCOLO_REENTRENAMIENTO or recursos['referencia_id']!=ref['id']:
        raise ValueError('Referencia de reentrenamiento alterada')
    folder=RECURSOS.parent/CICLO
    if (folder/'comparacion.json').exists():
        result=json.loads((folder/'comparacion.json').read_text())
        if result['referencia_id']!=ref['id']:raise ValueError('Ciclo existente con otra referencia')
        evento(repo,'COMPARADO',result)
        return {**result,'repeticion':True}
    if (folder/'entrenado.json').exists():
        return recuperar_entrenado(repo,json.loads((folder/'entrenado.json').read_text()),execution_id)

    for path,h in recursos['codigo_sha256'].items():
        if sha256(ROOT/path)!=h:raise ValueError('Preparar recursos con la fuente actual antes de entrenar')
    hist_path=RECURSOS.parent/'historico.parquet'
    if sha256(hist_path)!=recursos['historico_sha256']:raise ValueError('Histórico modificado')
    dia=repo.reloj(PLAN_DERIVA)
    plan=repo.contenido('PLANES',PLAN_DERIVA)
    if plan is None:raise ValueError('Escenario no preparado')
    lotes=[repo.contenido('LOTES_ENTRADA',PLAN_DERIVA,m['lote_id']) for m in plan['lotes']]
    if any(repo.contenido('LOTES_PROCESADOS',PLAN_DERIVA,l['lote_id']) is None for l in lotes):
        raise ValueError('Completar el escenario antes de armar la ventana')
    with repo.conn.cursor() as cur:
        datos=[json.loads(r[0]) for r in cur.execute(f'SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.MONITOREO WHERE PLAN_ID=%s AND LOTE_ID=%s AND DIA_REVISION<=%s',(PLAN_DERIVA,'L07',dia)).fetchall()]
        labels={r[0]:{'target':r[1],'dia':int(r[2])} for r in cur.execute(f'SELECT MATRICULA,TARGET_CLASS,DIA_DISPONIBLE FROM {ESQUEMA_OPERACION}.ETIQUETAS WHERE PLAN_ID=%s AND DIA_DISPONIBLE<=%s',(PLAN_DERIVA,dia)).fetchall()}
    alerta=next((m for m in datos if m['reentrenamiento_propuesto'] and m['etiquetas_completas'] and m['corte']==28),None)
    if alerta is None:raise ValueError('Sin disparador de desempeño persistente etiquetado')
    disponibles=[l for l in lotes if l['corte']==28 and all(m in labels for m in l['manifiesto']['base'])]
    if not disponibles:raise ValueError('Sin comparación madura')
    comparacion=max(disponibles,key=lambda l:l['dia'])
    if comparacion['lote_id']!='L08' or comparacion.get('alterado'):
        raise ValueError('La reserva predeclarada no coincide con el último lote etiquetado')
    temprano=next(l for l in lotes if l['corte']==14 and l['cohorte_id']==comparacion['cohorte_id'])
    train,auditoria=preparar_ventana(pd.read_parquet(hist_path),lotes,labels,comparacion,dia)
    modulos=comparacion['modulos']
    if len(modulos)!=1:raise ValueError('Esta versión del protocolo exige una referencia CV de módulo único')
    sigma=ref['cv_politica'][modulos[0]]['std']
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI','http://127.0.0.1:5001'))
    client=mlflow.MlflowClient();active=client.get_model_version_by_alias(NOMBRES[28],'champion')
    if active.run_id!=FUENTES[28]:raise ValueError('El champion cambió; revisar el ciclo antes de continuar')
    source_run=client.get_run(active.run_id)
    if source_run.data.params['pipeline_sha256']!=ref['pipeline_sha256']:raise ValueError('Preparación del champion incompatible')
    champion=mlflow.sklearn.load_model(f'models:/{NOMBRES[28]}/{active.version}')
    parametros=champion.named_steps['modelo'].get_params(deep=False)
    folder=RECURSOS.parent/CICLO;folder.mkdir(exist_ok=True)
    train_path=folder/'entrenamiento.parquet';train.to_parquet(train_path,index=False)
    snapshot={'protocolo':PROTOCOLO_REENTRENAMIENTO,'referencia_id':ref['id'],'snapshot_historico':ref['snapshot_id'],
              'plan_id':PLAN_DERIVA,'plan_huella':identidad(plan),'train_sha256':sha256(train_path),'auditoria':auditoria,
              'dia_simulado':dia,'comparacion':comparacion['lote_id'],'exclusion_por_persona':True,'pipeline_sha256':ref['pipeline_sha256']}
    snapshot['id']=identidad(snapshot)
    (folder/'snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    # El contexto no contiene targets de comparación en la matriz de entrenamiento.
    mlflow.set_experiment('oulad-apoyo-academico-operacion')
    x=entrada(train);y=train.target_class.astype(str).to_numpy();groups=train.persona.to_numpy()
    splitter=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=1706)
    fold_metrics=[];fold_manifest=[]
    with mlflow.start_run(run_name=CICLO) as run:
        mlflow.set_tags({'fase':'reentrenamiento','motivo':'dos_caidas_ap_corte28_lotes_etiquetados','ciclo_id':CICLO,
                         'git_commit':recursos['git_commit'],'new_training':'true','estado_aprobacion':'pendiente'})
        mlflow.log_params({'cutoff_day':28,'pipeline_sha256':ref['pipeline_sha256'],'snapshot_id':snapshot['id'],
            'source_snapshot_id':ref['snapshot_id'],'split_id':identidad({'seed':1706,'grupos':train.persona.tolist(),'matriculas':train.matricula.tolist()}),
            'champion_run_id':active.run_id,'champion_version':active.version,'plan_id':PLAN_DERIVA,'lote_comparacion':'L08',
            'training_window':PROTOCOLO_REENTRENAMIENTO['ventana'],'new_tuning':'false','policy_reference_id':ref['id'],
            'cv_coverage_scope':'singlecut_10pct; promoción usa sigma de política OOF de dos rondas'})
        mlflow.log_params({'model__'+k:str(v) for k,v in parametros.items()})
        for fold,(a,b) in enumerate(splitter.split(x,y,groups=groups)):
            if set(groups[a])&set(groups[b]):raise ValueError('Fuga de estudiantes entre folds')
            fitted=clone(champion)
            with threadpool_limits(limits=2):fitted.fit(x.iloc[a],y[a])
            p=riesgos(fitted,train.iloc[b]);ap=float(average_precision_score(y[b]=='Fail',p))
            # Métrica single-cut comparable con la metadata original del Registry.
            v=train.iloc[b];base=dict(zip(v.matricula,v.edicion))
            from fractions import Fraction
            from api.esquemas import Candidato,PoliticaCupos,priorizar_cohorte
            ranked=priorizar_cohorte([Candidato(r.matricula,r.edicion,r.persona,float(q)) for r,q in zip(v.itertuples(),p)],
                cohorte_base=base,elegibles_actuales=base,seleccionados_previos={},corte_dias=28,
                politica=PoliticaCupos(fraccion_semana2=Fraction(0)))
            chosen={r['matricula']:r['edicion'] for r in ranked['predicciones'] if r['consume_cupo_nuevo']}
            cov=metricas_negocio(chosen,dict(zip(v.matricula,v.target_class)),base)['cobertura']
            fold_metrics.append({'fold':fold,'ap_fail':ap,'coverage':cov,'train_n':len(a),'valid_n':len(b)})
            fold_manifest.append({'fold':fold,'train_matriculas':train.iloc[a].matricula.tolist(),'valid_matriculas':v.matricula.tolist()})
        for name in ['ap_fail','coverage']:
            vals=[v[name] for v in fold_metrics]
            mlflow.log_metric(name+'_mean',float(np.mean(vals)));mlflow.log_metric(name+'_std',float(np.std(vals,ddof=1)))
        challenger=clone(champion)
        with threadpool_limits(limits=2):challenger.fit(x,y)
        if challenger.named_steps['modelo'].get_params(deep=False)!=parametros:raise ValueError('Hiperparámetros cambiaron')
        base=comparacion['manifiesto']['base'];ys={k:labels[k]['target'] for k in base}
        with repo.conn.cursor() as cur:
            previos={r[0]:r[1] for r in cur.execute(f'''SELECT MATRICULA,SALIDA:edicion::VARCHAR FROM {ESQUEMA_OPERACION}.PREDICCIONES
                WHERE PLAN_ID=%s AND COHORTE_ID=%s AND CORTE=14 AND SALIDA:consume_cupo_nuevo::BOOLEAN''',(PLAN_DERIVA,comparacion['cohorte_id'])).fetchall()}
        test=_frame_lote(comparacion);actual={};scores={}
        for name,modelo in [('champion',champion),('challenger',challenger)]:
            p=riesgos(modelo,test);selected,_=seleccionar(test,p,base,28,previos)
            actual[name]=metricas_negocio(selected,ys,base)
            actual[name]['ap_fail']=float(average_precision_score(test.matricula.map(ys).eq('Fail'),p))
            scores[name]=p.tolist()
        early_static=mlflow.sklearn.load_model(f'runs:/{recursos["estaticos"]["14"]}/pipeline')
        late_static=mlflow.sklearn.load_model(f'runs:/{recursos["estaticos"]["28"]}/pipeline')
        a=_frame_lote(temprano);s14,_=seleccionar(a,riesgos(early_static,a),base,14)
        static,_=seleccionar(test,riesgos(late_static,test),base,28,s14)
        actual['estatico']=metricas_negocio(static,ys,base)
        regla=regla_promocion(actual['champion'],actual['challenger'],sigma)
        meta={name:evaluar_meta(actual['estatico']['tp'],actual[name]['tp'],actual[name]['fail_base'],actual[name]['cupos']) for name in ['champion','challenger']}
        signature=mlflow.models.get_model_info(f'models:/{NOMBRES[28]}/{active.version}').signature
        mlflow.sklearn.log_model(challenger,'pipeline',signature=signature,input_example=x.iloc[:1],pyfunc_predict_fn='predict_proba',
            pip_requirements=[f'{n}=={version_instalada(n)}' for n in ['mlflow','scikit-learn','numpy','pandas','scipy','cloudpickle','joblib','threadpoolctl']])
        for name,metrics in actual.items():
            mlflow.log_metrics({'evaluacion_'+name+'_'+k:float(v) for k,v in metrics.items() if v is not None})
        mlflow.log_dict(snapshot,'snapshot.json');mlflow.log_dict({'folds':fold_metrics},'folds.json')
        mlflow.log_dict({'folds':fold_manifest},'splits.json');mlflow.log_dict({'regla':regla,'modelos':actual,'meta_10':meta},'comparacion.json')
        mlflow.log_dict({'codigo_sha256':recursos['codigo_sha256'],'git_commit':recursos['git_commit']},'codigo.json')
        run_id=run.info.run_id
    entrenamiento={'run_id':run_id,'actual':actual,'regla':regla,'meta':meta,'snapshot':snapshot,'auditoria':auditoria,
                   'parametros':parametros,'champion_version':str(active.version),'champion_run_id':active.run_id,
                   'id_disparador':alerta['id_monitoreo'],'referencia_id':ref['id'],'dia_simulado':dia}
    guardar_json(folder/'entrenado.json',entrenamiento)
    versions=client.search_model_versions(f"name='{NOMBRES[28]}'")
    version=next((v for v in versions if v.run_id==run_id),None) or mlflow.register_model(f'runs:/{run_id}/pipeline',NOMBRES[28])
    aliases=client.get_registered_model(NOMBRES[28]).aliases
    if aliases.get('challenger') and str(aliases['challenger'])!=str(version.version):
        v=client.get_model_version(NOMBRES[28],str(aliases['challenger']))
        if client.get_run(v.run_id).data.tags.get('ciclo_id')!=CICLO:raise ValueError('Existe otro challenger pendiente')
    client.set_registered_model_alias(NOMBRES[28],'challenger',version.version)
    client.set_model_version_tag(NOMBRES[28],version.version,'ciclo_id',CICLO)
    client.set_model_version_tag(NOMBRES[28],version.version,'estado_aprobacion','pendiente')
    result={'ciclo_id':CICLO,'estado':'COMPARADO','plan_id':PLAN_DERIVA,'execution_id':execution_id,'run_id':run_id,
        'modelo':NOMBRES[28],'champion_version':str(active.version),'champion_run_id':active.run_id,
        'challenger_version':str(version.version),'snapshot_id':snapshot['id'],'dia_simulado':dia,'lote_comparacion':'L08',
        'auditoria':auditoria,'parametros_modelo':parametros,'modelos':actual,'regla':regla,'meta_10':meta,
        'sigma_referencia':ref['cv_politica'][modulos[0]],'id_disparador':alerta['id_monitoreo'],'referencia_id':ref['id']}
    guardar_json(folder/'comparacion.json',result)
    evento(repo,'COMPARADO',result)
    return result



def guardar_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n');tmp.replace(path)


def recuperar_entrenado(repo,data,execution_id):
    """Reconciliar un ajuste terminado después de un fallo de publicación."""
    import mlflow
    from .datos import PLAN_DERIVA
    ref=json.loads(REF_REENTRENO.read_text())
    if data['referencia_id']!=ref['id']:raise ValueError('Checkpoint de otro protocolo')
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI','http://127.0.0.1:5001'))
    client=mlflow.MlflowClient();active=client.get_model_version_by_alias(NOMBRES[28],'champion')
    if str(active.version)!=data['champion_version']:raise ValueError('Revisar cambio concurrente del champion')
    versions=client.search_model_versions(f"name='{NOMBRES[28]}'")
    version=next((v for v in versions if v.run_id==data['run_id']),None) or mlflow.register_model(f'runs:/{data["run_id"]}/pipeline',NOMBRES[28])
    aliases=client.get_registered_model(NOMBRES[28]).aliases
    if aliases.get('challenger') and str(aliases['challenger'])!=str(version.version):
        other=client.get_model_version(NOMBRES[28],str(aliases['challenger']))
        if client.get_run(other.run_id).data.tags.get('ciclo_id')!=CICLO:raise ValueError('Existe otro challenger pendiente')
    client.set_registered_model_alias(NOMBRES[28],'challenger',version.version)
    client.set_model_version_tag(NOMBRES[28],version.version,'ciclo_id',CICLO)
    client.set_model_version_tag(NOMBRES[28],version.version,'estado_aprobacion','pendiente')
    result={'ciclo_id':CICLO,'estado':'COMPARADO','plan_id':PLAN_DERIVA,'execution_id':execution_id,
        'run_id':data['run_id'],'modelo':NOMBRES[28],'champion_version':data['champion_version'],'champion_run_id':data['champion_run_id'],
        'challenger_version':str(version.version),'snapshot_id':data['snapshot']['id'],'dia_simulado':data['dia_simulado'],
        'lote_comparacion':'L08','auditoria':data['auditoria'],'parametros_modelo':data['parametros'],'modelos':data['actual'],
        'regla':data['regla'],'meta_10':data['meta'],'sigma_referencia':ref['cv_politica']['DDD'],
        'id_disparador':data['id_disparador'],'referencia_id':ref['id']}
    guardar_json(RECURSOS.parent/CICLO/'comparacion.json',result);evento(repo,'COMPARADO',result)
    return result


def verificar_pausa(execution_id,decision,motivo,responsable):
    """Verificar la reanudación real de Kestra antes de aceptar una decisión."""
    import urllib.request,base64,re
    if not re.fullmatch('[A-Za-z0-9_-]{1,128}',execution_id):raise ValueError('Execution id inválido')
    base=os.environ.get('PSET4_KESTRA_URL','http://kestra:8080/api/v1/main')
    secret=os.environ.get('PSET4_KESTRA_PASSWORD')
    if not secret:raise ValueError('Falta autenticación del verificador de pausa')
    user=os.environ.get('PSET4_KESTRA_USER','admin@psets.local')
    auth=base64.b64encode((user+':'+secret).encode()).decode()
    request=urllib.request.Request(base+'/executions/'+execution_id,headers={'Authorization':'Basic '+auth})
    with urllib.request.urlopen(request,timeout=30) as response:data=json.load(response)
    if data.get('flowId')!='reentrenamiento' or data.get('namespace')!='pset4.oulad':raise ValueError('Ejecución ajena al flujo de aprobación')
    task=next((t for t in data.get('taskRunList',[]) if t['taskId']=='aprobacion'),None)
    if data.get('inputs',{}).get('ciclo_id')!=CICLO:raise ValueError('Aprobación de otro ciclo')
    outputs=(task or {}).get('outputs',{})
    resume=outputs.get('onResume',{})
    if not task or task['state']['current']!='SUCCESS' or any(resume.get(k)!=v for k,v in [('decision',decision),('motivo',motivo),('responsable',responsable)]):
        raise ValueError('No existe una reanudación humana coincidente')
    return {'execution_id':execution_id,'responsable':responsable,'usuario_kestra':outputs.get('resumed',{}).get('by'),
            'resumido_en':outputs.get('resumed',{}).get('on'),'fuente':'kestra_pause'}


def validar_decision(preparado,decision,motivo,responsable,version_actual):
    if decision not in ['aprobar','rechazar'] or not isinstance(motivo,str) or not motivo.strip() or len(motivo)>1000:
        raise ValueError('Decisión o motivo inválidos')
    if not isinstance(responsable,str) or not responsable.strip() or len(responsable)>128:
        raise ValueError('Se requiere responsable de la decisión')
    if str(version_actual) not in {preparado['champion_version'],preparado['challenger_version']}:
        raise ValueError('El alias cambió fuera de este ciclo; revisar antes de resolver')
    if decision=='rechazar':return 'RECHAZADO'
    return 'PROMOVIDO' if preparado['regla']['elegible_promocion'] else 'BLOQUEADO_POR_REGLA'


def decidir_ciclo(repo,execution_id,decision,motivo,responsable):
    import mlflow
    from .datos import ahora
    previo=leer_evento(repo,'DECIDIDO')
    if previo:
        if previo['decision']!=decision or previo['motivo']!=motivo or previo['responsable']!=responsable:
            raise ValueError('La decisión registrada no se reemplaza')
        return {**previo,'repeticion':True}
    preparado=leer_evento(repo,'COMPARADO')
    if preparado is None:raise ValueError('Comparar antes de decidir')
    aprobacion=verificar_pausa(execution_id,decision,motivo,responsable)
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI','http://127.0.0.1:5001'))
    client=mlflow.MlflowClient();active=client.get_model_version_by_alias(NOMBRES[28],'champion')
    estado=validar_decision(preparado,decision,motivo,responsable,active.version)
    carpeta=RECURSOS.parent/CICLO
    intent_path=carpeta/'decision-solicitada.json'
    if intent_path.exists():
        intent=json.loads(intent_path.read_text())
        if any(intent[k]!=v for k,v in [('decision',decision),('motivo',motivo),('responsable',responsable)]):raise ValueError('Hay otra decisión solicitada')
    else:
        intent={**aprobacion,'decision':decision,'motivo':motivo,'momento_solicitud':ahora()};guardar_json(intent_path,intent)
    evento(repo,'DECISION_SOLICITADA',intent)
    if estado=='PROMOVIDO':
        candidate=client.get_model_version(NOMBRES[28],preparado['challenger_version'])
        if candidate.run_id!=preparado['run_id']:raise ValueError('Versión candidata alterada')
        client.set_registered_model_alias(NOMBRES[28],'champion',candidate.version)
    elif str(active.version)!=preparado['champion_version']:
        raise ValueError('No se revierte una promoción mediante un rechazo tardío')
    final=client.get_model_version_by_alias(NOMBRES[28],'champion')
    client.set_tag(preparado['run_id'],'estado_aprobacion',estado.lower())
    client.set_model_version_tag(NOMBRES[28],preparado['challenger_version'],'estado_aprobacion',estado.lower())
    result={**intent,'ciclo_id':CICLO,'estado':estado,'run_id':preparado['run_id'],
        'champion_anterior':preparado['champion_version'],'challenger_version':preparado['challenger_version'],
        'champion_actual':str(final.version),'regla':preparado['regla']}
    guardar_json(carpeta/'decision.json',result);evento(repo,'DECIDIDO',result)
    return result


def rollback_ciclo(repo,motivo,responsable):
    import mlflow
    from .datos import ahora
    preparado=leer_evento(repo,'COMPARADO');decidido=leer_evento(repo,'DECIDIDO')
    if preparado is None or decidido is None or decidido['estado']!='PROMOVIDO':
        raise ValueError('Rollback exige una promoción aprobada de este ciclo')
    if not motivo or not responsable:raise ValueError('Registrar motivo y responsable del rollback')
    previo=leer_evento(repo,'ROLLBACK')
    if previo:return {**previo,'repeticion':True}
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI','http://127.0.0.1:5001'))
    client=mlflow.MlflowClient();active=client.get_model_version_by_alias(NOMBRES[28],'champion')
    if str(active.version)!=preparado['challenger_version']:raise ValueError('El alias cambió después de la promoción; revisar rollback')
    client.set_registered_model_alias(NOMBRES[28],'champion',preparado['champion_version'])
    result={'ciclo_id':CICLO,'estado':'ROLLBACK','de':str(active.version),'a':preparado['champion_version'],
            'responsable':responsable,'motivo':motivo,'momento':ahora(),'sin_rebuild':True}
    evento(repo,'ROLLBACK',result);return result


def trabajar(operacion,execution_id='manual',decision=None,motivo=None,responsable=None):
    import fcntl
    from .datos import conectar_snowflake,RepositorioSnowflake
    registrar_contratos_reentrenamiento()
    with (ROOT/'.local/escritor-snowflake.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX)
        with conectar_snowflake() as conn:
            repo=RepositorioSnowflake(conn);repo.asegurar()
            if operacion=='solicitar':return solicitar_ciclo(repo,execution_id)
            if operacion=='preparar':return preparar_ciclo(repo,execution_id)
            if operacion=='decidir':return decidir_ciclo(repo,execution_id,decision,motivo,responsable)
            if operacion=='rollback':return rollback_ciclo(repo,motivo,responsable)
            raise ValueError('Operación de ciclo desconocida')


def exportar_reentrenamientos(repo,destino):
    import csv
    from .datos import ESQUEMA_OPERACION
    with repo.conn.cursor() as cur:
        rows=cur.execute(f'SELECT ESTADO,CONTENIDO FROM {ESQUEMA_OPERACION}.REENTRENAMIENTOS WHERE CICLO_ID=%s ORDER BY ID_EVENTO',(CICLO,)).fetchall()
    prepared=leer_evento(repo,'COMPARADO')
    if prepared is None:raise ValueError('Sin reentrenamiento comparado para exportar')
    path=Path(destino);path.parent.mkdir(parents=True,exist_ok=True)
    cols=['ciclo_id','evento','estado','run_id','champion_version','challenger_version','tp_champion','tp_challenger',
          'tp_estatico','sigma_politica','elegible_promocion','decision','responsable','motivo','contenido']
    tmp=path.with_suffix('.csv.tmp')
    with tmp.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');writer.writeheader()
        for estado,contenido in rows:
            data=json.loads(contenido)
            writer.writerow({'ciclo_id':CICLO,'evento':estado,'estado':data.get('estado','PENDIENTE'),
                'run_id':prepared['run_id'],'champion_version':prepared['champion_version'],'challenger_version':prepared['challenger_version'],
                'tp_champion':prepared['modelos']['champion']['tp'],'tp_challenger':prepared['modelos']['challenger']['tp'],
                'tp_estatico':prepared['modelos']['estatico']['tp'],'sigma_politica':prepared['regla']['sigma_politica'],
                'elegible_promocion':prepared['regla']['elegible_promocion'],'decision':data.get('decision'),
                'responsable':data.get('responsable'),'motivo':data.get('motivo'),'contenido':json.dumps(data,ensure_ascii=False,separators=(',',':'))})
    tmp.replace(path);return {'eventos_exportados':len(rows),'ciclo_id':CICLO}


def solicitar_ciclo(repo,execution_id):
    import urllib.request,urllib.parse,base64
    from .datos import PLAN_DERIVA,ESQUEMA_OPERACION,ahora
    previo=leer_evento(repo,'SOLICITADO')
    if previo:return {**previo,'repeticion':True}
    dia=repo.reloj(PLAN_DERIVA)
    with repo.conn.cursor() as cur:
        rows=cur.execute(f"SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.MONITOREO WHERE PLAN_ID=%s AND LOTE_ID='L07' AND DIA_REVISION<=%s",(PLAN_DERIVA,dia)).fetchall()
    trigger=next((json.loads(r[0]) for r in rows if json.loads(r[0]).get('reentrenamiento_propuesto')),None)
    if trigger is None:return {'solicitado':False,'motivo':'sin desempeño persistente etiquetado'}
    base=os.environ.get('PSET4_KESTRA_URL','http://kestra:8080/api/v1/main')
    secret=os.environ.get('PSET4_KESTRA_PASSWORD')
    if not secret:raise ValueError('Falta autenticación de Kestra')
    auth=base64.b64encode((os.environ.get('PSET4_KESTRA_USER','admin@psets.local')+':'+secret).encode()).decode()
    def request(path,method='GET',data=None,ctype='application/json'):
        req=urllib.request.Request(base+path,method=method,data=data,headers={'Authorization':'Basic '+auth,'Content-Type':ctype})
        with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
    found=request('/executions/search?namespace=pset4.oulad&flowId=reentrenamiento&size=100')
    existing=next((v for v in found.get('results',[]) if v.get('namespace')=='pset4.oulad' and v.get('flowId')=='reentrenamiento' and v.get('inputs',{}).get('ciclo_id')==CICLO),None)
    if existing is None:
        boundary='Pset4Reentrenamiento'
        body=f'--{boundary}\r\nContent-Disposition: form-data; name="ciclo_id"\r\n\r\n{CICLO}\r\n--{boundary}--\r\n'
        existing=request('/executions/pset4.oulad/reentrenamiento','POST',body.encode(),'multipart/form-data; boundary='+boundary)
    result={'ciclo_id':CICLO,'estado':'SOLICITADO','execution_id':existing['id'],'solicitado_desde':execution_id,
            'id_disparador':trigger['id_monitoreo'],'momento':ahora(),'origen':'alerta_desempeno_persistente'}
    evento(repo,'SOLICITADO',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preparar-servicio',action='store_true')
    group.add_argument('--registrar-referencia',action='store_true')
    group.add_argument('--exportar-corridas',action='store_true')
    group.add_argument('--preparar-recursos',action='store_true')
    group.add_argument('--exportar-reentrenamientos',type=Path)
    parser.add_argument('--origen-local',type=Path)
    args=parser.parse_args()
    if args.preparar_servicio or args.preparar_recursos:
        if args.origen_local is None:parser.error('--origen-local requerido')
        result=preparar_recursos(args.origen_local) if args.preparar_recursos else preparar(args.origen_local)
        if result is not None:print(json.dumps(result,ensure_ascii=False))
    elif args.registrar_referencia:registrar_referencia()
    elif args.exportar_corridas:exportar_corridas()
    else:
        from .datos import conectar_snowflake,RepositorioSnowflake
        with conectar_snowflake() as conn:print(json.dumps(exportar_reentrenamientos(RepositorioSnowflake(conn),args.exportar_reentrenamientos)))


if __name__=='__main__':
    main()
