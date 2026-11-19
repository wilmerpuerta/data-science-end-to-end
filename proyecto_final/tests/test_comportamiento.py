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
