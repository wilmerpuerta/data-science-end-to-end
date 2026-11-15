# PSet 1: propuesta revisada de focalización académica

Wilmer Puerta · Revisión local del 15-nov-2026. Se incorporan los tres gaps docentes: objetivo de negocio calculable, comparación de procesos y pitch con viabilidad técnica, evaluación, MVP y beneficio esperado. Universidad hipotética; modelos y simulación de políticas todavía pendientes.

El límite vigente del memo es cinco páginas, por indicación del usuario del 15-nov-2026. El límite anterior de 1-2 páginas procedía del encargo local y de la rúbrica transcrita; ambos se conservan como antecedentes, sin prevalecer sobre esta actualización. La cobertura de criterios y gaps se documenta por separado.

## Entregables y fuentes controladas

| Entregable | Fuente y exportación |
|---|---|
| Canvas | [Markdown](canvas-wilmer-puerta.md) |
| Memo de propuesta | [Markdown](propuesta-pset1.md) y [memo PDF de cinco páginas](output/pdf/PSet1_memo_Puerta_Wilmer.pdf) |
| Pitch | [Texto visible y notas](pset01-presentacion.md), [PPTX editable](output/pitch/PSet1_pitch_Puerta_Wilmer.pptx) y [PPT real](output/pitch/PSet1_pitch_Puerta_Wilmer.ppt), seis diapositivas |
| Proyecto ampliado | [Markdown íntegro](proyecto-completo-pset1.md), [notebook completo](notebooks/PSet1_notebook_completo_Puerta_Wilmer.ipynb) y [PDF completo](output/pdf/PSet1_notebook_completo_Puerta_Wilmer.pdf) |
| Evaluación docente | [Rúbrica preservada](rubrica.md), [respuesta a los tres gaps](docs/respuesta-feedback.md) y [cobertura de la rúbrica en el memo](docs/cobertura-rubrica-memo.md) |
| Evidencia descriptiva | [Auditoría original](docs/auditoria-datos.md), [JSON original](docs/auditoria-resultados.json), [poblaciones por edición](docs/poblaciones-por-edicion.csv), [métricas de negocio](docs/metricas-negocio.json) y [manifiesto](../datasets/manifest.json) |
| Trazabilidad | [Fuentes y formatos](docs/trazabilidad-entregables.md), [informe de verificación](docs/verificacion.json) y [revisión visual](docs/revision-visual.json) |

## Objetivo de negocio y tres políticas

Cubrir más futuras reprobaciones con los mismos cupos y medir semanas de anticipación potencial respecto al cierre. Cobertura preventiva = TP seleccionados antes del cierre / Fail elegibles. Se reportan casos, porcentaje de cobertura, casos por cada 100 revisiones, omisiones, carga y personas únicas; la unidad analítica es matrícula estudiante-módulo-edición.

La comparación principal fija la cohorte elegible al día 56 y K = floor(0.10 × N) por edición para las tres políticas: reactiva tras conocer Fail, estática con antecedentes iniciales y longitudinal con los mismos antecedentes más actividad hasta ese corte. Históricos: 26.294 elegibles, 6.972 Fail y 2.619 cupos. La meta provisional es +10 % relativo de TP longitudinal frente al estático. Con TP estático = 0 se informa diferencia absoluta. Las cifras se recalcularán en la prueba reservada.

Anticipación potencial = (duración de la edición - día de primera selección) / 7. Al día 56 quedan 25,4-30,4 semanas en las ediciones de esta copia; es margen disponible, no rendimiento alcanzado ni fecha real de tutoría o publicación de notas. La reactiva puede cubrir casos después del cierre, con cero anticipación preventiva por definición del escenario.

Para cuatro listas se fijará presupuesto total B común: cada revisión repetida consume un cupo y cada matrícula cuenta una vez en cobertura acumulada. Las capacidades por corte auditadas no conceden cuatro presupuestos gratuitos a una política. Sensibilidad 5 % y 20 %.

## Viabilidad, evaluación y MVP

Se conservan las tres ideas y la matriz de selección 16/13/16; OULAD es la idea elegida. Regresión logística multinomial y Random Forest se compararán en versiones estática/longitudinal, con PR-AUC para Fail, calibración e incertidumbre como respaldo técnico. La prueba requiere ediciones posteriores compatibles, etiquetas maduras y estudiantes separados, con transformaciones aprendidas solo en entrenamiento. No se usan notas de evaluaciones.

El PSet 2 ya construyó datos reproducibles: OBT de 108.277 filas/35 columnas y 168 pruebas dbt aprobadas. El MVP previsto añadirá selector de edición/corte/capacidad, modelos y transformaciones versionados, listas, evolución y reporte de las tres políticas. Entrenamiento, simulación y beneficio predictivo siguen pendientes; completar el MVP no garantiza la mejora del 10 %.

OULAD permite evaluar listas, cobertura, anticipación y carga simulada. Tutorías efectivas, participación, capacidad real, costos, reducción de reprobación o deserción y transferencia institucional requieren otra fase. El MVP utiliza exclusivamente OULAD. D2L y WiFi de la USFQ quedan fuera; su eventual uso requiere aprobación formal y revisión LOPDP. Los registros digitales no acreditan intencionalidad.

## Reproducir esta revisión

Desde la raíz, con Python y [requirements.txt](scripts/requirements.txt) instalados:

```bash
.venv/bin/python pset-01/scripts/preparar_documentacion.py
.venv/bin/python pset-01/scripts/generar_contenidos.py
.venv/bin/python pset-01/scripts/generar_pitch.py
.venv/bin/python pset-01/scripts/exportar_documentos.py
.venv/bin/python pset-01/scripts/cerrar_documentacion.py
```

preparar_documentacion.py actualiza únicamente métricas descriptivas de negocio. generar_contenidos.py valida las fuentes editoriales vigentes; ya no reconstruye textos desde el prompt histórico. cerrar_documentacion.py comprueba documentación y enlaces sin reemplazar README o dependencias. Los scripts anteriores de bootstrap se preservan en el respaldo local de la revisión. El prompt original permanece intacto.

Editar propuesta-pset1.md, canvas-wilmer-puerta.md y proyecto-completo-pset1.md como fuentes editoriales controladas; editar scripts/pitch-contenido.json como fuente del pitch. generar_pitch.py deriva el Markdown exacto y objetos nativos PPTX usando pitch-base.json, una base técnica normalizada por PowerPoint sin contenido de diapositivas ni propiedades personales. exportar_documentos.py conserva íntegro el Markdown ampliado en el notebook y PDF. Los cambios editoriales se revisan con validar_fuentes.py para mantener los tres gaps.

Para exportar el PPT binario y los PDF temporales de revisión en este Mac:

```bash
osascript pset-01/scripts/convertir_powerpoint.applescript "$PWD"
.venv/bin/python pset-01/scripts/verificar_entregables.py
```

La conversión usa Microsoft PowerPoint y requiere permiso de automatización de macOS. Sin ese conversor, el PPT y su render deben declararse pendientes después de modificar el PPTX. Los PNG/PDF de revisión y respaldos se guardan en tmp/ y backups/, excluidos de Git. Se mantienen los nombres finales canónicos.

ReportLab exporta PDF y PyMuPDF permite extracción y revisión visual. La tipografía es Arial del sistema macOS; adaptar FONT si cambia de plataforma. El runtime artifact-tool/load_workspace_dependencies no está disponible en este host: se conserva el generador OOXML nativo existente, sin python-pptx ni diapositivas aplanadas, y la revisión real con PowerPoint. No se afirma usar herramientas ausentes.

La auditoría descriptiva original se reproduce, si es necesario, con auditar_datos.py sobre los cinco CSV; no es necesario releer los 433 MB de actividad para cambiar textos o exportar documentos. calcular_metricas_negocio.py verifica courses.csv y reutiliza los conteos auditados; no ajusta modelos ni conecta con Snowflake.

## Cierre de los tres gaps y pendientes

1. Objetivo de negocio: cobertura y anticipación potencial, con meta provisional, presupuesto y denominadores explícitos.
2. Viabilidad de negocio: tres políticas, igualdad de capacidad y límites de lo validable por simulación; D2L/WiFi institucionales fuera del MVP.
3. Pitch y propuesta: problema cuantificado, viabilidad técnica y evaluación, MVP y apoyo solicitado visibles, con cifras observadas separadas de metas y márgenes potenciales.

Los modelos y la simulación aún deben ejecutarse. Cobertura externa de logs y disponibilidad histórica de atributos/etiquetas requieren validación. Colab continúa pendiente de acceso identificable y sincronización; el notebook local es la fuente derivada actual. La publicación inicial del 14-nov-2026 se conserva en el historial. El autor autorizó actualizar el mismo destino con esta revisión el 15-nov-2026; ver la [guía de publicación](../pset-02/docs/publicacion-github.md).
