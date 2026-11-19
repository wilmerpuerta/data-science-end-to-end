"""Preparación reproducible del servicio con modelos existentes, sin repetir tuning.

El ciclo de reentrenamiento se incorporará después del monitoreo. Estos comandos
solo reutilizan modelos del PSet 03 y registran referencias de reproducción.
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preparar-servicio', action='store_true')
    group.add_argument('--registrar-referencia', action='store_true')
    group.add_argument('--exportar-corridas', action='store_true')
    parser.add_argument('--origen-local', type=Path)
    args = parser.parse_args()
    if args.preparar_servicio:
        if args.origen_local is None:
            parser.error('--origen-local es obligatorio para preparar las muestras')
        preparar(args.origen_local)
    elif args.registrar_referencia:
        registrar_referencia()
    else:
        exportar_corridas()
