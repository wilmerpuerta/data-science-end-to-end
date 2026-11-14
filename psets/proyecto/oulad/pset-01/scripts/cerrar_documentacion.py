from generar_contenidos import ROOT,write
from importlib.metadata import distributions
def main():
 write('pset-01/scripts/requirements.txt','\n'.join(sorted(f'{d.metadata["Name"]}=={d.version}' for d in distributions())))
 write('README.md','''# Apoyo académico a tiempo con OULAD

Wilmer Puerta · Proyecto académico de ciencia de datos · 12-nov-2026.

Evaluar si la actividad digital longitudinal permite detectar más futuras reprobaciones con los mismos cupos de revisión preventiva. Universidad hipotética, sin socio institucional comprometido. El proyecto distingue predicción, focalización retrospectiva e impacto educativo posterior.

## Etapas y estructura

```text
psets/
├── datasets/       originales compartidos y manifiesto
├── pset-01/        propuesta revisada, auditoría y exportaciones
├── pset-02/        documentación de continuidad del pipeline
├── pset-03/        alcance pendiente de enunciado
└── pset-04/        alcance pendiente de enunciado
```

- [PSet 1: propuesta y entregables](pset-01/README.md).
- [PSet 2: plan de pipeline](pset-02/README.md).
- [Datos compartidos y reproducción](datasets/README.md).

Las cuatro carpetas organizan etapas del mismo proyecto. La rúbrica del profesor menciona cinco PSets del curso; se conserva su texto y ponderación sin inventar una quinta etapa o requisitos de las etapas 3 y 4.

## Qué leer y estado real

Leer primero la [propuesta](pset-01/propuesta-pset1.md), el [Canvas](pset-01/canvas-wilmer-puerta.md), el [proyecto completo](pset-01/proyecto-completo-pset1.md) y la [guía del pitch](pset-01/pset01-presentacion.md).

PSet 1: fuentes Markdown, notebook válido, memo PDF de dos páginas, PDF completo y pitch nativo de seis diapositivas en PPTX y PPT real. Auditoría ejecutada sobre cinco CSV: 32.593 matrículas, 7.052 Fail (21,64 %). No hay entrenamiento ni demostración de impacto. Colab continúa pendiente de sincronización. Hay limitaciones de cobertura, temporalidad y duplicados de actividad documentadas.

PSet 2: enunciado y rúbrica preservados, plan y contrato preparados. Infraestructura, Compose, flujos, modelos dbt, Spark y Snowflake pendientes de implementación. Ningún servicio ni recurso cloud ejecutado en este encargo. PSet 3 y 4 solo contienen .gitkeep.

## Datos y verificación

Colocar los originales OULAD en datasets/, siguiendo su README. Cada etapa consume esa fuente común y guarda sus derivados por separado. La auditoría de PSet 1 no modifica CSV; PSet 2 prevé montaje de solo lectura de ../datasets.

Instalar dependencias locales desde pset-01/scripts/requirements.txt y seguir los comandos de [PSet 1](pset-01/README.md). Verificar con `python pset-01/scripts/verificar_entregables.py` desde el entorno configurado. El informe [verificacion.json](pset-01/docs/verificacion.json) registra comparaciones entre Markdown, notebook, PDF, PPTX y renderizado de PowerPoint, enlaces y checksums. La [trazabilidad](pset-01/docs/trazabilidad-entregables.md) describe fuentes, formatos y limitaciones.

## Versionado y continuidad

Versionar código, Markdown, notebook final, manifiestos y exportaciones finales. .gitignore excluye datos crudos y voluminosos, secretos, entornos, caches, logs, temporales y backups. Los generadores de contenido respaldan textos distintos antes de reemplazarlos: reconciliar cambios editoriales antes de regenerar desde prompt-codex-psets.md. No había entregables previos en pset-01 o pset-02 al inicio; el encargo original permanece intacto.

La publicación en GitHub queda a cargo del autor. No se crearon remotos, no se realizó push y no se enviaron mensajes. Los documentos del pipeline son especificaciones para la siguiente etapa, no evidencia de ejecución.
''')
 write('pset-01/README.md','''# PSet 1: propuesta revisada de focalización académica

Wilmer Puerta · 12-nov-2026. Una universidad hipotética con tutorías limitadas necesita priorizar revisión antes del cierre. El objetivo es evaluar si la evolución de actividad digital mejora la detección con igual capacidad. No hay institución participante ni modelo entrenado.

## Entregables reales

| Entregable | Fuente y exportación |
|---|---|
| Canvas | [Markdown](canvas-wilmer-puerta.md) |
| Propuesta breve | [Markdown](propuesta-pset1.md), [memo PDF](output/pdf/PSet1_memo_Puerta_Wilmer.pdf), dos páginas |
| Pitch | [Texto visible y notas](pset01-presentacion.md), [PPTX editable](output/pitch/PSet1_pitch_Puerta_Wilmer.pptx), [PPT real](output/pitch/PSet1_pitch_Puerta_Wilmer.ppt), seis diapositivas |
| Proyecto ampliado | [Markdown completo](proyecto-completo-pset1.md), [notebook](notebooks/PSet1_notebook_completo_Puerta_Wilmer.ipynb), [PDF completo](output/pdf/PSet1_notebook_completo_Puerta_Wilmer.pdf) |
| Evaluación docente | [Rúbrica íntegra](rubrica.md) |
| Evidencia de datos | [Auditoría](docs/auditoria-datos.md), [resultados JSON](docs/auditoria-resultados.json), [poblaciones por edición](docs/poblaciones-por-edicion.csv), [manifiesto](../datasets/manifest.json) |
| Revisión | [Feedback](docs/respuesta-feedback.md), [trazabilidad](docs/trazabilidad-entregables.md), [verificación automática](docs/verificacion.json) |

## Decisiones y límites

Tres ideas conservadas: riesgo académico con OULAD; revisión de ECG para fibrilación auricular; crecimiento anual de ingresos en telecomunicaciones. Matriz de seis criterios con totales 16, 13 y 16. Se seleccionó la primera por menor incertidumbre de acceso público, target y evaluación delimitada frente al empate con la tercera. Las puntuaciones son juicios de diseño, no experimentos.

Pregunta principal: antecedentes estáticos frente a los mismos algoritmos enriquecidos con actividad longitudinal. Regresión logística multinomial y Random Forest. Comparador adicional: recencia descendente, que ya usa tiempo y no sustituye el baseline estático. Target: Fail, Withdrawn y aprobación (Pass + Distinction). Cuatro cortes: 14, 28, 42 y 56, por matrícula registrada hasta el inicio y aún no retirada al corte. Sin notas de evaluaciones en el análisis principal.

Meta provisional: +10 % relativo en TP@K al día 56 frente al baseline estático, igual N y K. Presupuesto preventivo simulado del 10 % por edición y corte: K = floor(0.10 × N), sensibilidad 5 % y 20 %. No es una capacidad institucional medida. El ejemplo 40 a 44 con 100 revisiones ilustra la meta; no representa desempeño obtenido ni aprobaciones ganadas. Focalización se evalúa retrospectivamente; impacto requiere el piloto posterior de oferta aleatoria de acompañamiento vs atención habitual, con aprobación por asignación e intervalo de confianza.

## Reproducción local y regeneración

Comandos desde raíz. Python usado: 3.14.7, dependencias efectivas resueltas en [requirements.txt](scripts/requirements.txt). Crear un entorno e instalar ese archivo; en otra plataforma confirmar disponibilidad compatible de paquetes. Los scripts resuelven la raíz desde su ubicación. Font de exportación: Arial instalada en macOS, ruta /System/Library/Fonts/Supplemental; adaptar FONT si se cambia de sistema.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r pset-01/scripts/requirements.txt
.venv/bin/python pset-01/scripts/auditar_datos.py
.venv/bin/python pset-01/scripts/preparar_documentacion.py
.venv/bin/python pset-01/scripts/generar_contenidos.py
.venv/bin/python pset-01/scripts/generar_pitch.py
.venv/bin/python pset-01/scripts/exportar_documentos.py
.venv/bin/python pset-01/scripts/cerrar_documentacion.py
.venv/bin/python pset-01/scripts/verificar_entregables.py
```

Auditoría alternativa: `--data-dir /ruta/autorizada`. Se ejecutó con ../datasets como origen común resuelto desde raíz. No se requieren datos en otra carpeta. Audita hashes, clases, población, claves, relaciones y actividad hasta cada corte, sin entrenamiento. Aproximadamente 433 MB de actividad se leen por chunks.

Antes de regenerar, reconciliar cambios del usuario; generar_contenidos.py reconstruye desde el encargo conservado más la auditoría y respalda textos diferentes en backups/. exportar_documentos.py usa los Markdown revisados como fuentes íntegras para notebook y PDF. generar_pitch.py usa objetos de texto nativos, guarda su contenido JSON y deriva el Markdown exacto. No se usa el memo como resumen del notebook.

Para convertir después de regenerar el PPTX en este Mac, crear tmp/ y ejecutar `osascript pset-01/scripts/convertir_powerpoint.applescript "$PWD"`. Este paso abre Microsoft PowerPoint y requiere permiso de automatización del sistema. Se ejecutó correctamente: exportó PPT binario real y PDF temporal de revisión de seis páginas. No es un simple cambio de extensión. Si se regenera PPTX sin convertir, el PPT y la revisión quedan desactualizados: volver a convertir antes de verificar. Sin PowerPoint o un conversor compatible, la conversión .ppt queda pendiente. No se requiere distribuir el PDF del pitch.

Las dependencias artifact-tool/load_workspace_dependencies y Poppler no estaban disponibles en este host. Se usó OOXML nativo sin python-pptx para el pitch, Microsoft PowerPoint para conversión real y render, ReportLab para los PDF y PyMuPDF para extracción y renderizado. Los scripts están incluidos. No se declara una validación ejecutada mediante herramientas ausentes.

## Feedback y estado de evidencia

| Feedback | Respuesta y evidencia | Estado |
|---|---|---|
| Cómo evaluar tutorías | Protocolo de asignación aleatoria e intención de tratar, aprobación principal, retiro y costos en propuesta, Canvas y proyecto completo | Diseño completo; piloto fuera de alcance |
| Seguimiento concreto | Recencia, cuatro listas, mismo K, repeticiones, TP por matrícula y personas únicas en revisión metodológica | Especificado; comparación pendiente de modelos |
| Cuantificar problema | 7.052 Fail / 32.593 matrículas originales = 21,64 %, con población inicial y por corte en auditoría | Conteos locales verificados; sin extrapolación |
| Viabilidad y MVP en pitch | Cinco archivos auditados, validación prevista, MVP y criterios de avance en seis diapositivas | Documentado; producto aún no construido |
| Beneficio esperado | Ejemplo ilustrativo 40 a 44 con 100 revisiones, +10 % relativo y límites causales | Meta, no resultado |

Notebook válido y texto íntegro respecto del Markdown. Memo y PDF completo revisados en todas sus páginas, tablas legibles. Pitch revisado mediante exportación real de PowerPoint y comparación de texto. [Informe reproducible](docs/verificacion.json). Persisten comprobaciones globales de duplicados, cobertura semántica, calendario, etiquetas maduras y particiones; ninguna métrica predictiva calculada.

Colab fue antecedente de trabajo. No se facilitó URL ni sesión autenticada identificable que permita respaldar, comparar celdas y sincronizar: actualización remota pendiente. La fuente local revisada es la base controlada, sin afirmar que Colab esté actualizado.
''')
 write('pset-01/docs/respuesta-feedback.md','''# Respuesta al feedback

1. Problema y métrica: se conserva la pregunta estática/longitudinal, se separan PR-AUC, TP@K y aprobación del piloto. Propuesta secciones 1 y 3, Canvas y revisión metodológica del proyecto completo. El piloto posterior define oferta aleatoria por persona, estratificación, coherencia de matrículas múltiples, intención de tratar, diferencia absoluta de aprobación e intervalo, con Fail y Withdrawn separados; muestra pendiente según supuestos y potencia.
2. Seguimiento: comparador de recencia descendente, N y K comunes, nunca activos y cobertura desconocida explícitos, cuatro listas, repetidos consumen cupos, TP acumulados por matrícula y personas únicas. Protocolo de seguimiento futuro registra oferta, contacto, participación, otras ayudas, acciones, tiempos y costos. La simulación no modifica trayectorias ni demuestra efecto educativo.
3. Pitch: seis diapositivas con tasa auditada y denominador, fuente, modelos y evaluación, alcance del MVP, ejemplo ilustrativo de beneficio, cuatro grupos de riesgos y solicitud. Auditoría: 7.052 Fail de 32.593, 21,64 %. Retiros separados, sin extrapolación. Día 56: 26.294 elegibles y 2.619 cupos, sin ranking entrenado.

Cuantificación descriptiva cerrada para esta copia; cobertura y particiones finales por validar. La mejora del 10 % no está demostrada. Impacto, costos y capacidad reales siguen sin datos institucionales. La elección de módulos puede acotarse con criterios de calidad previos a mirar resultados. Colab pendiente de acceso y sincronización verificable.
''')
 write('pset-01/docs/trazabilidad-entregables.md','''# Trazabilidad de entregables

Fecha de revisión: 12-nov-2026. No existían versiones de entregables en las carpetas pset-01 y pset-02; se preservó prompt-codex-psets.md. Backups locales de revisiones se excluyen de Git. No se creó el nombre histórico PSe1_memo ni un memo divergente.

| Fuente controlada | Derivado | Verificación |
|---|---|---|
| propuesta-pset1.md | PSet1_memo_Puerta_Wilmer.pdf | Dos páginas; cuatro secciones y referencias; fragmentos completos por extracción |
| proyecto-completo-pset1.md | Notebook completo y PDF completo | Celdas Markdown concatenadas idénticas; todos los fragmentos sustantivos en PDF; tres ideas, seis criterios, matriz 16/13/16, selección y ocho riesgos |
| scripts/pitch-contenido.json | pset01-presentacion.md y PPTX | Seis títulos, mensajes, texto visible y notas comparados exactamente; objetos nativos editables |
| PPTX nativo | PPT binario y PDF temporal de revisión | Conversión real con Microsoft PowerPoint, seis diapositivas y texto completo en render PDF; cabecera OLE del PPT comprobada |
| Cinco CSV originales | Auditoría JSON, tabla por edición y manifiesto | SHA-256, bytes, conteos, claves y relaciones; hashes originales comprobados al final |
| Bloques M, N y O del encargo | Enunciado y rúbricas | Texto docente preservado; notas locales separadas |

## Coherencia metodológica

Unidad matrícula, población registrada hasta día 0, retiro solo si ya ocurrió, target Fail/Withdrawn/aprobación, cuatro cortes 14/28/42/56, K por edición con floor y presupuesto simulado del 10 %. Meta +10 % relativo en TP al día 56, no resultado. Regresión logística multinomial y Random Forest con comparación estática/longitudinal por algoritmo. Recencia es comparador operativo adicional. Tutor conserva decisión. Aprobación por asignación es resultado principal del piloto posterior, fuera del MVP.

Riesgos de memo/Canvas/pitch: R1 mejora y transferencia, R2 fuga/cobertura/procesamiento, R3 capacidad y efecto, R4 equidad/confianza. Correspondencia con ampliados: {1,4}, {2,3,8}, {5,6}, {7}. Gravedad alta/crítica/alta/alta. Documentales: escala de publicación; auditadas: tasas y poblaciones locales; ilustrativas: 40 a 44. No se mezclan niveles ni se atribuye causalidad a clics.

## Herramientas y revisión

Python 3.14.7 y paquetes exactos en scripts/requirements.txt. ReportLab exporta párrafos y tablas completos; PyMuPDF extrae y renderiza cada página. Notebook nbformat 4 validado. No había artifact-tool ni load_workspace_dependencies disponible; fallback OOXML nativo, sin python-pptx ni aplanado. PowerPoint convirtió y renderizó el archivo local. No se afirma validación con Poppler ni servicios ausentes.

Todas las páginas del memo y documento completo, y las seis diapositivas renderizadas, fueron revisadas visualmente. El script verificar_entregables.py comprueba fuentes/exportaciones, límites de página, formatos, enlaces de README, clases, originales y ausencia de rutas personales. verificacion.json conserva el resultado; entregables-manifest.json identifica archivos por hash. El PDF temporal del pitch y PNG de revisión se conservan solo en tmp/ excluido de Git.

## Fuentes externas

Se contrastaron OULAD (Kuzilek et al., doi:10.1038/sdata.2017.171), Icentia11k versión 1.0 en PhysioNet (doi:10.13026/kk0v-r952) y preprint CinC 2021. La navegación oficial de OU conduce actualmente a https://research.stem.open.ac.uk/ouanalyse/dataset/; se conserva el DOI para identificación estable. OU Analyse describe actualización semanal del riesgo de la siguiente evaluación: plausibilidad operativa, distinto target y sin prueba causal para este proyecto. Klenke et al. arXiv:2102.08803 v4, 2023, informa efecto positivo impreciso en otro contexto. AERA presenta el ensayo de Bettinger y Baker, pero su página muestra metadatos de volumen/fecha inconsistentes con la referencia suministrada; no se usó esa discrepancia para inferir resultados propios. Referencias históricas con fechas de consulta del autor se conservan y no se presentan como auditorías de datos.

## Pendientes reales

Colab: falta acceso identificable para respaldo y sincronización. Datos: significado y conteo global de claves diarias repetidas, cobertura, calendario y maduración de etiquetas por validar. Modelos, características y comparación sin ejecutar. PSet 2 solo preparado; sin Compose aparente ni consumo cloud. PSet 3 y 4 sin enunciados. Ningún remoto ni publicación automática.
''')
 print('README, feedback, trazabilidad y dependencias escritos')
if __name__=='__main__':main()
