"""Tipos del núcleo de priorización; el contrato HTTP se incorporará con la API."""
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
