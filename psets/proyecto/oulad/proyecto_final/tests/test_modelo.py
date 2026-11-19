"""Reproducción de modelos exportados y referencias; sin servicios externos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
import mlflow.sklearn
import mlflow.pyfunc
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits
from api.esquemas import Features
from src.datos import sha256
from src.pipeline import CATEGORICAS

FIXTURES = Path(__file__).parent / 'fixtures'
REF = json.loads((FIXTURES/'referencia.json').read_text())


@pytest.mark.parametrize('corte', [14, 28])
def test_fixture_reproduce_probabilidades_y_metrica(corte, monkeypatch):
    monkeypatch.setenv('MLFLOW_TRACKING_URI', 'http://127.0.0.1:1')
    sample = json.loads((FIXTURES/f'muestra_semana{corte//7}.json').read_text())
    x = pd.DataFrame([r['features'] for r in sample['rows']])
    for name in x:
        x[name] = x[name].astype(object).where(x[name].notna(), np.nan) if name in CATEGORICAS else x[name].astype(float)
    model = mlflow.sklearn.load_model(str(FIXTURES/f'semana{corte//7}'))
    with threadpool_limits(limits=2):p = model.predict_proba(x)[:,list(model.classes_).index('Fail')]
    assert np.allclose(p,sample['expected_p_fail'],rtol=0,atol=REF['tolerance'])
    ap = average_precision_score(np.asarray([r['target'] for r in sample['rows']])=='Fail',p)
    assert abs(ap-REF['modelos'][str(corte)]['ci_ap_fail']) <= REF['tolerance']
    assert 'development' in sample['scope']
    pyfunc = mlflow.pyfunc.load_model(str(FIXTURES/f'semana{corte//7}'))
    with threadpool_limits(limits=2):
        probabilities = pyfunc.predict(x)
    assert probabilities.shape == (len(x), 3)
    names={f['name'] for f in json.loads(REF['modelos'][str(corte)]['signature']['inputs'])}
    assert names==set(Features.model_fields)


def test_hashes_preparacion_y_fixtures():
    assert sha256(FIXTURES.parents[1]/'src/pipeline.py')==REF['pipeline_sha256']
    for name,expected in REF['files_sha256'].items():assert sha256(FIXTURES/name)==expected


def test_baseline_original_corresponde_a_regla_de_respaldo():
    model=mlflow.sklearn.load_model(str(FIXTURES/'baseline'))
    sample=json.loads((FIXTURES/'muestra_semana2.json').read_text())
    x=pd.DataFrame([r['features'] for r in sample['rows']])
    for name in CATEGORICAS:x[name]=x[name].astype(object).where(x[name].notna(),np.nan)
    with threadpool_limits(limits=2):p=model.predict_proba(x)[:,list(model.classes_).index('Fail')]
    assert np.all(p==REF['baseline']['probabilidad_fail'])
    assert model.named_steps['modelo'].strategy=='most_frequent'
