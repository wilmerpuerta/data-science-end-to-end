# Apoyo académico a tiempo con OULAD

Wilmer Puerta · Proyecto académico de ciencia de datos · 12-nov-2026.

Evaluar si la actividad digital longitudinal permite detectar más futuras reprobaciones con los mismos cupos de revisión preventiva. Universidad hipotética, sin socio institucional comprometido. El proyecto distingue predicción, focalización retrospectiva e impacto educativo posterior.

## Etapas y estructura

```text
psets/
├── datasets/       originales compartidos y manifiesto
├── pset-01/        propuesta revisada, auditoría y exportaciones
├── pset-02/        pipeline verificado, memo y reproducción
├── pset-03/        experimentación v2 cerrada; seis familias, prompting y Registry
├── pset-04/        alcance acordado y planificación del proyecto final
└── proyecto_final/ API batch y fixtures verificadas; integración final pendiente
```

- [PSet 1: propuesta y entregables](pset-01/README.md).
- [PSet 2: pipeline y reproducción](pset-02/README.md).
- [PSet 3: experimentación y MLflow](pset-03/README.md).
- [PSet 4: alcance, recursos y plan de integración](pset-04/README.md).
- [Proyecto final: estado de implementación y pruebas del núcleo](proyecto_final/README.md).
- [Datos compartidos y reproducción](datasets/README.md).

Las cuatro carpetas organizan etapas del mismo proyecto. La rúbrica del profesor menciona cinco PSets del curso; se conserva su texto y ponderación sin inventar una quinta etapa o requisitos de las etapas 3 y 4.

## Qué leer y estado real

Leer primero la [propuesta](pset-01/propuesta-pset1.md), el [Canvas](pset-01/canvas-wilmer-puerta.md), el [proyecto completo](pset-01/proyecto-completo-pset1.md) y la [guía del pitch](pset-01/pset01-presentacion.md).

PSet 1: fuentes Markdown, notebook válido, memo breve PDF de dos páginas y versión extendida de cinco páginas, PDF completo y pitch nativo de seis diapositivas en PPTX y PPT real. Auditoría ejecutada sobre cinco CSV: 32.593 matrículas, 7.052 Fail (21,64 %). No hay entrenamiento ni demostración de impacto. Colab continúa pendiente de sincronización. Hay limitaciones de cobertura, temporalidad y duplicados de actividad documentadas.

PSet 2: pipeline completo verificado con Kestra, Snowflake, dbt y Spark. Raw contiene cinco fuentes y 10.726.852 filas; Silver/Gold conservan 8.459.320 claves diarias y 39.605.099 clics. dbt aprobó 168 pruebas en 23 modelos. La OBT publicada contiene 108.277 filas y 35 columnas, con cuatro cortes reconciliados, pruebas temporales y lectura de vuelta aprobadas. Se comprobaron detención y retry controlados, idempotencia y backfill por fichero. La reproducción desde exportación limpia usó volúmenes nuevos, recargó cinco CSV y produjo una OBT idéntica. El [memo técnico de seis páginas](pset_2/docs/PSet2_memo_Puerta_Wilmer.pdf) está generado desde [Markdown](pset_2/docs/memo-pset2.md), con [verificación de coherencia](pset_2/docs/memo-verificacion.json). La [revisión local del paquete](pset_2/docs/revision-paquete.md) está completada. El costo monetario permanece sin cuantificar; la actualización GitHub del paquete está autorizada por el autor el 15-nov-2026. PSet 3: reconstrucción v2 con seis familias (incluido GPT mediante prompting), dos baselines, 90 configuraciones de tuning por el criterio del negocio, controles estáticos, anticipación y seis notebooks ejecutados. Champion HGB v1 y challenger logística v2 registrados y reproducidos; memo legible de seis páginas, CSV y auditoría. La prueba 2014J se declara benchmark reutilizado; el costo-beneficio operativo de un LLM externo se evaluará posteriormente con la Universidad. PSet 4 tiene como meta acordada al menos +10 % relativo en cobertura de Fail frente al modelo estático, con los mismos cupos. Usa batch preventivo durante el período actual y mantiene la bolsa reactiva vigente protegida; el adelanto de hasta el 30 % de cupos reactivos futuros es un escenario presupuestario. El árbol `proyecto_final/` ya se creó y la API batch y las fixtures tienen 63 pruebas aprobadas, con dbt/Spark y memos incorporados; ocho lotes de control con Kestra y carga a Snowflake verificados; monitoreo, deriva, alertas y tablero verificados; challenger reentrenado, comparado y rechazado por decisión humana; CD/GHCR y recarga/rollback técnico verificados; evaluación final de negocio pendiente.

La revisión local del PSet 1 del 15-nov-2026 incorpora los tres gaps docentes: cobertura y anticipación como objetivo de negocio, tres políticas con igual capacidad y pitch con viabilidad técnica, evaluación, MVP y beneficio esperado. Los formatos se derivan de fuentes controladas; ver la [respuesta al feedback](pset-01/docs/respuesta-feedback.md). La publicación inicial es del 14-nov-2026; el autor autorizó actualizar el mismo destino el 15-nov-2026, incluyendo las aclaraciones de continuidad en PSet 2.

## Datos y verificación

Colocar los originales OULAD en datasets/, siguiendo su README. Cada etapa consume esa fuente común y guarda sus derivados por separado. La auditoría de PSet 1 no modifica CSV; PSet 2 monta ../datasets en solo lectura, comprobado desde Spark.

Instalar dependencias locales desde pset-01/scripts/requirements.txt y seguir los comandos de [PSet 1](pset-01/README.md). Verificar con `python pset-01/scripts/verificar_entregables.py` desde el entorno configurado. El informe [verificacion.json](pset-01/docs/verificacion.json) registra comparaciones entre Markdown, notebook, PDF, PPTX y renderizado de PowerPoint, enlaces y checksums. La [trazabilidad](pset-01/docs/trazabilidad-entregables.md) describe fuentes, formatos y limitaciones.

## Versionado y continuidad

Versionar código, Markdown, notebook final, manifiestos y exportaciones finales. .gitignore excluye datos crudos y voluminosos, secretos, entornos, caches, logs, temporales y backups. Los generadores de contenido respaldan textos distintos antes de reemplazarlos: reconciliar cambios editoriales antes de regenerar desde prompt-codex-psets.md. No había entregables previos en pset-01 o pset-02 al inicio; el encargo original permanece intacto.

Destino de publicación autorizado: [wilmerpuerta/data-science-end-to-end](https://github.com/wilmerpuerta/data-science-end-to-end), carpeta [psets/proyecto/oulad/](https://github.com/wilmerpuerta/data-science-end-to-end/tree/master/psets/proyecto/oulad), dentro del fork existente del curso. Desde un clon, entrar en esa carpeta antes de seguir los comandos del proyecto. La [guía de publicación](pset_2/docs/publicacion-github.md) explica ubicación y alcance; las configuraciones y enunciados del curso se conservan. PSet 2 distingue componentes probados y trabajo pendiente en su README e informes de evidencia.

## Cambio de directorio local

La migración a `MSDS_6003_CD_Erick_Naunay` está comprobada. Ver [correcciones, evidencia y uso desde el IDE](docs/migracion-directorio.md).

Ética del proyecto final: auditoría por discapacidad declarada, revisión de la brecha de L06 y criterios de retirada documentados; interruptor de respaldo y reversibilidad HTTP verificados. El modelo se mantiene y las propuestas requieren revisión humana.
