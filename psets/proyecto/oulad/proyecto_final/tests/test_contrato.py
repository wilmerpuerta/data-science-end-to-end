"""Contrato HTTP, respaldo y persistencia; fixtures locales y cohortes sintéticas."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient
from api.main import crear_app

FIXTURES = Path(__file__).parent / 'fixtures'


def datos(corte=14, n=40):
    sample = json.loads((FIXTURES / f'muestra_semana{corte // 7}.json').read_text())['rows'][0]['features']
    rows = [{'matricula': f'M{i:03}', 'edicion': 'AAA-2014J', 'persona': f'P{i:03}', 'features': deepcopy(sample)} for i in range(n)]
    return {'cohorte_id': 'cohorte-ci', 'corte_dias': corte, 'matriculas': rows}


def registrar(app, n=40):
    base = {f'M{i:03}': 'AAA-2014J' for i in range(n)}
    app.state.almacen.registrar_cohorte({'cohorte_id': 'cohorte-ci', 'base': base,
        'elegibles': {'14': base, '28': base}, 'personas': {f'M{i:03}': f'P{i:03}' for i in range(n)}})


@pytest.fixture
def servicio(tmp_path):
    app = crear_app(ruta_db=tmp_path / 'operacion.sqlite', modo='fixture', forzar_respaldo=False)
    registrar(app)
    with TestClient(app) as client:
        yield app, client


def test_salud_y_modelo_trazable(servicio):
    _, client = servicio
    assert client.get('/salud').json()['modelo_cargado'] is True
    for corte in [14, 28]:
        meta = client.get('/modelo', params={'corte_dias': corte}).json()['modelos'][0]
        assert meta['cutoff_day'] == corte
        assert meta['alias'] == 'champion' and meta['version'] == '1'
        assert meta['run_id'] and meta['snapshot_id'] and not meta['respaldo']


def test_lote_valido_persiste_y_aplica_cupo(servicio):
    app, client = servicio
    response = client.post('/predecir', json=datos())
    assert response.status_code == 200
    body = response.json()
    assert body['nuevas_propuestas'] == 1 and len(body['predicciones']) == 40
    assert len({r['id_prediccion'] for r in body['predicciones']}) == 40
    assert not body['respaldo']
    with app.state.almacen.conexion() as db:
        rows = db.execute('SELECT * FROM predicciones').fetchall()
    assert len(rows) == 40
    for row in rows:
        assert json.loads(row['entradas'])['gender']
        assert json.loads(row['modelo'])['run_id'] == body['modelo']['run_id']
        assert row['latencia_ms'] > 0 and row['momento']
    assert client.get('/metricas').json()['solicitudes'] == 1


@pytest.mark.parametrize('mutacion,campo', [('faltante','studied_credits'), ('tipo','clicks_current_14d'), ('categoria','region'), ('etiqueta','target_class'), ('rango','active_days_current_14d')])
def test_entradas_invalidas_son_422(servicio, mutacion, campo):
    app, client = servicio
    payload = datos(); features = payload['matriculas'][0]['features']
    if mutacion == 'faltante': features.pop(campo)
    if mutacion == 'tipo': features[campo] = '12'
    if mutacion == 'categoria': features[campo] = 'REGION_INEXISTENTE'
    if mutacion == 'etiqueta': features[campo] = 'Fail'
    if mutacion == 'rango': features[campo] = 15
    response = client.post('/predecir', json=payload)
    assert response.status_code == 422
    assert campo in response.text
    assert app.state.almacen.metricas()['predicciones_registradas'] == 0
    assert app.state.almacen.metricas()['errores_4xx'] == 1


def test_nan_invalido_no_se_convierte_en_error_500(servicio):
    _, client = servicio
    payload = datos();payload['matriculas'][0]['features']['studied_credits'] = float('nan')
    response = client.post('/predecir', content=json.dumps(payload), headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert 'studied_credits' in response.text


def test_repeticion_y_orden_conservan_ids_y_no_repuntuan(servicio, monkeypatch):
    app, client = servicio
    first = client.post('/predecir', json=datos()).json()
    monkeypatch.setattr(app.state.proveedor, 'obtener', lambda _: (_ for _ in ()).throw(AssertionError('No debe volver a puntuar')))
    assert client.get('/salud').json()['modelo_cargado'] is True
    payload = datos();payload['matriculas'].reverse()
    second = client.post('/predecir', json=payload)
    assert second.status_code == 200 and second.json() == first
    assert app.state.almacen.metricas()['predicciones_registradas'] == 40


def test_no_se_reasigna_un_lote_distinto(servicio):
    _, client = servicio
    assert client.post('/predecir', json=datos()).status_code == 200
    payload = datos();payload['matriculas'][0]['features']['num_of_prev_attempts'] = 9
    assert client.post('/predecir', json=payload).status_code == 409


def test_rondas_comparten_cupo_y_requieren_orden(servicio):
    _, client = servicio
    assert client.post('/predecir', json=datos(28)).status_code == 409
    first = client.post('/predecir', json=datos()).json()
    second_response = client.post('/predecir', json=datos(28))
    assert second_response.status_code == 200
    second = second_response.json()
    assert first['nuevas_propuestas'] == 1 and second['nuevas_propuestas'] == 3
    a = {r['matricula'] for r in first['predicciones'] if r['consume_cupo_nuevo']}
    b = {r['matricula'] for r in second['predicciones'] if r['consume_cupo_nuevo']}
    assert not a & b and len(a | b) == 4


def test_fragmentos_y_cohortes_inventadas_no_obtienen_cupos(servicio):
    _, client = servicio
    payload = datos();payload['matriculas'] = payload['matriculas'][:20]
    assert client.post('/predecir', json=payload).status_code == 422
    payload = datos();payload['cohorte_id'] = 'inventada'
    assert client.post('/predecir', json=payload).status_code == 404


def test_dos_peticiones_concurrentes_no_duplican_presupuesto(servicio):
    app, client = servicio
    with ThreadPoolExecutor(max_workers=2) as pool:
        respuestas = list(pool.map(lambda _: client.post('/predecir', json=datos()), range(2)))
    assert all(r.status_code == 200 for r in respuestas)
    assert respuestas[0].json() == respuestas[1].json()
    assert app.state.almacen.metricas()['predicciones_registradas'] == 40


@pytest.mark.parametrize('origen', ['fallo_carga', 'interruptor'])
def test_respaldo_real_del_pset3(tmp_path, monkeypatch, origen):
    if origen == 'fallo_carga':
        import mlflow.sklearn
        monkeypatch.setattr(mlflow.sklearn, 'load_model', lambda *_: (_ for _ in ()).throw(OSError('fallo_simulado')))
    else:
        monkeypatch.setenv('PSET4_FORCE_FALLBACK', '1')
    app = crear_app(ruta_db=tmp_path/'fallback.sqlite', modo='fixture', forzar_respaldo=None)
    registrar(app)
    with TestClient(app) as client:
        assert client.get('/salud').json()['modelo_cargado'] is False
        response = client.post('/predecir', json=datos())
    assert response.status_code == 200
    body = response.json()
    assert body['respaldo'] is True and body['modelo']['nombre'] == 'dummy-pset3'
    assert all(r['riesgo_fail'] == 0 and r['respaldo'] for r in body['predicciones'])
    assert body['modelo']['run_id'] == 'dcb91965644a479baa7a0f08555df32e'


def test_un_nombre_nuevo_no_renueva_el_presupuesto(servicio):
    app, _ = servicio
    base = {f'M{i:03}': 'AAA-2014J' for i in range(40)}
    with pytest.raises(ValueError, match='presupuesto nuevo'):
        app.state.almacen.registrar_cohorte({'cohorte_id': 'otra', 'base': base,
            'elegibles': {'14': base, '28': base}, 'personas': {f'M{i:03}': f'P{i:03}' for i in range(40)}})
