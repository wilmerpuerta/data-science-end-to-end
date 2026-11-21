# 1. Problema y formulación final

**Apoyo académico preventivo con capacidad limitada.** El proyecto prioriza matrículas que podrían terminar en Fail para proponer tutorías durante el período en curso. La Universidad es el escenario de decisión; los datos proceden de The Open University (OULAD).

El criterio del negocio es mejorar al menos **10 % relativo la cobertura de Fail frente al predictor estático, con los mismos cupos**. La simulación original obtiene 420 frente a 314 Fail priorizados con 920 cupos: 106 netos adicionales (+33,76 %). Es evidencia retrospectiva de focalización, no de tutorías realizadas o reprobaciones evitadas.

Fail focalizados con iguales 920 propuestas, base de 1.947 Fail. La mejora relativa es (420/314 - 1), no 33,76 puntos de cobertura.

Figura: Fail focalizados con iguales 920 propuestas, base de 1.947 Fail. La mejora relativa es (420/314 - 1), no 33,76 puntos de cobertura.


| Decisión de formulación | Elección final |
|---|---|
| Unidad y target | Matrícula-asignatura. Tres clases: Approved (Pass/Distinction), Fail y Withdrawn; Fail es la clase de interés. |
| Horizonte | Features congeladas en días 14 y 28; resultado al cierre. Disponibilidad de etiqueta: cierre del módulo +14 días, supuesto explícito. |
| Métricas | AP de Fail como diagnóstico técnico; cobertura y precisión a cupo efectivo para decidir. Personas únicas se informan aparte. |
| Líneas base | Predictor estático para la meta; Dummy/cola administrativa para respaldo. Política reactiva posterior y no actuar, con horizonte separado. |
| Umbral | Ranking por edición, no probabilidad 0,5. K=floor(0,10 × elegibles en día 14); primera ronda floor(0,25 K). |
| Juicio humano | La API propone; tutores revisan contexto y necesidad. No decide sanciones, causas ni la asignación institucional definitiva. |


## Uso operativo del resultado

El modelo prioriza contacto, y la coordinación confirma necesidad, disponibilidad y aceptación antes de asignar la atención. Entre las 920 propuestas, 500 corresponden a no-Fail: la proporción de falsas alertas es 54,35 %, diferente de la FPR poblacional. La mejora se evalúa a capacidad constante y requiere aceptar ese costo de revisión. El piloto deberá medir cuántas propuestas se convierten en contactos y tutorías, y comparar sus resultados con una alternativa de igual capacidad.

**Estado de comunicación:** documentos para revisión. El video todavía no está grabado/publicado y los notebooks finales 01-07 siguen pendientes. Enlace de la demo: **pendiente de publicación**. No se declara cerrada toda la rúbrica.


<!-- SALTO DE PÁGINA -->


# 2. Arquitectura y trazabilidad

Flujo completo del proyecto. Kestra orquesta; Snowflake conserva capas y evidencia; MLflow versiona artefactos. La promoción exige decisión humana.

Figura: Flujo completo del proyecto. Kestra orquesta; Snowflake conserva capas y evidencia; MLflow versiona artefactos. La promoción exige decisión humana.

Se eligió **batch por cohorte completa** porque el presupuesto depende de la edición y de las propuestas previas. Un endpoint por estudiante sin ese contexto permitiría fragmentar cupos. Un servicio online sería útil para consulta, pero tendría que consultar el mismo manifiesto confiable y estado transaccional; no se añadió otra regla de asignación.


| Eslabón | Referencia y control |
|---|---|
| Gold y OBT | PSET2_OULAD.GOLD y ANALYTICS.OBT_FEATURES; SHA de originales, claves por corte y lectura de vuelta. |
| Snapshot | 0a75615bd8ff6b16…: features y outcomes separados; el modelo registra snapshot y split de su entrenamiento. |
| Modelo temprano | Semanas 2/4: runs a6c0b65d… / 048df692…; Registry por corte, alias champion, versión 1. |
| Predicción | PREDICCIONES conserva entrada sin target, salida, run_id, versión, snapshot, split, Gold, política, momento y latencia. |
| Auditoría posterior | MONITOREO, ALERTAS y REENTRENAMIENTOS vinculan plan/lote. La etiqueta se filtra por el reloj simulado antes de unirse. |


La API usa SQLite como registro durable y outbox, con publicación posterior conciliada a Snowflake. Transacción, manifiesto de cohorte y hash de contenido preservan presupuesto e idempotencia. Una solicitud repetida devuelve los IDs, riesgos y versión originales; no consume otro cupo.

Un Compose propio levanta nueve servicios: Kestra, PostgreSQL, dbt, Spark, MLflow, dos API, monitor y tablero. El código de los ejecutores está incorporado a sus imágenes. Solo los workers necesarios montan claves cloud; API y tablero no reciben credenciales Snowflake.


<!-- SALTO DE PÁGINA -->


# 3. Datos y modelo dimensional

Grano de actividad: matrícula-recurso-día. Las dimensiones no multiplican hechos. FACT_ENROLLMENT tiene una fila por matrícula; OUTCOME_ENROLLMENT conserva resultados fuera de las features.

Figura: Grano de actividad: matrícula-recurso-día. Las dimensiones no multiplican hechos. FACT_ENROLLMENT tiene una fila por matrícula; OUTCOME_ENROLLMENT conserva resultados fuera de las features.


| Problema / magnitud | Decisión y verificación |
|---|---|
| 5 fuentes / 10.726.852 filas Raw | Conservar fila de origen, SHA, número de fila y valores vacíos. No eliminar silenciosamente duplicados al cargar. |
| 10.655.280 filas de actividad | Silver/Gold agregan al grano diario: 8.459.320 claves y 39.605.099 clics reconciliados. |
| 1.111 IMD vacíos; 45 fechas de registro vacías | Preservar el faltante; indicador IMD. Registro temporal desconocido no se convierte arbitrariamente en matriculación al inicio. |
| OBT: 108.277 filas × 35 columnas | Cortes 14/28/42/56; unicidad matrícula-corte, poblaciones idénticas a Gold, joins conciliados y sin target/retiro posterior. |


El join de actividad se realiza después de fijar la población elegible. Así, una matrícula sin registros conserva su fila y sus contadores observados en cero; no desaparece del análisis por un inner join. Este orden protege precisamente al grupo que podría requerir contacto temprano y permite distinguir ausencia de eventos de una ausencia real de estudio.

La ingesta comprueba bytes, SHA256, columnas y filas contra manifest.json. Una versión Raw reconciliada se registra como NOOP. Un backfill explícito prepara y valida una tabla temporal antes de publicar el archivo completo en transacción; un error revierte la publicación. No hay streaming porque las fuentes son archivos históricos sin calendario real de llegada.

En la ejecución integrada **2sQlV9Hreu3bWXWi7MtYRE**, Raw, dbt, Spark y verificación terminaron SUCCESS a la primera: 23 modelos y 168 pruebas dbt, cuatro pruebas de perturbación futura y lectura de vuelta completa. Los hashes de los cuatro cortes coinciden con el PSet 02. Spark publica por staging/swap después de comprobar contenido.

Retries: Raw hasta tres intentos, dbt/Spark hasta dos; trabajos exitosos se reutilizan por execution_id. La primera ejecución de integración falló al leer el perfil de dbt desde el directorio sincronizado; se corrigieron su directorio de trabajo y el empaquetado del código. El historial fallido se conserva.


<!-- SALTO DE PÁGINA -->


# 4. EDA, candidatos y selección

El EDA de desarrollo al día 56 usó 16.331 matrículas y 15.482 personas. Encontró 9.219 Approved, 4.918 Fail y 2.194 Withdrawn. Las colas largas de clics motivaron ensayar log1p sin borrar extremos; 432 matrículas sin registros tuvieron 75,69 % Fail frente a 28,88 % con registros. Esa asociación no prueba que la inactividad cause reprobación.


| Familia / baseline | AP Fail CV | Cobertura CV al 10 % |
|---|---|---|
| Dummy | 0,3012 ± 0,0117 | 9,15 % ± 1,50 % |
| Logística | 0,5687 ± 0,0245 | 22,92 % ± 0,80 % |
| Random Forest | 0,5611 ± 0,0301 | 22,57 % ± 1,12 % |
| HGB | 0,5777 ± 0,0273 | 22,81 % ± 0,82 % |
| MLP | 0,5042 ± 0,0283 | 20,09 % ± 1,27 % |
| GaussianNB | 0,5375 ± 0,0273 | 22,78 % ± 1,07 % |
| GPT prompting | 0,3821 ± 0,0394 | 14,87 % ± 1,88 % |


La comparación supervisada usa los mismos cinco folds agrupados por persona y las mismas validaciones completas. Se separan desarrollo y 2014J y se excluyen del desarrollo las personas presentes en esa presentación. Transformaciones aprendidas e imputación se ajustan dentro de cada train-fold. ± es la desviación descriptiva entre pliegues, no un intervalo independiente. Las cifras anteriores corresponden a candidatos iniciales del día 56; no son las métricas operativas de semana 2 o 4.

La AP evalúa el ordenamiento de los casos Fail a lo largo de los umbrales; la cobertura al cupo evalúa la decisión que efectivamente puede financiarse. Una familia puede mejorar el orden global y no identificar más Fail entre las primeras propuestas. Por eso, la selección conserva la cobertura como criterio principal y usa AP, dispersión, costo y trazabilidad para interpretar la conveniencia del candidato.

## Tuning decidido por el negocio

Se probaron 30 configuraciones de Logística, HGB y GaussianNB: **90 en total**. HGB obtuvo la mayor cobertura CV media, 23,40 % (AP 0,5830); el finalista logístico alcanzó 23,24 %. La diferencia de 0,16 puntos es menor que la dispersión HGB de 0,93 puntos: se conserva la selección predeclarada, sin afirmar superioridad estadística estable.

Run final histórico del día 56: **fcd23ae22d6c46ffb41c1e4f23e1c02d**, Registry oulad-apoyo-academico-v2-modelo, versión 1. Tuning HGB: 160 iteraciones, learning_rate 0,02181, 7 hojas, min_samples_leaf 80; early_stopping desactivado. Los modelos tempranos se identifican por separado en la página siguiente.

En 2014J, ya observado antes, HGB focalizó 465 Fail con 872 cupos al día 56 y Logística 477. No se reabre la selección hecha por CV tras mirar ese resultado; se necesita una cohorte prospectiva para contrastar la decisión.

## Prompting y modelo fundacional

Sí fue factible probar GPT mediante prompting: 18 ejemplos del train-fold (seis por clase), probabilidades JSON y la misma validación de los candidatos. No ajusta los pesos del LLM ni equivale a entrenarlo con todas las filas. Su cobertura CV fue 14,87 %; no quedó entre las tres familias a tunear. El costo registrado de esas cinco validaciones fue USD 0,8535, no el costo de un despliegue. La evaluación posterior con la Universidad debe considerar costo-beneficio, latencia, privacidad y dependencia del proveedor; no se afirma SOTA en OULAD.


<!-- SALTO DE PÁGINA -->


# 5. Modelos tempranos y fuga temporal

El modelo histórico del día 56 no se usa para puntuar semanas 2/4. Se reutilizaron HGB específicos del corte temprano, con sus artefactos completos y firmas; no se repitió tuning para escoger un resultado favorable. Los comparadores estáticos conservan las mismas poblaciones y capacidad de cada política.


| Corte / modelo HGB | AP CV | Cobertura CV |
|---|---|---|
| Día 14 estático | 0,3965 | 15,36 % |
| Día 14 longitudinal | 0,4570 | 18,63 % |
| Día 28 estático | 0,4085 | 15,44 % |
| Día 28 longitudinal | 0,4927 | 20,15 % |



| Control de fuga | Aplicación |
|---|---|
| Disponibilidad | Registro al inicio (date_registration ≤0) y retiro no ocurrido al corte. Actividad solo hasta ese día; días negativos y día cero separados. Outcomes/retiro posterior no entran a X. |
| Ventanas | 14 días actuales y 14 anteriores comparables desde día 28. Ausencia de registro no demuestra ausencia de estudio. |
| Preprocesamiento | Imputación, escalado y codificación dentro de cada train-fold; indicadores de faltantes y actividad explícitos. |
| Prueba directa | Perturbar eventos futuros deja inalterada la OBT temprana en los cuatro cortes; joins y claves se verifican antes de publicar. |
| Evaluación | 2014J ya fue examinado en PSet 03. La reserva L08 se excluye por persona del reentrenamiento; no se presenta como nuevo ensayo prospectivo. |


## Artefactos tempranos activos

```json
Día 14: a6c0b65d4e354ceaabfc565c88bfa0c2 | versión 1
Día 28: 048df6920ba747d28d957b052e685666 | versión 1
```

El reparto de dos rondas convierte el calendario en una decisión de capacidad: cada propuesta temprana reduce el saldo disponible para la segunda revisión. La observación adicional puede cambiar el orden de riesgo, pero la reserva anterior se conserva para sostener la continuidad del contacto. El beneficio de anticipar depende también de que exista un tutor disponible y de la aceptación del apoyo; esas variables no están en OULAD y deben medirse antes de adoptar un reparto institucional.

## Elección del calendario, con 920 cupos


| Calendario longitudinal | TP | FP | Lectura de oportunidad |
|---|---|---|---|
| Solo semana 2 | 415 | 505 | Máxima anticipación; no incorpora observación posterior. |
| Dos rondas 25/75 | 420 | 500 | 226 propuestas en semana 2; 694 nuevas en semana 4. |
| Solo semana 4 | 426 | 494 | 11 TP más que semana 2; retrasa todas las propuestas iniciales. |


Las 226 propuestas iniciales incluyen 121 Fail observados posteriormente y se adelantan 14 días respecto de esperar al corte de semana 4. El margen al fin del módulo es 245-255 días en semana 2 y 231-241 en semana 4, según duración del curso OULAD; no es un calendario universitario local. Las alternativas cambian modelos/elegibilidad, y fueron analizadas retrospectivamente: no prueban una política óptima ni el efecto de más datos.


<!-- SALTO DE PÁGINA -->


# 6. Servicio de predicción y contrato

La API recibe la cohorte completa del corte; su manifiesto y base de presupuesto se registran desde una fuente confiable. La carga por alias se resuelve para cada lote nuevo y se fija una versión durante todo el lote. Los identificadores de persona permiten contar atención única aparte de matrícula-asignatura.

## POST /predecir: fragmento ilustrativo del JSON

```json
{"cohorte_id":"demo-comunicacion", "corte_dias":14,
 "matriculas":[{"matricula":"demo-comunicacion-M000",
 "edicion":"demo-comunicacion-edicion",
 "persona":"demo-comunicacion-P000",
 "features": {"studied_credits":60.0, ...}}, ...]}
```

Los puntos suspensivos solo abrevian el documento: **no son un JSON ejecutable**. El archivo docs/ejemplo_api.json contiene manifiesto, solicitud completa de 40 matrículas, respuesta real del servicio aislado y ejemplo 422. Sus IDs son sintéticos y las features son valores de una muestra CI repetidos; no estima calidad del modelo.

## Respuesta observada en el servicio aislado

```json
{"respaldo": false, "nuevas_propuestas": 1,
 "modelo": {"version":"1", "cutoff_day":14, ...},
 "predicciones": [{"matricula":"demo-comunicacion-M000",
   "riesgo_fail": 0.0868027791425706,
   "decision":"proponer_tutoria", ...}, ...]}
```


| Ruta / control | Comportamiento comprobado |
|---|---|
| GET /salud y /modelo | Estado de carga, corte, versión, run y procedencia. Sin credenciales cloud en la API. |
| POST /predecir válido | HTTP 200; 40 respuestas, una propuesta inicial y tres adicionales al día 28, bajo el mismo presupuesto. |
| Contrato inválido | HTTP 422 al omitir studied_credits. También se prueban tipos, categorías, rangos, finitos y ausencia de targets. |
| Consistencia | 409 si cambia un corte ya registrado, falta la ronda previa o cambia su política; cohorte incompleta/duplicada rechazada. |
| Persistencia | Transacción lote/predicciones; reenvío idéntico conserva versión e IDs y no inserta nuevas asignaciones. |


## Rechazo 422 observado

```json
HTTP 422 Unprocessable Entity
loc: [body, matriculas, 0, features, studied_credits]
type: missing
```

El contrato se valida antes de recuperar una respuesta previa o consumir capacidad. Las solicitudes no transportan target ni resultado final; quien llama tampoco puede modificar la cuota de una cohorte existente. El registro confiable y el orden de las rondas son parte del contrato, no decisiones del consumidor.

Ante una respuesta perdida, el consumidor debe reenviar la misma cohorte y corte. Un error 422 exige corregir el contrato; un 409 requiere conciliar el contenido o la secuencia. Cambiar el identificador no constituye una autorización para abrir capacidad adicional.

El ejemplo se ejecutó con la imagen publicada, Registry propio y un SQLite separado, sin carga a Snowflake ni modificación de aliases. El contenedor de prueba se retiró. Las métricas de error/latencia de ese ejercicio no se incorporan a los lotes de negocio.


<!-- SALTO DE PÁGINA -->


# 7. Pruebas, CI/CD y despliegue

**84 pruebas** aprobaron en Python y dentro de la imagen publicada. Cubren contrato, fixture y probabilidades con tolerancia 1e-10, presupuesto compartido, desempates, idempotencia, fallback, ventanas de reentrenamiento, criterios de retirada y publicación Raw transaccional. CI valida además Compose con valores ficticios, sin conectarse a Snowflake o MLflow.

Captura real de GitHub Actions: CI reutilizable y publicación en Success. Revisión 03018cb; run 44781023359, 20-nov-2026. Se conserva la captura completa y su URL en la evidencia.

Figura: Captura real de GitHub Actions: CI reutilizable y publicación en Success. Revisión 03018cb; run 44781023359, 20-nov-2026. Se conserva la captura completa y su URL en la evidencia.


| Código publicado | Modelo servido |
|---|---|
| Cada push/PR ejecuta CI; merge a main publica imagen en GHCR tras probarla. Tag de commit y digest quedan registrados. | Un alias no cambia por publicar código. La promoción exige comparación y decisión humana, y queda auditada. |
| Imagen activa: commit a4fc842a0f38ddf2f4ccba01638f6c67be36f9a3; API, API sintética, monitor, tablero y MLflow comparten digest. | Semanas 2/4 siguen en versión 1; la versión 2 de semana 4 permanece challenger, rechazada. |


Digest activo: <font face="Courier" size="8">sha256:c8c922877eeaa909c9463deaa877e3908451e1e373e5b9eeff10ed7b58ab5c96</font>. El último commit documental también publicó una imagen probada, pero el entorno conserva deliberadamente la referencia inmutable comprobada. Fuente: GHCR y artefactos de Actions.


| Consulta local | Uso |
|---|---|
| localhost:5004 / 8094 | MLflow propio / ejecución y pausa en Kestra. |
| localhost:8004 / 8006 | API control / escenario sintético; /docs conserva el contrato. |
| localhost:8504 | Tablero por escenario, lote y disponibilidad de etiquetas. |


Esta separación permite corregir el servicio y probar su imagen sin convertir cada ajuste de código en un cambio de priorización. Para reproducir una decisión previa se necesitan tanto el artefacto del modelo como la versión del servicio y su política.

**Fuera de CI:** credenciales/roles cloud, ingesta real, restauración del Registry, disponibilidad externa, escala de concurrencia, SLA y efecto de tutorías. Se verificaron localmente ingesta completa, nueve servicios saludables, código incorporado a ejecutores y copia del Registry (825 runs / 20.790 archivos). Ninguna prueba de fixture acredita desempeño prospectivo.


<!-- SALTO DE PÁGINA -->


# 8. Simulación, monitoreo y deriva

Se construyeron ocho despachos de 2014J: cuatro ondas de ediciones completas en días 14-17 y 28-31, con features congeladas 14/28. La demora de 0-3 días es un supuesto de cola. Son ocho lotes, **no ocho semestres independientes**. Antes de la liberación simulada del target no se calcula AP ni se reentrena con sus etiquetas.

AP sobre etiquetas maduras. El eje identifica el despacho, no la fecha de llegada del resultado. Cada punto tiene su referencia CV por corte/módulos; todos los scores servidos siguen en versión 1.

Figura: AP sobre etiquetas maduras. El eje identifica el despacho, no la fecha de llegada del resultado. Cada punto tiene su referencia CV por corte/módulos; todos los scores servidos siguen en versión 1.


| Lote | Corte | N | Nuevas | AP control | AP sintética |
|---|---|---|---|---|---|
| L01 | 14 | 1.369 | 33 | 0,3970 | 0,3970 |
| L02 | 14 | 3.637 | 90 | 0,3872 | 0,3872 |
| L03 | 14 | 2.750 | 67 | 0,3224 | 0,3224 |
| L04 | 14 | 1.475 | 36 | 0,4381 | 0,4381 |
| L05 | 28 | 1.359 | 103 | 0,4315 | 0,4315 |
| L06 | 28 | 3.590 | 273 | 0,3954 | 0,2126 |
| L07 | 28 | 2.684 | 207 | 0,3310 | 0,2310 |
| L08 | 28 | 1.459 | 111 | 0,4339 | 0,4339 |


La inducción afecta L06/L07: permuta vectores completos dentro de edición (semilla 5041+orden) y suma 120 créditos. Conserva IDs, targets y cupos. Modifica también variables estáticas y demografías; estas últimas no se usan como equidad real. Hay 36.646 predicciones, 32 revisiones y 28 alertas (12 control, 16 sintético), con escenarios y presupuestos separados.


| Señal | Ventana y destinatario | Respuesta |
|---|---|---|
| PSI >0,25 | Un lote; equipo de datos | Revisar extracción, cobertura y composición; no promover ni retirar por PSI solo. |
| AP bajo referencia | Dos lotes maduros del mismo corte; modelo/coordinación | Revisar resultado y solicitar un candidato; la aprobación queda separada. |


El umbral AP es media CV -2 desviaciones: regla operativa, no intervalo estadístico. KS/chi-cuadrado complementan el diagnóstico. Los controles también alertan; no se afirma tasa cero de falsas alarmas ni deriva conceptual causal. L07 sintético tuvo una petición atribuida, 0 errores 4xx/5xx y p50=p95=4.920,7 ms del batch: no acredita SLA. En controles históricos los errores no atribuibles quedan NULL, no cero.

Investigar origen, mezcla de módulos y prevalencia orienta la respuesta; la alerta no identifica por sí sola la causa.


<!-- SALTO DE PÁGINA -->


# 9. Reentrenamiento y decisión humana

La revisión madura de L07 sintético disparó el ciclo cuando las etiquetas estaban disponibles (día simulado 283), después de las ocho predicciones. La ventana combina 16.838 filas históricas y 7.538 recientes maduras: **24.376 en total**. Excluye por persona a toda la reserva L08: 1.475 personas, solapamiento cero. No trata control y sintético como cohortes independientes.


| Comparador L08 | Cupos | TP | FP | Cobertura |
|---|---|---|---|---|
| Estático | 147 | 54 | 93 | 14,88 % |
| Modelo vigente v1 | 147 | 77 | 70 | 21,21 % |
| Candidato v2 | 147 | 81 | 66 | 22,31 % |


Se mantuvieron pipeline e hiperparámetros del modelo vigente; cinco folds por persona y un ajuste final, **sin nuevo tuning**. La regla previa exige superar una sigma OOF de la política de dos rondas (1,6598 puntos de cobertura). La mejora fue 1,1019 puntos: cuatro TP adicionales cuando se requieren al menos siete. La AP tampoco mejoró (0,432826 frente a 0,433943).

## Pausa real y rechazo registrado

Kestra 6lcaE9ak8kGv4myx06ZMMw se detuvo en PAUSED. Wilmer Puerta confirmó rechazar por no alcanzar la métrica de reemplazo; la reanudación quedó registrada el 20-nov-2026 a 01:35 UTC (19-nov en Ecuador). Terminó SUCCESS y conservó el alias champion en versión 1. Run del candidato: **e0ca46ddc9a84d7eaeffa750633ee2ce**. No se movieron scores históricos ni se observa un período posterior con un modelo promovido.


| Evento persistido | Evidencia |
|---|---|
| SOLICITADO | Disparador maduro y ciclo identificados. |
| COMPARADO | Modelo vigente, candidato y estático con idénticos cupos. |
| DECISION_SOLICITADA | Propuesta rechazar; pausa de aprobación real. |
| DECIDIDO | RECHAZADO, responsable y motivo; alias operativo conservado. |


La decisión protege al proyecto frente a reemplazos que añaden costo operativo sin una ganancia suficiente bajo su regla previa. Aunque el candidato reduce cuatro falsas alertas con los mismos cupos, esa mejora no alcanza el margen exigido para cambiar el modelo. Conservarlo registrado permite auditar el rechazo y contrastar la regla con evidencia futura.

## Recarga/rollback e interruptor: alcance de la evidencia


| Prueba aislada | Resultado y límite |
|---|---|
| Recarga 1 → 2 → 1 | 120 predicciones sintéticas; misma imagen y contenedor. Versiones con los mismos pesos en un nombre de prueba. Demuestra mecánica; no mejora predictiva ni promoción del candidato rechazado. |
| Respaldo 0 → 1 → 0 | 160 predicciones sintéticas en SQLite propio. Cola administrativa con score técnico constante, cupos 1+3, validación 422 e historial conservados. Activar/desactivar requiere recrear el proceso. |


El fallback usa el Dummy most_frequent histórico; riesgo_fail=0 es una compatibilidad técnica y **no una estimación individual**. Se informa puntuacion_individual=false, respaldo y revisión humana. Las dos pruebas quedaron fuera de Snowflake y del presupuesto de negocio; las instancias se retiraron.


<!-- SALTO DE PÁGINA -->


# 10. Ética, acceso y retirada

El análisis por discapacidad declarada usa solo el control original y resultados maduros. N significa que no consta declaración, no que no existan necesidades. La base de semana 2 se mantiene al calcular cobertura/FPR acumuladas, incluyendo propuestas previas que ya no son elegibles en semana 4.


| Semana 4, control | Base | Fail | Cobertura | FPR |
|---|---|---|---|---|
| N: sin declaración | 8.374 | 1.731 | 21,89 % | 6,95 % |
| Y: declaración | 857 | 216 | 18,98 % | 5,93 % |
| L06, N | 3.291 | 687 | 23,14 % | - |
| L06, Y | 346 | 87 | 14,94 % | - |


El agregado presenta una brecha de -2,91 puntos de cobertura Y frente a N; en L06 llega a **-8,20 puntos** y activa revisión de acceso. No se acepta uso automático de esa onda sin revisar composición por módulo, accesibilidad y necesidades. Una señal no prueba discriminación causal; la falta de dos cohortes persistentes tampoco certifica equidad.


| Señal observable | Acción y responsable |
|---|---|
| Fuera de contrato | Inmediato: 422 y corrección de fuente por el equipo de datos. El fallback no elude el contrato. |
| Carga/firma/modelo inválido | Respaldo administrativo inmediato para lotes nuevos; operación y responsable del modelo corrigen antes de reactivar. |
| Menos TP que el estático | Dos cohortes maduras distintas del mismo corte, tras evaluar reentrenamiento: proponer retirada del ranking. Coordinación y modelo. |
| Brecha >5 pp cobertura o >3 pp FPR | Mínimos 200 casos, 20 Fail y 20 no-Fail/grupo. Un lote: revisar; dos cohortes comparables: proponer suspensión. Coordinación académica. |
| 5xx >1 % con ≥20 solicitudes | Dos lotes consecutivos del mismo corte: restaurar servicio/evaluar respaldo. Operación; el tamaño actual no acredita SLA. |


## Decisiones en elegibles del día 28


| Grupo / N | AP Fail | Nueva propuesta | Ya propuesta | Seguimiento |
|---|---|---|---|---|
| N / 8.250 | 0,3789 | 7,72 % | 2,42 % | 89,85 % |
| Y / 842 | 0,4281 | 6,77 % | 2,61 % | 90,62 % |


AP y tasas de decisión usan elegibles del corte; cobertura/FPR de la tabla superior usan la base inicial. Una AP mayor en Y no garantiza igual acceso: la mezcla de módulos y prevalencia difieren.

Antes del piloto, debe acordarse cómo informar la propuesta, obtener la aceptación y registrar su resolución. Ese seguimiento permitiría identificar si la pérdida de acceso aparece al priorizar, contactar o atender, tres momentos que el score por sí solo no distingue. La Universidad deberá evaluar esa trayectoria por grupo y atender la revisión de L06 antes de ampliar el uso del ranking. El registro debe distinguir una propuesta pendiente de una atención efectivamente realizada.

FP: tiempo/cupo para Universidad y tutores, contacto y posible estigma para el estudiante; puede tratarse de Withdrawn que también necesite apoyo. FN: apoyo oportuno no ofrecido a quien termina en Fail. Los tutores revisan contexto y contactos; el estudiante conserva vías habituales y puede pedir revisión. El módulo institucional de atención, consentimiento y apelaciones no está implementado.


<!-- SALTO DE PÁGINA -->


# 11. Resultado de negocio por lote

La comparación principal es el control original al finalizar ambas rondas: **420 vs 314 TP con 920 cupos**, coberturas 21,57 % vs 16,13 % sobre 1.947 Fail, +33,76 % relativo y +5,44 puntos. Los FP bajan de 606 a 500. Las 106 detecciones netas son matrículas: 257 ganadas menos 151 perdidas, no necesariamente 106 personas.

TP del longitudinal y estático con iguales cupos en cada onda/corte. L07 maduro identifica el disparador; L08 es la reserva de comparación. Todos los puntos son v1: el reentrenamiento rechazado no cambió estos scores.

Figura: TP del longitudinal y estático con iguales cupos en cada onda/corte. L07 maduro identifica el disparador; L08 es la reserva de comparación. Todos los puntos son v1: el reentrenamiento rechazado no cambió estos scores.


| Lote / corte | Cupos acum. | TP long. | TP estático | TP sintét. | Hito posterior |
|---|---|---|---|---|---|
| L01 / 14 | 33 | 19 | 13 | 19 | - |
| L02 / 14 | 90 | 50 | 41 | 50 | - |
| L03 / 14 | 67 | 26 | 26 | 26 | - |
| L04 / 14 | 36 | 26 | 17 | 26 | - |
| L05 / 28 | 136 | 66 | 43 | 66 | - |
| L06 / 28 | 363 | 172 | 132 | 105 | - |
| L07 / 28 | 274 | 105 | 85 | 69 | R: alerta y entreno |
| L08 / 28 | 147 | 77 | 54 | 77 | V: reserva; rechazo |


L05-L08 acumulan las propuestas de L01-L04 de la misma onda: **no sumar ambos cortes**. El agregado final suma las cuatro ondas de semana 4. L03 empata; en L07 sintético hay 69 frente a 73 TP estáticos. El total sintético es 317 frente a 263 (+20,53 %), con pérdida de 103 TP frente al longitudinal del control; no se suman ambos escenarios.

Los TP absolutos varían con el tamaño de la onda y su presupuesto: el valor de L06 no demuestra por sí solo un mejor modelo que en L03. La comparación conserva cohorte, corte y cupos; la revisión operativa considera también los errores y la referencia estática de cada onda. La cobertura facilita interpretar la detección en relación con los Fail disponibles.

La cola administrativa logra 187 TP con 920 cupos. No actuar tiene cero propuestas tempranas. La política reactiva también anticipa cero: asigna 920 casos una vez conocido Fail al cierre+14 simulado, por construcción. Su precisión posterior no es una predicción comparable al horizonte temprano. El longitudinal propone para 893 personas distintas; matrícula y persona se reportan por separado.


<!-- SALTO DE PÁGINA -->


# 12. Presupuesto, límites y siguiente decisión


| Escenario ilustrativo | Cupos tempranos | TP / FP | Saldo reactivo futuro |
|---|---|---|---|
| Prevención independiente K | 920 | 420 / 500 | 920 |
| Solo adelanto 30 % | 274 | 152 / 122 | 646 |
| Prevención K + adelanto | 1.194 | 530 / 664 | 646 |


La bolsa reactiva futura se supone igual a K por edición; el adelanto se redondea dentro de cada edición: 274, no 276 al agrupar todo. La bolsa reactiva vigente se protege y su importe es desconocido. Si no existe prevención financiada, el 30 % solo permite 274 cupos; no financia automáticamente las 920 propuestas del benchmark. Costos por atención, horas y demanda reales no se conocen.

Con asistencia y probabilidad reactiva iguales a uno, adelantar 274 para añadir 110 TP sobre la prevención ya financiada exigiría efectividad 274/110=2,49 para compensar cupos bajo costo unitario igual, fuera de [0,1]. Con efectividad cero no se reduce necesidad y quedan menos cupos futuros. Las 288 sensibilidades son supuestos contables por edición, no efectos causales ni ahorro observado.

## Recomendación: ajustar y validar en un piloto supervisado

Mantener el modelo vigente y la revisión humana; no promover el candidato rechazado. Revisar el acceso de L06 antes de uso institucional, acordar unidad/capacidad y calendario reales, y medir aceptación, atención, costos e impacto con nuevas cohortes. El resultado de focalización a igual capacidad no obliga a ampliar presupuesto ni justifica por sí solo adelantar 30 % o 50 %. El piloto debe poder operar respaldo y detener nuevas propuestas según las señales acordadas.

El piloto debe fijar capacidad, responsables y qué resultado justificaría continuar, ajustar o detener la intervención. Registrar propuestas, contactos, aceptación y atenciones permitirá estimar costos y diseñar una evaluación posterior del efecto del apoyo.

## Limitaciones y pendientes de entrega

2014J fue observado previamente y las ocho ondas no son semestres nuevos. La fecha real de etiquetas y el presupuesto institucional no están disponibles; hay deriva inducida y pocos eventos para SLA. La diferencia CV entre finalistas no demuestra superioridad estable. Faltan validación prospectiva, efecto tutorial y evaluación económica; los notebooks finales 01-07 y el pitch histórico en PDF no están cerrados.

**Demo:** guion de 6:35 min en docs/guion_video.md; grabación y enlace público/accesible todavía pendientes. No se presenta un enlace ficticio. Antes de entregar: grabar, comprobar acceso, insertar URL y revisar esta versión con los notebooks Restart/Run All.


| Pendiente | Cierre requerido |
|---|---|
| Notebooks 01-07 | Ejecutar Restart/Run All, guardar salidas y comprobar trazabilidad. |
| Video / pitch histórico | Grabar demo accesible hasta 7 min; insertar URL; cerrar PDF del pitch histórico. |
| Entrega | Revisar coherencia entre memo, presentación, cinco CSV y repositorio. |


**Repositorio:** github.com/wilmerpuerta/data-science-end-to-end, rama main, psets/proyecto/oulad/proyecto_final. **Anexos:** PSet4_anexos_Puerta_Wilmer.pdf reúne los tres memos históricos y docs/cambios.md. Datos: OULAD, The Open University, CC BY 4.0, DOI 10.1038/sdata.2017.171. Evidencias: cinco CSV de docs/, snapshots y artefactos privados; los números de este memo no requieren nuevas llamadas a un LLM.
