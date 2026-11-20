"""Tipos del núcleo de cupos y contrato Pydantic del servicio batch."""
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from numbers import Real

@dataclass(frozen=True)
class PoliticaCupos:
    version: str = 'preventiva-prototipo-0.1'
    capacidad: Fraction = Fraction(1, 10)
    fraccion_semana2: Fraction = Fraction(1, 4)

    def __post_init__(self):
        if not self.version or not isinstance(self.capacidad, Fraction) or not 0 < self.capacidad <= 1:
            raise ValueError('La capacidad debe ser una fracción exacta entre 0 y 1')
        if not isinstance(self.fraccion_semana2, Fraction) or not 0 <= self.fraccion_semana2 <= 1:
            raise ValueError('El reparto debe ser una fracción exacta entre 0 y 1')

@dataclass(frozen=True)
class Candidato:
    matricula: str
    edicion: str
    persona: str
    riesgo_fail: float

    def __post_init__(self):
        identificadores = [self.matricula, self.edicion, self.persona]
        if any(not isinstance(valor, str) or not valor.strip() for valor in identificadores):
            raise ValueError('Matrícula, edición y persona son identificadores obligatorios')
        if (
            isinstance(self.riesgo_fail, bool)
            or not isinstance(self.riesgo_fail, Real)
            or not isfinite(self.riesgo_fail)
            or not 0 <= self.riesgo_fail <= 1
        ):
            raise ValueError('El riesgo debe ser una probabilidad finita')


# Contrato HTTP: los identificadores son metadatos; el modelo recibe solo features.
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictStr, field_validator, model_validator

Numero = Annotated[StrictFloat, Field(allow_inf_nan=False)]
NoNegativo = Annotated[StrictFloat, Field(ge=0, allow_inf_nan=False)]
Identificador = Annotated[StrictStr, Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9._:-]+$')]
EdicionGold = Annotated[StrictStr, Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9._:|\-]+$')]


class Features(BaseModel):
    model_config = ConfigDict(extra='forbid')
    num_of_prev_attempts: NoNegativo | None
    studied_credits: NoNegativo | None
    module_presentation_length: Annotated[StrictFloat, Field(gt=0, allow_inf_nan=False)]
    registration_days_before_start: Numero | None
    is_imd_missing: Annotated[StrictFloat, Field(ge=0, le=1)]
    clicks_through_cutoff: NoNegativo | None
    active_days_through_cutoff: NoNegativo | None
    resources_through_cutoff: NoNegativo | None
    clicks_current_14d: NoNegativo | None
    active_days_current_14d: Annotated[StrictFloat, Field(ge=0, le=14, allow_inf_nan=False)] | None
    clicks_previous_14d: NoNegativo | None = None
    click_change_14d: Numero | None = None
    recency_days: NoNegativo | None
    has_recorded_activity: Annotated[StrictFloat, Field(ge=0, le=1)]
    gender: StrictStr | None
    region: StrictStr | None
    highest_education: StrictStr | None
    imd_band: StrictStr | None
    age_band: StrictStr | None
    disability: StrictStr | None

    @field_validator('is_imd_missing', 'has_recorded_activity')
    @classmethod
    def binario(cls, value):
        if value not in (0., 1.):
            raise ValueError('La bandera debe ser 0 o 1')
        return value

    @model_validator(mode='after')
    def coherencia(self):
        if self.is_imd_missing != float(self.imd_band is None):
            raise ValueError('is_imd_missing debe coincidir con la ausencia de imd_band')
        if self.clicks_current_14d is not None and self.clicks_through_cutoff is not None and self.clicks_current_14d > self.clicks_through_cutoff:
            raise ValueError('clicks_current_14d no puede exceder clicks_through_cutoff')
        if self.has_recorded_activity == 0 and self.recency_days is not None:
            raise ValueError('recency_days debe ser null sin actividad registrada')
        return self


class MatriculaEntrada(BaseModel):
    model_config = ConfigDict(extra='forbid')
    matricula: Identificador
    edicion: EdicionGold
    persona: Identificador
    features: Features


class SolicitudLote(BaseModel):
    model_config = ConfigDict(extra='forbid')
    cohorte_id: Identificador
    corte_dias: Literal[14, 28]
    matriculas: list[MatriculaEntrada] = Field(min_length=1, max_length=50000)

    @model_validator(mode='after')
    def corte_compatible(self):
        for fila in self.matriculas:
            if fila.features.module_presentation_length <= self.corte_dias:
                raise ValueError('El corte debe preceder al fin del período')
            if self.corte_dias == 28:
                for campo in ['clicks_previous_14d', 'click_change_14d']:
                    if campo not in fila.features.model_fields_set:
                        raise ValueError(f'Falta el campo requerido en día 28: {campo}')
        return self


# La política se comparte entre inferencia y evaluación del ciclo de vida.
from collections import Counter
from math import ceil
import hashlib
import json

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
