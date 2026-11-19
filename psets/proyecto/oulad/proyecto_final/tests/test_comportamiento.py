"""Invariantes de cupos compartidos y del objetivo de negocio; datos sintéticos."""
from fractions import Fraction
import pytest
from api.main import priorizar_cohorte, evaluar_meta
from api.esquemas import Candidato, PoliticaCupos


def cohorte(n=40, edicion='A'):
    filas = [Candidato(f'{edicion}-{i:03}', edicion, f'P-{i:03}', (n-i)/n) for i in range(n)]
    return filas, {f.matricula: f.edicion for f in filas}


def run(filas, base, corte=14, prev=None, elegibles=None, politica=PoliticaCupos()):
    return priorizar_cohorte(filas, cohorte_base=base, elegibles_actuales=base if elegibles is None else elegibles,
                            seleccionados_previos={} if prev is None else prev,
                            corte_dias=corte, politica=politica)


def elegidos(result):
    return {r['matricula']: r['edicion'] for r in result['predicciones'] if r['consume_cupo_nuevo']}


def test_orden_y_empates_no_alteran_asignacion():
    rows, base = cohorte()
    ties = [Candidato(x.matricula, x.edicion, x.persona, .5) for x in rows]
    a = run(ties, base); b = run(list(reversed(ties)), base)
    assert a == b
    assert list(elegidos(a)) == ['A-000']


def test_dos_rondas_comparten_un_presupuesto_y_no_repiten():
    rows, base = cohorte(); first = run(rows, base); prev = elegidos(first)
    second = run(rows, base, 28, prev)
    assert len(prev) == 1 and second['nuevas_propuestas'] == 3
    assert not set(prev) & set(elegidos(second))
    assert sum(p['saldo_total'] for p in second['presupuestos']) == 0
    assert next(x for x in second['predicciones'] if x['matricula'] in prev)['decision'] == 'tutoria_ya_propuesta'


def test_propuesta_previa_consume_cupo_aunque_desaparezca_de_elegibles():
    rows, base = cohorte(); prev = elegidos(run(rows, base)); current = [x for x in rows if x.matricula not in prev]
    result = run(current, base, 28, prev, {x.matricula: x.edicion for x in current})
    assert result['nuevas_propuestas'] == 3
    assert result['presupuestos'][0]['propuestas_previas'] == 1


def test_fragmento_de_lote_no_obtiene_cupo_propio():
    rows, base = cohorte()
    with pytest.raises(ValueError, match='Lote incompleto'):
        run(rows[:20], base)


def test_duplicados_y_ediciones_inventadas_rechazados():
    rows, base = cohorte()
    with pytest.raises(ValueError, match='duplicado'):
        run(rows + rows[:1], base)
    with pytest.raises(ValueError, match='edición'):
        run([Candidato(rows[0].matricula, 'OTRA', rows[0].persona, .99), *rows[1:]], base)


def test_presupuesto_no_se_transfiere_entre_ediciones():
    a, ma = cohorte(19, 'A'); b, mb = cohorte(21, 'B')
    result = run(a+b, ma|mb, politica=PoliticaCupos(fraccion_semana2=Fraction(1)))
    assert {p['edicion']: p['presupuesto_total'] for p in result['presupuestos']} == {'A': 1, 'B': 2}


def test_personas_unicas_no_se_confunden_con_matriculas():
    rows, base = cohorte()
    rows = [Candidato(x.matricula, x.edicion, 'MISMA', x.riesgo_fail) for x in rows]
    result = run(rows, base, politica=PoliticaCupos(fraccion_semana2=Fraction(1)))
    assert result['nuevas_propuestas'] == 4
    assert result['personas_unicas_en_nuevas_propuestas'] == 1


def test_diez_por_ciento_es_relativo_y_redondea_sin_error_binario():
    result = evaluar_meta(100, 110, 500, 200)
    assert result['tp_minimos_para_meta'] == 110
    assert result['cumple_meta'] is True
    assert result['cobertura_longitudinal'] == .22
    assert result['tp_adicionales_netos'] == 10
    assert result['fail_evitados_observados'] is None
    assert evaluar_meta(100, 109, 500, 200)['cumple_meta'] is False


def test_base_cero_no_certifica_una_mejora_relativa():
    assert evaluar_meta(0, 3, 50, 10)['cumple_meta'] is None
    assert evaluar_meta(0, 0, 0, 10)['mejora_relativa'] is None


@pytest.mark.parametrize('risk', [float('nan'), float('inf'), -.01, 1.01, True])
def test_scores_invalidos_rechazados(risk):
    with pytest.raises(ValueError):
        Candidato('M', 'E', 'P', risk)


def test_corte_distinto_y_cupos_anteriores_inconsistentes_rechazados():
    rows, base = cohorte()
    with pytest.raises(ValueError):
        run(rows, base, corte=56)
    with pytest.raises(ValueError, match='exceden'):
        run(rows, base, corte=28, prev={x.matricula: x.edicion for x in rows[:3]})

# El reloj y la construcción de lotes se verifican sin servicios externos.
def fuente_operativa():
    import json
    from src.datos import ROOT
    features = json.loads((ROOT/'tests/fixtures/muestra_semana4.json').read_text())['rows'][0]['features']
    return [{**features, 'enrollment_key': f'{module}-M{i}', 'id_student': i,
             'edition_key': f'{module}|2014J', 'code_module': module, 'code_presentation': '2014J', 'cutoff_day': cut}
            for module in ['AAA','BBB','CCC','DDD','EEE','FFF','GGG'] for cut in [14,28] for i in range(12 if cut==14 else 11)]


def test_lotes_conservan_ediciones_completas_y_son_deterministas():
    from src.datos import construir_lotes
    rows = fuente_operativa(); lotes = construir_lotes(rows)
    assert lotes == construir_lotes(list(reversed(rows)))
    assert [l['dia'] for l in lotes] == [14,15,16,17,28,29,30,31]
    assert len(lotes) == 8
    for a,b in zip(lotes[:4],lotes[4:]):
        assert a['manifiesto'] == b['manifiesto']
        assert set(b['manifiesto']['elegibles']['28']) < set(a['manifiesto']['base'])
        assert all(sum(r['edicion']==edition for r in a['solicitud']['matriculas'])==12 for edition in set(a['manifiesto']['base'].values()))
    assert sum(len(l['solicitud']['matriculas']) for l in lotes)==len(rows)
    assert len({m for l in lotes[:4] for m in l['manifiesto']['base']})==84


def test_fuente_operativa_rechaza_target_duplicados_y_nuevas_matriculas():
    from src.datos import construir_lotes
    rows=fuente_operativa()
    with pytest.raises(ValueError): construir_lotes([{**r,'target_class':'Fail'} for r in rows])
    with pytest.raises(ValueError): construir_lotes(rows+[rows[0]])
    extra={**rows[-1], 'enrollment_key':'nueva-solo-dia28'}
    with pytest.raises(ValueError): construir_lotes(rows+[extra])


def test_lote_fuera_de_orden_no_llama_api_ni_avanza_reloj():
    from src.datos import construir_lotes,procesar_lote
    class Repo:
        def contenido(self,tabla,plan,lote):
            return construir_lotes(fuente_operativa())[1] if tabla=='LOTES_ENTRADA' else None
        def reloj(self,*args):raise AssertionError('No se debe avanzar')
    with pytest.raises(ValueError,match='precedente'): procesar_lote(Repo(),None,'L02','http://no-usar')


def test_repeticion_conciliada_no_repuntua_ni_consume_cupo():
    from src.datos import procesar_lote
    class Repo:
        def contenido(self,*args):return {'predicciones':12,'nuevas_propuestas':1}
    result=procesar_lote(Repo(),None,'L01','http://no-usar')
    assert result=={'predicciones':12,'nuevas_propuestas':1,'repeticion':True}


def test_etiquetas_inmaduras_no_consultan_gold():
    from src.datos import construir_lotes,liberar_etiquetas
    lotes=construir_lotes(fuente_operativa())
    class Repo:
        def contenido(self,tabla,plan,lote=None):
            if tabla=='PLANES':return {'lotes':lotes}
            if tabla=='LOTES_PROCESADOS':return {'status':'ok'}
            return next(l for l in lotes if l['lote_id']==lote)
        def reloj(self,plan,dia):assert dia==31
        @property
        def conn(self):raise AssertionError('No consultar targets inmaduros')
    result=liberar_etiquetas(Repo(),31)
    assert result['etiquetas']==0 and result['fuente_target_consultada'] is False


def test_etiquetas_no_se_liberan_con_predicciones_pendientes():
    from src.datos import liberar_etiquetas
    class Repo:
        def contenido(self,tabla,*args):return {'lotes':[{'lote_id':'L01'}]} if tabla=='PLANES' else None
        def reloj(self,*args):raise AssertionError('Reloj aún no debe avanzar')
    with pytest.raises(ValueError,match='Completar predicciones'): liberar_etiquetas(Repo(),283)


def test_lotes_admiten_claves_gold_y_contrato_sin_target():
    from src.datos import construir_lotes
    from api.esquemas import SolicitudLote
    for lote in construir_lotes(fuente_operativa()):
        contrato=SolicitudLote.model_validate(lote['solicitud'])
        assert all('|' in r.edicion for r in contrato.matriculas)
        assert all('target_class' not in r.features.model_dump() for r in contrato.matriculas)


def test_separador_gold_se_admite_solo_en_edicion():
    from src.datos import construir_lotes
    from api.esquemas import SolicitudLote
    import copy
    payload=construir_lotes(fuente_operativa())[0]['solicitud']
    for campo in ['cohorte_id','matricula','persona']:
        altered=copy.deepcopy(payload)
        if campo=='cohorte_id':altered[campo]='cohorte|con|separadores'
        else:altered['matriculas'][0][campo]='identificador|ambiguo'
        with pytest.raises(ValueError):SolicitudLote.model_validate(altered)


def test_psi_es_finito_con_ceros_y_detecta_desplazamiento():
    from monitoreo.deriva import psi
    import math
    assert psi([100,0,20],[100,0,20])==0
    assert math.isfinite(psi([100,0],[0,100]))
    assert psi([100,0],[0,100])>.25


def test_psi_binario_y_nueva_categoria_no_se_confunden_con_nulos():
    import pandas as pd
    from monitoreo.deriva import perfil_entrenamiento,calidad_y_deriva
    train=pd.DataFrame({'is_imd_missing':[0.]*200+[1.]*200,'region':['A']*400})
    test=pd.DataFrame({'is_imd_missing':[1.]*400,'region':['NUEVA']*399+[None]})
    r=calidad_y_deriva(test,perfil_entrenamiento(train,list(train)))
    assert r['is_imd_missing']['psi']>.25
    assert r['region']['categorias_nuevas']==399/400
    assert r['region']['faltantes']==1/400


def metricas_alertas(caida=False,cambio=False,completas=True,lote='L06',corte=28,dia=283):
    return {'lote_id':lote,'corte':corte,'dia_revision':dia,'dia_prediccion':29,'n':400,
        'etiquetas_completas':completas,'caida_ap':caida,'ap_fail':.2 if caida else .6,'umbral_ap':.4,
        'datos':{'studied_credits':{'psi':.8 if cambio else 0,'fuera_contrato':0,'categorias_nuevas':0}},
        'sistema':{'solicitudes_atribuidas':1}}


def test_cambio_sin_caida_no_propone_reentrenar_y_pendientes_tampoco():
    from monitoreo.alertas import evaluar_alertas,diagnostico
    alerts,trigger=evaluar_alertas(metricas_alertas(cambio=True))
    assert alerts and not trigger
    assert diagnostico(True,False,True)[0]=='datos_sin_impacto'
    pending=metricas_alertas(cambio=True,completas=False)
    alerts,trigger=evaluar_alertas(pending,[metricas_alertas(caida=True,lote='L05')])
    assert not trigger and not any(a['tipo']=='desempeno' for a in alerts)


def test_dos_caidas_mismo_corte_proponen_revision_sin_promover():
    from monitoreo.alertas import evaluar_alertas
    old=metricas_alertas(caida=True,lote='L06');old['dia_prediccion']=29
    current=metricas_alertas(caida=True,cambio=True,lote='L07');current['dia_prediccion']=30
    alerts,trigger=evaluar_alertas(current,[old])
    assert trigger and any(a['tipo']=='reentrenamiento_propuesto' for a in alerts)
    old['corte']=14
    assert evaluar_alertas(current,[old])[1] is False
    old['corte']=28;old['dia_revision']=284
    assert evaluar_alertas(current,[old])[1] is False


def test_referencia_monitoreo_tiene_identidad_y_cv_historica():
    from monitoreo.deriva import REFERENCIA
    from src.datos import identidad,ROOT
    import json
    ref=json.loads(REFERENCIA.read_text());native=json.loads((ROOT/'tests/fixtures/referencia.json').read_text())
    assert identidad({k:v for k,v in ref.items() if k!='id'})==ref['id']
    assert ref['snapshot_id']==native['modelos']['14']['snapshot_id']
    for cut,info in ref['cortes'].items():
        assert info['global']['cv_ap_mean']==pytest.approx(native['modelos'][cut]['cv_ap_fail_mean'])
        assert len(info['ondas'])==4


def test_induccion_preserva_control_targets_y_presupuesto():
    from src.datos import construir_lotes,preparar_plan,PLAN_CONTROL,PLAN_DERIVA,identidad
    import copy
    originals=construir_lotes(fuente_operativa());before=identidad(originals)
    class Repo:
        def __init__(self):self.data={}
        def contenido(self,tabla,plan,lote=None):
            if plan==PLAN_CONTROL:
                if tabla=='PLANES':return {'lotes':originals,'matriculas_corte':sum(len(l['solicitud']['matriculas']) for l in originals)}
                return next(l for l in originals if l['lote_id']==lote)
            return self.data.get((tabla,plan,lote))
        def insertar(self,tabla,rows):
            for r in rows:self.data[(tabla,r['PLAN_ID'],r.get('LOTE_ID'))]=copy.deepcopy(r['CONTENIDO'])
    repo=Repo();preparar_plan(repo,PLAN_DERIVA)
    assert identidad(originals)==before
    for original in originals:
        changed=repo.contenido('LOTES_ENTRADA',PLAN_DERIVA,original['lote_id'])
        assert changed['manifiesto']['base']==original['manifiesto']['base']
        assert changed['fuentes']==original['fuentes']
        for a,b in zip(original['solicitud']['matriculas'],changed['solicitud']['matriculas']):
            assert 'target_class' not in b['features']
            if changed['alterado']:assert b['features']['studied_credits']==a['features']['studied_credits']+120
            else:assert a['features']==b['features']


def test_migracion_de_telemetria_preserva_registros_historicos(tmp_path):
    import sqlite3
    from src.datos import Almacen
    path=tmp_path/'old.sqlite'
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE peticiones(id INTEGER PRIMARY KEY,momento TEXT,codigo INTEGER,latencia_ms REAL)')
        db.execute("INSERT INTO peticiones VALUES(1,'2026-01-01',422,3.)")
    almacen=Almacen(path);almacen.registrar_peticion(200,10.,'plan','L01','ejecucion')
    with almacen.conexion() as db:
        rows=db.execute('SELECT codigo,plan_id FROM peticiones ORDER BY id').fetchall()
    assert [tuple(r) for r in rows]==[(422,None),(200,'plan')]
