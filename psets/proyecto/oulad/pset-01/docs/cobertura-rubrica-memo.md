# Cobertura del memo: rúbrica y tres gaps

Revisión del 15-nov-2026. Este mapa documenta cobertura, no asigna una nota ni acredita resultados predictivos todavía no obtenidos.

## Extensión vigente

El usuario indicó expresamente que el memo puede tener hasta cinco páginas. Esa actualización prevalece sobre el límite anterior de 1-2 páginas del prompt y la rúbrica transcrita. La [rúbrica original](../rubrica.md) se conserva sin modificaciones; no se atribuye al profesor una nueva redacción. El [memo vigente](../output/pdf/PSet1_memo_Puerta_Wilmer.pdf) tiene cinco páginas y mantiene el orden de cuatro secciones: problema/métrica, viabilidad técnica, viabilidad de negocio y riesgos.

## Criterios de la rúbrica

| Criterio | Ubicación en el memo | Evidencia y límites |
|---|---|---|
| Formulación del problema y métrica de éxito | Página 1, sección 1 | Decisión, actores, población, target de tres clases, cortes; cobertura, TP y anticipación; K, umbral y error prioritario; meta relativa con baseline cero y ejemplo explícitamente hipotético |
| Viabilidad técnica | Páginas 2-3, sección 2 | Cinco fuentes, grano y acceso; datos no disponibles; preparación realmente verificada; modelos estático/longitudinal, validación temporal, etiquetas maduras, estudiantes separados, transformaciones en entrenamiento e incertidumbre |
| Viabilidad de negocio | Página 4, sección 3 | Reactiva, estática y longitudinal con igual cohorte/capacidad; presupuesto total común para cuatro cortes, repeticiones; responsables y juicio; resultados validables sin institución y apoyo solicitado |
| Riesgos | Página 5, sección 4 | R1-R4 con supuesto, gravedad, verificación y respuesta; transferencia, calidad/fuga, capacidad/impacto y equidad/confianza; correspondencia con ocho riesgos ampliados |
| Calidad profesional y coherencia | Páginas 1-5 y exportaciones | Texto autónomo, referencias, cifras observadas separadas de metas; MVP explícito en página 3; fuentes comunes con Canvas, documento ampliado y pitch; cinco páginas por instrucción vigente del usuario |

## Tres gaps acordados

| Gap | Corrección en el memo | Separación necesaria |
|---|---|---|
| 1. Objetivo de negocio calculable | Página 1: cobertura preventiva con mismos cupos, omisiones, casos por 100 revisiones y semanas potenciales; página 4: N, Fail, K y límite ideal de cobertura | Ni el margen temporal ni el +10 % son desempeño demostrado; una selección no es una tutoría realizada ni una reprobación evitada |
| 2. Proceso de comparación y viabilidad | Página 4: tres políticas con igual cohorte y K; presupuesto B común en múltiples cortes; roles, carga y límites | La reactiva puede cubrir casos después; no recibe capacidad ilimitada. El histórico conserva sus resultados y no demuestra impacto educativo |
| 3. Pitch y propuesta completos | Páginas 2-3: factibilidad, evaluación y MVP con etapas/aceptación; páginas 1 y 4: problema y beneficio esperado cuantificados y apoyo solicitado | El pitch de seis diapositivas contiene los mismos mensajes; el patrocinio respalda la evaluación, sin retorno financiero inventado |

## Límites y estado

OULAD es la única fuente del MVP. D2L/WiFi quedan fuera para una fase posterior con aprobación formal y revisión institucional LOPDP. Entrenamiento, evaluación, simulación y demostración predictiva aún deben ejecutarse; los controles del PSet 2 prueban preparación de datos. El efecto de tutorías es una hipótesis posterior, no un requisito para validar el MVP retrospectivo.

El texto íntegro del memo se controla en [propuesta-pset1.md](../propuesta-pset1.md). El [verificador](../scripts/verificar_entregables.py) comprueba todos sus fragmentos y SHA de fuente, geometría y máximo de cinco páginas; la inspección visual complementa esos controles. El [informe visual](revision-visual.json) identifica las salidas revisadas. Colab y la publicación de esta revisión en GitHub siguen pendientes.
