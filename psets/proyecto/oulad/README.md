# Apoyo académico a tiempo con OULAD

Wilmer Puerta · Proyecto académico de ciencia de datos · 12-nov-2026.

Evaluar si la actividad digital longitudinal permite detectar más futuras reprobaciones con los mismos cupos de revisión preventiva. Universidad hipotética, sin socio institucional comprometido. El proyecto distingue predicción, focalización retrospectiva e impacto educativo posterior.

## Etapas y estructura

```text
psets/
├── datasets/       originales compartidos y manifiesto
├── pset-01/        propuesta revisada, auditoría y exportaciones
├── pset-02/        pipeline verificado, memo y reproducción
├── pset-03/        alcance pendiente de enunciado
└── pset-04/        alcance pendiente de enunciado
```

- [PSet 1: propuesta y entregables](pset-01/README.md).
- [PSet 2: pipeline y reproducción](pset-02/README.md).
- [Datos compartidos y reproducción](datasets/README.md).

Las cuatro carpetas organizan etapas del mismo proyecto. La rúbrica del profesor menciona cinco PSets del curso; se conserva su texto y ponderación sin inventar una quinta etapa o requisitos de las etapas 3 y 4.

## Qué leer y estado real

Leer primero la [propuesta](pset-01/propuesta-pset1.md), el [Canvas](pset-01/canvas-wilmer-puerta.md), el [proyecto completo](pset-01/proyecto-completo-pset1.md) y la [guía del pitch](pset-01/pset01-presentacion.md).

PSet 1: fuentes Markdown, notebook válido, memo PDF de dos páginas, PDF completo y pitch nativo de seis diapositivas en PPTX y PPT real. Auditoría ejecutada sobre cinco CSV: 32.593 matrículas, 7.052 Fail (21,64 %). No hay entrenamiento ni demostración de impacto. Colab continúa pendiente de sincronización. Hay limitaciones de cobertura, temporalidad y duplicados de actividad documentadas.

PSet 2: pipeline completo verificado con Kestra, Snowflake, dbt y Spark. Raw contiene cinco fuentes y 10.726.852 filas; Silver/Gold conservan 8.459.320 claves diarias y 39.605.099 clics. dbt aprobó 168 pruebas en 23 modelos. La OBT publicada contiene 108.277 filas y 35 columnas, con cuatro cortes reconciliados, pruebas temporales y lectura de vuelta aprobadas. Se comprobaron detención y retry controlados, idempotencia y backfill por fichero. La reproducción desde exportación limpia usó volúmenes nuevos, recargó cinco CSV y produjo una OBT idéntica. El [memo técnico de seis páginas](pset-02/output/pdf/PSet2_memo_Puerta_Wilmer.pdf) está generado desde [Markdown](pset-02/memo-pset2.md), con [verificación de coherencia](pset-02/docs/memo-verificacion.json). La [revisión local del paquete](pset-02/docs/revision-paquete.md) está completada. Quedan el costo monetario sin cuantificar y la decisión de publicación GitHub. PSet 3 y 4 solo contienen .gitkeep.

## Datos y verificación

Colocar los originales OULAD en datasets/, siguiendo su README. Cada etapa consume esa fuente común y guarda sus derivados por separado. La auditoría de PSet 1 no modifica CSV; PSet 2 monta ../datasets en solo lectura, comprobado desde Spark.

Instalar dependencias locales desde pset-01/scripts/requirements.txt y seguir los comandos de [PSet 1](pset-01/README.md). Verificar con `python pset-01/scripts/verificar_entregables.py` desde el entorno configurado. El informe [verificacion.json](pset-01/docs/verificacion.json) registra comparaciones entre Markdown, notebook, PDF, PPTX y renderizado de PowerPoint, enlaces y checksums. La [trazabilidad](pset-01/docs/trazabilidad-entregables.md) describe fuentes, formatos y limitaciones.

## Versionado y continuidad

Versionar código, Markdown, notebook final, manifiestos y exportaciones finales. .gitignore excluye datos crudos y voluminosos, secretos, entornos, caches, logs, temporales y backups. Los generadores de contenido respaldan textos distintos antes de reemplazarlos: reconciliar cambios editoriales antes de regenerar desde prompt-codex-psets.md. No había entregables previos en pset-01 o pset-02 al inicio; el encargo original permanece intacto.

Destino de publicación autorizado: [wilmerpuerta/data-science-end-to-end](https://github.com/wilmerpuerta/data-science-end-to-end), carpeta [psets/proyecto/oulad/](https://github.com/wilmerpuerta/data-science-end-to-end/tree/master/psets/proyecto/oulad), dentro del fork existente del curso. Desde un clon, entrar en esa carpeta antes de seguir los comandos del proyecto. La [guía de publicación](pset-02/docs/publicacion-github.md) explica ubicación y alcance; las configuraciones y enunciados del curso se conservan. PSet 2 distingue componentes probados y trabajo pendiente en su README e informes de evidencia.
