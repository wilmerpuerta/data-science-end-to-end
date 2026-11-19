# Efecto de la revisión de PSet 1 sobre PSet 2

Revisión del 15-nov-2026. Se contrastaron el memo vigente del PSet 1, contratos, código y evidencia de PSet 2. Se recalcularon poblaciones, Fail y cupos desde studentInfo.csv, studentRegistration.csv y courses.csv; no se ejecutó el pipeline ni se consultó Snowflake. El [informe de comprobaciones](impacto-revision-pset1.json) registra alcance, resultados y hashes de entradas revisadas.

## Conclusión

Los tres gaps y el límite actualizado de cinco páginas del memo no exigen modificar Kestra, dbt, Spark, infraestructura, fuentes ni las 35 columnas de OBT_FEATURES. La implementación ya conserva los insumos necesarios. Esta revisión es una comprobación local de compatibilidad, no una nueva ejecución cloud ni una validación de modelos o políticas.

El cambio principal es hacer explícita la conexión entre los datos preparados y la evaluación de negocio futura. El README y el contrato ya incorporan, por autorización posterior del usuario del 15-nov-2026, las tres políticas y sus reglas de capacidad. El memo técnico actual es compatible con los nuevos objetivos; una frase de enlace sería una mejora editorial opcional, sin ampliar su alcance ni sustituir resultados observados.

## Trazabilidad de los cambios

| Cambio en PSet 1 | Soporte existente en PSet 2 | Efecto necesario o recomendado |
|---|---|---|
| Cobertura de futuras reprobaciones con los mismos cupos | OBT identifica matrícula, edición, estudiante y corte; OUTCOME_ENROLLMENT conserva target_fail y target_class aparte | Calcular N y K por edición y unir etiquetas solo para evaluación. No filtrar la OBT al 10 % ni añadir target como predictor. Aclaración documental incorporada |
| Semanas de anticipación potencial | module_presentation_length y cutoff_day ya están en OBT; se conserva identidad para registrar primera selección | La fecha/día de primera selección se generará en la simulación futura. No hace falta otra fuente ni modificar la OBT. El cierre aproxima la referencia; no hay fechas reales de tutoría/publicación de notas |
| Tres políticas comparables | Contrato con 11 variables estáticas y 16 de actividad; etiquetas separadas en Gold | Estática usa el grupo estático; longitudinal lo amplía. Reactiva consulta Fail después del cierre de la misma cohorte. Falta implementar su evaluación futura, no el pipeline de preparación |
| Igual capacidad y múltiples listas | OBT por matrícula-corte, con edition_key e id_student | Fijar K por edición para el caso principal; presupuesto total B común para cuatro listas; repeticiones consumen cupos y matrícula cubierta cuenta una vez. Son reglas de decisión futuras, no transformaciones ELT |
| MVP y límites institucionales | PSet 2 termina con datos preparados, sin modelos; solo ingiere los cinco CSV OULAD | El producto predictivo, evaluación y simulación siguen pendientes. D2L/WiFi quedan fuera; no se añade captura institucional ni se atribuyen intencionalidad, ahorro o eficacia educativa |
| Memo de PSet 1 hasta cinco páginas | Requisito independiente del memo técnico PSet 2 | PSet 2 conserva máximo seis páginas según su enunciado; no se modifica ese límite |

## Comprobaciones ejecutadas

Las 19 comprobaciones locales aprobaron: SHA de los tres CSV pequeños, poblaciones y cupos, esquema de 35 columnas, grupos disjuntos, separación de target, campos para anticipación, etiquetas disponibles por clave, cortes coincidentes, evidencia temporal/lectura previa y huellas de 99 archivos del runtime frente a la reproducción limpia.

| Corte | Matrículas elegibles | Futuras Fail | Suma de cupos por edición |
|---|---:|---:|---:|
| 14 | 27.881 | 6.972 | 2.779 |
| 28 | 27.307 | 6.972 | 2.719 |
| 42 | 26.795 | 6.972 | 2.672 |
| 56 | 26.294 | 6.972 | 2.619 |

Las matrículas coinciden con el [informe OBT](obt-verificacion.json), con la auditoría PSet 1 y con sus [métricas de negocio](../../pset-01/docs/metricas-negocio.json). El presupuesto se obtiene sumando floor(0.10 × N) por edición, no aplicando floor una sola vez al total. Los cupos de distintos cortes de esta tabla no son automáticamente un presupuesto acumulado: el análisis de cuatro listas debe fijar B común antes de comparar.

OBT conserva 108.277 filas y 35 columnas. El margen de 25,4-30,4 semanas al día 56 se reconstruye desde courses.csv. Es margen disponible hasta el cierre, no anticipación conseguida por un modelo. La cota ideal de 37,6 % y la meta +10 % tampoco son desempeño obtenido.

## Contrato que debe respetar la evaluación futura

1. Usar la misma cohorte elegible del día 56 y K por edición para la comparación principal. La reactiva puede cubrir casos después del cierre y no recibe capacidad ilimitada.
2. Separar cobertura preventiva de posterior; conservar todos los resultados históricos. La comparación estática/longitudinal mide aporte de variables; compararlas con reactiva mide oportunidad preventiva.
3. Registrar versión, algoritmo, política, matrícula, corte, puntuación cuando corresponda y selección. La primera selección y las revisiones repetidas son salidas futuras de simulación, no columnas que deban existir hoy en OBT_FEATURES.
4. Construir conjuntos de predictores mediante listas permitidas; nunca usar etiquetas, retiro futuro o una tabla retrospectiva como variables de entrada. IDs y campos de auditoría no son automáticamente predictores.
5. Comprobar disponibilidad histórica de atributos y maduración de etiquetas, ediciones compatibles y estudiantes separados antes de entrenar. Las pruebas temporales ya ejecutadas protegen agregaciones de actividad; no acreditan por sí solas todas esas condiciones.
6. Aprender imputación, codificación y otros ajustes solo con entrenamiento. Documentar tratamiento de recencia desconocida, desempates, cupos pequeños e incertidumbre antes de consultar el test final.

Estas reglas no asignan nuevos requisitos a PSet 3 o PSet 4 ni amplían PSet 2 a entrenamiento, intervención o streaming.

## Aclaraciones documentales aplicadas y alcance de esta revisión

- [README](../README.md): explicación del objetivo revisado, tres políticas, misma capacidad, margen temporal, separación entre preparación y simulación y exclusiones del MVP.
- [Contrato de datos](contrato-datos.md): separación explícita entre columnas existentes y futuras salidas de la simulación, K frente al presupuesto B, métricas y validación aún pendiente.
- [Memo técnico](../memo-pset2.md): compatible; una mención a las tres políticas sería opcional. Cualquier edición posterior de su fuente deberá regenerar y verificar el PDF de seis páginas.

El diagnóstico inicial agregó este informe y su evidencia. Posteriormente, el usuario autorizó aplicar las aclaraciones al README y al contrato y publicar las revisiones de PSet 1 y PSet 2 en el destino existente. Se aplicaron las aclaraciones sin modificar los artefactos de ejecución ni reconstruir tablas. Las pruebas de modelos, utilidad de listas, capacidad institucional y efecto de tutorías siguen pendientes. La [guía de publicación](publicacion-github.md) registra destino y alcance; los hashes originales del diagnóstico identifican las entradas antes de estas aclaraciones.
