# Trazabilidad de entregables revisados

Revisión local del 15-nov-2026, posterior a la publicación del 14-nov-2026. Se respaldó el árbol anterior del PSet 1 y el memo original de cinco páginas antes de editar. Respaldos y PNG/PDF de revisión quedan en backups/ y tmp/, excluidos de Git. Se mantienen los nombres finales canónicos, sin dos versiones divergentes del mismo entregable.

| Fuente controlada | Derivado | Comprobación |
|---|---|---|
| propuesta-pset1.md | Memo PDF | Cinco páginas, cuatro secciones, fuentes y todos los fragmentos del Markdown |
| proyecto-completo-pset1.md | Notebook y PDF completo | Celdas Markdown concatenadas idénticas; texto íntegro; paginación verificada, tres ideas, matriz 16/13/16, selección, ocho riesgos y auditoría |
| scripts/pitch-contenido.json | pset01-presentacion.md y PPTX | Seis títulos, mensajes, texto visible y notas exactos; objetos nativos editables |
| PPTX | PPT binario y PDF temporal de revisión | Conversión real de PowerPoint; seis diapositivas; comparación textual y revisión visual |
| Auditoría original, tabla por edición y courses.csv | docs/metricas-negocio.json | Identidad de courses por SHA; N, Fail y K reconciliados; margen temporal por duración; sin entrenamiento |
| Fuentes editoriales vigentes | Validación de los tres gaps | validar_fuentes.py comprueba objetivo, métricas, tres políticas, presupuesto, viabilidad, evaluación, MVP y exclusiones |

## Coherencia de negocio

La unidad es matrícula estudiante-módulo-edición; las personas únicas se informan aparte. El objetivo mide casos cubiertos, cobertura preventiva y anticipación potencial. Comparación principal: día 56, misma cohorte y K = floor(0.10 × N) por edición para reactiva, estática y longitudinal. Meta +10 % relativa frente al estático; baseline cero se trata mediante diferencia absoluta. Las otras semanas se analizan con presupuesto total B común y las repeticiones consumen capacidad.

La reactiva consulta Fail únicamente después del cierre; tiene cero anticipación preventiva por definición del escenario, pero puede cubrir casos después. El resultado observado permanece fijo en las tres políticas. La duración de edición aproxima cierre; no se afirma conocer fechas de tutoría o comunicación del resultado. El margen 25,4-30,4 semanas y la cota 37,6 % son descriptivos y límites, no desempeño logrado.

## Viabilidad y MVP

El pipeline PSet 2 ya está verificado; modelos, evaluación y simulación siguen pendientes. El MVP previsto incluye selector de edición/corte/capacidad, modelo y transformaciones versionados, listas, evolución y comparación de políticas. Cobertura y anticipación miden utilidad retrospectiva. El efecto de tutorías es hipótesis de una fase posterior, sin prueba causal requerida en este PSet.

OULAD es la única fuente del MVP. D2L y WiFi institucionales quedan fuera, sujetos a aprobación y revisión LOPDP en otra fase. Los logs no acreditan intencionalidad ni la reprobación acredita deserción. Riesgos comunes R1 aporte, R2 fuga/cobertura, R3 capacidad/adopción y R4 equidad/confianza mantienen gravedad alta/crítica/alta/alta. Correspondencia con los ocho riesgos ampliados: R1={1,4}, R2={2,3,8}, R3={5,6}, R4={7}.

## Generación y límites de herramientas

Los Markdown y pitch-contenido.json son fuentes editoriales actuales. generar_contenidos.py valida su coherencia, preparar_documentacion.py deriva métricas y cerrar_documentacion.py valida documentación, sin reponer textos históricos ni archivos PSet 2. exportar_documentos.py deriva notebook y PDF; generar_pitch.py utiliza pitch-base.json para conservar un paquete OOXML normalizado por PowerPoint, con notas editables y sin cuadros de reparación al regenerar. Cada escritura de fuente generada respalda versiones diferentes.

ReportLab exporta PDF, nbformat valida notebook y PyMuPDF extrae texto y renderiza. Microsoft PowerPoint convierte PPT y renderiza el pitch. El runtime artifact-tool/load_workspace_dependencies y Poppler no están disponibles; no se declara una validación con herramientas ausentes. Los originales OULAD y el memo aportado se conservan sin cambios.

## Estado y pendientes

El [informe de verificación](verificacion.json) registra formato, texto, datos y los tres gaps. La [revisión visual](revision-visual.json) registra las 5 páginas del memo, las 20 del documento completo y las 6 diapositivas; los renders de PPTX y PPT coinciden píxel a píxel. Esta revisión complementa la extracción; esta última no prueba legibilidad por sí sola. El [inventario](entregables-manifest.json) se actualiza al cerrar el paquete. Modelos, simulación, incertidumbre predictiva, disponibilidad temporal de atributos/etiquetas y transferencia institucional aún deben verificarse. Colab continúa pendiente de acceso y sincronización. La revisión local no actualiza por sí sola GitHub.

## Extensión actualizada y acceso al pitch

Por indicación del usuario del 15-nov-2026, el memo admite hasta cinco páginas. El generador y el verificador aplican ese límite; el [mapa de cobertura de rúbrica y gaps](cobertura-rubrica-memo.md) permite revisar cada criterio. La rúbrica y el prompt históricos conservan sus textos originales, incluida la extensión anterior; no se presentan como requisitos de extensión vigentes. La revisión previa se preserva en backups/, excluido de Git.

Se reintentó el acceso al pitch local mediante Microsoft PowerPoint: apertura del PPTX sin aviso de reparación, seis miniaturas con notas y diapositiva de alcance/MVP visible. No había una sesión de documento conectada al conector, por lo que la comprobación se hizo en la aplicación nativa. Se cerró sin modificar su contenido.
