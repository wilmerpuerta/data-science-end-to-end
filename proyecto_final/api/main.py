"""Núcleo de asignación batch. Los endpoints y la persistencia aún no se implementan.

Los manifiestos y las asignaciones previas deben proceder del almacenamiento
confiable del servicio, nunca de un cliente que pueda inventar su propia cuota.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import ceil
from .esquemas import Candidato, PoliticaCupos

CORTES_PERMITIDOS = (14, 28)
UNIDAD_CUPO = "matricula_asignatura"


def priorizar_cohorte(candidatos, *, cohorte_base, elegibles_actuales,
                     seleccionados_previos, corte_dias, politica=PoliticaCupos()):
    """Una capacidad por edición para ambas rondas, sin repetir matrícula.

    cohorte_base y elegibles_actuales: mapas matrícula -> edición, obtenidos de
    la cohorte completa del día 14 y de la elegibilidad al corte actual.
    seleccionados_previos: mapa persistido de propuestas, incluso si después
    cambia la elegibilidad. No hay reembolso automático de un cupo propuesto.
    """
    if corte_dias not in CORTES_PERMITIDOS:
        raise ValueError('Solo están habilitadas las semanas 2 y 4')
    if not cohorte_base or any(not isinstance(k, str) or not k or not isinstance(v, str) or not v for k, v in cohorte_base.items()):
        raise ValueError('Se requiere un manifiesto de cohorte base válido')
    for mapping in [elegibles_actuales, seleccionados_previos]:
        if any(k not in cohorte_base or cohorte_base[k] != v for k, v in mapping.items()):
            raise ValueError('Matrícula o edición fuera de la cohorte base')
    if corte_dias == 14 and (dict(elegibles_actuales) != dict(cohorte_base) or seleccionados_previos):
        raise ValueError('La primera ronda requiere la cohorte inicial y ninguna asignación previa')
    claves = [c.matricula for c in candidatos]
    if len(claves) != len(set(claves)) or set(claves) != set(elegibles_actuales):
        raise ValueError('Lote incompleto, duplicado o con matrículas adicionales')
    if any(c.edicion != elegibles_actuales[c.matricula] for c in candidatos):
        raise ValueError('La edición no coincide con el manifiesto')
    counts = Counter(cohorte_base.values())
    pasados = Counter(seleccionados_previos.values())
    presupuestos = {e: int(n * politica.capacidad) for e, n in sorted(counts.items())}
    topes_tempranos = {e: int(k * politica.fraccion_semana2) for e, k in presupuestos.items()}
    if any(pasados[e] > topes_tempranos[e] for e in pasados):
        raise ValueError('Las propuestas anteriores exceden el cupo de semana 2')
    nuevos = set()
    registros = []
    for edicion, total in presupuestos.items():
        tope = topes_tempranos[edicion] if corte_dias == 14 else total
        disponibles = max(0, tope - pasados[edicion])
        lista = sorted((c for c in candidatos if c.edicion == edicion), key=lambda c: (-c.riesgo_fail, c.matricula))
        elegibles = [c for c in lista if c.matricula not in seleccionados_previos]
        elegidos = elegibles[:disponibles]
        nuevos.update(c.matricula for c in elegidos)
        registros.append({'edicion': edicion, 'poblacion_base': counts[edicion], 'presupuesto_total': total,
                          'tope_acumulado_ronda': tope, 'propuestas_previas': pasados[edicion],
                          'propuestas_nuevas': len(elegidos), 'saldo_total': total - pasados[edicion] - len(elegidos)})
    filas = []
    ranking = Counter()
    for c in sorted(candidatos, key=lambda c: (c.edicion, -c.riesgo_fail, c.matricula)):
        ranking[c.edicion] += 1
        previa = c.matricula in seleccionados_previos
        nueva = c.matricula in nuevos
        filas.append({'matricula': c.matricula, 'edicion': c.edicion, 'persona': c.persona,
                      'riesgo_fail': float(c.riesgo_fail), 'posicion_en_edicion': ranking[c.edicion],
                      'decision': 'tutoria_ya_propuesta' if previa else ('proponer_tutoria' if nueva else 'seguimiento'),
                      'accion': 'revision_humana_de_apoyo_preventivo' if previa or nueva else 'mantener_seguimiento',
                      'consume_cupo_nuevo': nueva})
    identity = hashlib.sha256(json.dumps(dict(cohorte_base), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'politica_version': politica.version, 'cohorte_base_sha256': identity, 'corte_dias': corte_dias,
            'unidad': UNIDAD_CUPO, 'presupuestos': registros, 'predicciones': filas,
            'nuevas_propuestas': len(nuevos),
            'personas_unicas_en_nuevas_propuestas': len({c.persona for c in candidatos if c.matricula in nuevos})}


def evaluar_meta(tp_estatico, tp_longitudinal, fail_totales, cupos, mejora_minima=Fraction(1, 10)):
    """Objetivo +10% relativo en cobertura con un mismo denominador y cupo."""
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in [tp_estatico, tp_longitudinal, fail_totales, cupos]):
        raise ValueError('Los conteos deben ser enteros no negativos')
    if not isinstance(mejora_minima, Fraction) or mejora_minima < 0:
        raise ValueError('La mejora mínima debe ser una fracción exacta no negativa')
    if max(tp_estatico, tp_longitudinal) > min(fail_totales, cupos):
        raise ValueError('Los TP no pueden exceder el número de Fail ni el cupo')
    definible = fail_totales > 0 and tp_estatico > 0
    requeridos = ceil(tp_estatico * (1 + mejora_minima)) if definible else None
    return {'tp_estatico': tp_estatico, 'tp_longitudinal': tp_longitudinal,
            'tp_adicionales_netos': tp_longitudinal - tp_estatico,
            'cobertura_estatica': tp_estatico / fail_totales if fail_totales else None,
            'cobertura_longitudinal': tp_longitudinal / fail_totales if fail_totales else None,
            'mejora_relativa': tp_longitudinal / tp_estatico - 1 if definible else None,
            'tp_minimos_para_meta': requeridos,
            'cumple_meta': tp_longitudinal >= requeridos if definible else None,
            'estado': 'evaluable' if definible else 'razon_no_definida',
            'cupos_comunes': cupos, 'fail_evitados_observados': None}
