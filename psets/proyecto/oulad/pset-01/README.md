# PSet 1: propuesta revisada de focalización académica

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
