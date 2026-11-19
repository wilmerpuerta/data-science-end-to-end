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
