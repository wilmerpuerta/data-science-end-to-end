# PSet 04: proyecto final de apoyo académico preventivo

Estado: API batch y modelos tempranos implementados, con 84 pruebas completas aprobadas en el entorno del proyecto y en Docker. Control y escenario sintético están ejecutados; el challenger ya se comparó y rechazó por decisión humana; Kestra terminó en SUCCESS. CD/GHCR y rollback técnico verificados; auditoría ética y respaldo demostrados; evaluación de negocio completada (420 frente a 314 Fail, +33,76 % con iguales 920 cupos); Compose único e ingesta fuente→OBT verificados; notebooks y comunicación pendientes.

La [rúbrica original](CD-PSet-4.pdf) exige integrar los PSets 01-04 en una carpeta `proyecto_final/`, con infraestructura, API, pruebas, simulación, monitoreo, reentrenamiento y comunicación. La [extracción del enunciado](enunciado.md) conserva su contenido textual.

## Decisiones acordadas

- Patrón batch: priorización por cohorte completa, con API obligatoria.
- Meta principal acordada: al menos 10 % de mejora relativa en cobertura de Fail frente al modelo estático, con los mismos cupos.
- Apoyo preventivo durante el período en curso, con dos puntos funcionales de detección: semanas 2 y 4.
- Presupuesto reactivo vigente separado y protegido para atender reprobaciones anteriores.
- Propuesta de presupuesto preventivo financiado mediante un adelanto de hasta el 30 % de los cupos reactivos futuros, pendiente de validación institucional y conversión a costos y horas.
- Reducir atención reactiva futura es una hipótesis de valor; una tutoría preventiva no equivale automáticamente a un Fail evitado o a una tutoría reactiva menos.
- La predicción produce riesgo; una política versionada asigna los cupos del lote. Los cupos son propuestas para revisión humana.

## Documentos de preparación

- [Alcance y criterios de negocio](docs/alcance-acordado.md).
- [Semanas 2 y 4, FP y solicitud del 30 %](docs/cortes-y-presupuesto.md).
- [Plan de trabajo y condiciones de aceptación](docs/plan-trabajo.md).
- [Matriz de la rúbrica](docs/matriz-rubrica.md).
- [Recursos y estructura propuesta](docs/recursos.md).

El prototipo usa matrícula-asignatura y capacidad experimental del 10 % por edición sobre elegibles de día 14; no representan capacidad institucional aprobada. El 30 % es un escenario presupuestario. El reparto 25/75 de las pruebas aún no se selecciona para producción. Ya se integraron dbt/Spark, se prepararon las versiones y fixtures y se implementó la API. La carga a Snowflake/Kestra y la simulación temporal de ambos escenarios están verificadas. Ingesta, Spark y MLflow ya están integrados en el Compose único. El siguiente punto es completar notebooks y comunicación. La menor proporción histórica de FP en semana 4 orienta la comparación, sin garantizar el nivel futuro de error. Los modelos tempranos específicos están registrados y desplegados experimentalmente en versión 1; no hay aprobación institucional de uso ni promoción del candidato rechazado.

La entrega se está construyendo en [proyecto_final](../proyecto_final/README.md), con el árbol exacto de la rúbrica. [Cambios y decisiones](../proyecto_final/docs/cambios.md) identifica lo implementado y lo pendiente. Las carpetas anteriores conservarán sus entregas e historial. El champion actual del PSet 03 corresponde al día 56 y no se presentará como un modelo validado para los días 14 o 28.

## Criterio de trabajo

La prioridad es completar `proyecto_final/`. Los laboratorios son una referencia opcional: sus patrones se priorizan cuando encajan y aportan al resultado; las demás decisiones siguen el criterio técnico y de negocio del proyecto. Cada configuración se justifica por los requisitos y la evidencia. Completar los `TODO` de los laboratorios queda fuera del alcance prioritario. Las directrices para continuar se conservan en [AGENTS.md](../AGENTS.md).
