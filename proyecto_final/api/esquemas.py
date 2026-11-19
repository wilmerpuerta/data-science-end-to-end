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
