# Trazabilidad de entregables

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
