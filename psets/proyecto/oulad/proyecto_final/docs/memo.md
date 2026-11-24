# 1. Problema y formulación final

**Apoyo académico preventivo con cupos limitados.** El proyecto ordena las matrículas según el riesgo de reprobar (Fail), para proponer tutorías durante el período en curso. Cada matrícula representa a un estudiante en una asignatura. La Universidad es el escenario de decisión; los datos proceden de The Open University (OULAD).

El criterio del negocio es **detectar al menos 10 % más casos Fail que el modelo con datos de matrícula, sin aumentar los cupos**. Al añadir actividad digital, la simulación identifica 420 frente a 314 casos con 920 propuestas: 106 adicionales netos (+33,76 %). **2014J ya se había consultado: esta comparación es retrospectiva y no constituye una prueba final independiente.**

Fail focalizados con iguales 920 propuestas, base de 1.947 Fail. La mejora relativa es (420/314 - 1), no 33,76 puntos de cobertura.

Figura: Fail focalizados con iguales 920 propuestas, base de 1.947 Fail. La mejora relativa es (420/314 - 1), no 33,76 puntos de cobertura.


| Decisión de formulación | Elección final |
|---|---|
| Unidad y target | Matrícula en una asignatura. Tres resultados: aprobado, reprobado (Fail) y retirado. Se prioriza el riesgo de Fail. |
| Horizonte | Información disponible en semanas 2 y 4; resultado al cierre. Se supone disponible 14 días después del fin del curso. |
| Métricas | AP de Fail como diagnóstico técnico; cobertura y precisión a cupo efectivo para decidir. Personas únicas se informan aparte. |
| Líneas base | Predictor estático para la meta; Dummy/cola administrativa para respaldo. Política reactiva posterior y no actuar, con horizonte separado. |
| Umbral | Lista ordenada por edición: cupos del 10 % de elegibles en semana 2, redondeados hacia abajo. Se reserva 25 % para la primera ronda. |
| Juicio humano | La API propone; tutores revisan contexto y necesidad. No decide sanciones, causas ni la asignación institucional definitiva. |


## Uso operativo del resultado

La tabla resume qué se decide, cuándo se decide y quién confirma la atención. La cobertura indica qué proporción de todos los Fail aparece entre las propuestas; la precisión indica cuántas propuestas corresponden a Fail. De 920 propuestas, 500 no terminan en Fail: 54,35 % requieren revisión sin confirmar ese resultado. La coordinación debe comprobar necesidad, disponibilidad y aceptación antes de asignar la tutoría. Detectar un caso no demuestra que se haya atendido ni evitado su reprobación.

**Estado de comunicación:** siete notebooks preparados con salidas verificadas. El video aún no se ha grabado ni publicado. Enlace de la demo: **pendiente de publicación**. La entrega conserva pendientes explícitos.


<!-- SALTO DE PÁGINA -->


# 2. Arquitectura y trazabilidad

Flujo completo del proyecto. Kestra orquesta; Snowflake conserva capas y evidencia; MLflow versiona artefactos. La promoción exige decisión humana.

Figura: Flujo completo del proyecto. Kestra orquesta; Snowflake conserva capas y evidencia; MLflow versiona artefactos. La promoción exige decisión humana.

Se procesa **cada grupo completo de matrículas a la vez** (batch), porque los cupos pertenecen a una edición del curso y deben descontar las propuestas anteriores. Procesar estudiantes por separado podría repartir más cupos de los disponibles. El servicio recibe el grupo, calcula el orden de riesgo y propone contactos; una consulta individual tendría que respetar el mismo registro de capacidad.


| Eslabón | Referencia y control |
|---|---|
| Gold y OBT | PSET2_OULAD.GOLD y ANALYTICS.OBT_FEATURES; SHA de originales, claves por corte y lectura de vuelta. |
| Snapshot | 0a75615bd8ff6b16…: features y outcomes separados; el modelo registra snapshot y split de su entrenamiento. |
| Modelo temprano | Semanas 2/4: runs a6c0b65d… / 048df692…; Registry por corte, alias champion, versión 1. |
| Predicción | PREDICCIONES conserva entrada sin target, salida, run_id, versión, snapshot, split, Gold, política, momento y latencia. |
| Auditoría posterior | MONITOREO, ALERTAS y REENTRENAMIENTOS vinculan plan/lote. La etiqueta se filtra por el reloj simulado antes de unirse. |


La tabla vincula cada propuesta con sus datos y modelo. SQLite registra la operación y después la concilia con Snowflake. Reenviar el mismo grupo devuelve la respuesta original y no consume otro cupo; así se recuperan respuestas sin duplicar reservas.

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


La tabla resume riesgos de calidad y controles. Primero se fija quién es elegible y después se une su actividad; quien no registra accesos conserva su fila con contadores en cero. Así no se excluye del análisis a un grupo que podría necesitar contacto. Ausencia de registros no demuestra ausencia de estudio.

Antes de cargar se verifican contenido, tamaño, columnas y filas. Un archivo idéntico ya conciliado no se recarga (NOOP). Una recarga solicitada se valida en una tabla temporal y se publica completa; un error revierte la operación. Se usan lotes porque los archivos son históricos, sin llegada continua de registros.

En la ejecución integrada **2sQlV9Hreu3bWXWi7MtYRE**, Raw, dbt, Spark y verificación terminaron SUCCESS a la primera: 23 modelos y 168 pruebas dbt, cuatro pruebas de perturbación futura y lectura de vuelta completa. Los hashes de los cuatro cortes coinciden con el PSet 02. Spark publica por staging/swap después de comprobar contenido.

Retries: Raw hasta tres intentos, dbt/Spark hasta dos; trabajos exitosos se reutilizan por execution_id. La primera ejecución de integración falló al leer el perfil de dbt desde el directorio sincronizado; se corrigieron su directorio de trabajo y el empaquetado del código. El historial fallido se conserva.


<!-- SALTO DE PÁGINA -->


# 4. EDA, candidatos y selección

La exploración de desarrollo al día 56 comprende 16.331 matrículas: 9.219 aprobadas, 4.918 reprobadas y 2.194 retiradas; corresponden a 15.482 personas. Entre 432 matrículas sin actividad registrada, 75,69 % termina en Fail, frente a 28,88 % con actividad. Esa asociación orienta una revisión de necesidad, pero no demuestra que la falta de acceso cause reprobación.


| Modelo / referencia | Orden de riesgo (AP) | Fail detectados, cupo 10 % |
|---|---|---|
| Dummy | 0,3012 ± 0,0117 | 9,15 % ± 1,50 % |
| Logística | 0,5687 ± 0,0245 | 22,92 % ± 0,80 % |
| Random Forest | 0,5611 ± 0,0301 | 22,57 % ± 1,12 % |
| HGB | 0,5777 ± 0,0273 | 22,81 % ± 0,82 % |
| MLP | 0,5042 ± 0,0283 | 20,09 % ± 1,27 % |
| GaussianNB | 0,5375 ± 0,0273 | 22,78 % ± 1,07 % |
| GPT prompting | 0,3821 ± 0,0394 | 14,87 % ± 1,88 % |


La tabla compara los candidatos iniciales del día 56. Se valida cinco veces, separando personas: ninguna aparece en entrenamiento y validación a la vez. La imputación y el escalado se aprenden solo en el entrenamiento de cada ronda. El signo ± muestra cuánto varía el resultado entre esas cinco validaciones; no es una garantía de desempeño futuro. Estas cifras no corresponden todavía a semanas 2 y 4.

**Cómo leer la tabla:** cobertura es la proporción de Fail detectados al ofrecer cupos al 10 % de las matrículas; cuanto mayor, más casos caben en el mismo presupuesto. AP resume el orden de riesgo en toda la lista, no el porcentaje de tutorías útiles. Se elige por cobertura y se revisan estabilidad, costo y facilidad de operar; una AP mayor por sí sola no resuelve la decisión de negocio.

## Tuning decidido por el negocio

Se ajustaron 30 configuraciones por familia para Logística, HGB y GaussianNB: **90 en total**. HGB detectó en promedio 23,40 % de los Fail; Logística, 23,24 %. La diferencia de 0,16 puntos es menor que la variación de HGB entre validaciones (0,93 puntos). Se mantiene la selección registrada, con esa incertidumbre; no se afirma que HGB sea siempre mejor.

Run final histórico del día 56: **fcd23ae22d6c46ffb41c1e4f23e1c02d**, Registry oulad-apoyo-academico-v2-modelo, versión 1. Tuning HGB: 160 iteraciones, learning_rate 0,02181, 7 hojas, min_samples_leaf 80; early_stopping desactivado. Los modelos tempranos se identifican por separado en la página siguiente.

En 2014J, HGB detectó 465 Fail y Logística 477 con 872 cupos. **Ya conocíamos esa cohorte: no es una evaluación final independiente.** Separar personas o reconstruir el proyecto no borra ese conocimiento. Se conserva la selección por validación de desarrollo; una cohorte futura sin consultar debe confirmar su conveniencia.

## Prompting y modelo fundacional

Sí fue factible probar GPT mediante prompting: 18 ejemplos del train-fold (seis por clase), probabilidades JSON y la misma validación de los candidatos. No ajusta los pesos del LLM ni equivale a entrenarlo con todas las filas. Su cobertura CV fue 14,87 %; no quedó entre las tres familias a tunear. El costo registrado de esas cinco validaciones fue USD 0,8535, no el costo de un despliegue. La evaluación posterior con la Universidad debe considerar costo-beneficio, latencia, privacidad y dependencia del proveedor; no se afirma SOTA en OULAD.


<!-- SALTO DE PÁGINA -->


# 5. Modelos tempranos y fuga temporal

Para proponer apoyo temprano se usan modelos específicos de semanas 2 y 4; el modelo del día 56 no puntúa esos cortes. Se conservan los artefactos y la preparación ya evaluados, sin repetir la búsqueda para escoger un resultado favorable. La tabla compara datos de matrícula frente a matrícula más actividad digital, con las mismas poblaciones y cupos.


| Corte / modelo HGB | Orden de riesgo (AP) | Cobertura CV |
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

**Lectura de las tablas:** añadir actividad digital mejora la detección en ambos cortes de desarrollo. Cada propuesta de semana 2 consume parte del mismo presupuesto y se conserva en semana 4, aunque cambie el orden de riesgo. En la comparación de calendarios, TP son propuestas que después terminan en Fail y FP las que no. Esperar aporta más observación, pero deja menos tiempo para ofrecer apoyo; tutor disponible y aceptación también importan y deben medirse.

## Elección del calendario, con 920 cupos


| Calendario longitudinal | TP | FP | Lectura de oportunidad |
|---|---|---|---|
| Solo semana 2 | 415 | 505 | Máxima anticipación; no incorpora observación posterior. |
| Dos rondas 25/75 | 420 | 500 | 226 propuestas en semana 2; 694 nuevas en semana 4. |
| Solo semana 4 | 426 | 494 | 11 TP más que semana 2; retrasa todas las propuestas iniciales. |


Las 226 propuestas iniciales incluyen 121 matrículas que después terminaron en Fail y permiten contactar 14 días antes. Según el curso OULAD, quedan 245-255 días hasta su fin en semana 2 y 231-241 en semana 4; no es un calendario local. El contraste entre calendarios es retrospectivo y también cambia elegibilidad/modelo: no demuestra una regla óptima ni una reducción causal de errores por esperar.


<!-- SALTO DE PÁGINA -->


# 6. Servicio de predicción y contrato

La API es el servicio que recibe el grupo completo y devuelve las propuestas. Su registro previo fija quién es elegible y cuántos cupos comparte. Para cada lote nuevo se selecciona una versión de modelo, que permanece fija durante todo ese procesamiento. La identificación de personas permite distinguir estudiantes únicos de matrículas en distintas asignaturas.

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

La tabla distingue solicitudes correctas, datos incompletos y conflictos con una operación previa. El código 422 pide corregir los datos; el 409 pide revisar el grupo o el orden de las rondas. El servicio valida antes de reservar cupos. El usuario no puede enviar el resultado final ni cambiar la capacidad de un grupo ya registrado.

Si se pierde una respuesta, el usuario debe reenviar el mismo grupo y corte: recuperará la decisión anterior. Cambiar el identificador no autoriza cupos adicionales. El ejemplo de 40 matrículas comprueba que el servicio responde y respeta el presupuesto; sus identificadores son sintéticos y no sirve para estimar la calidad predictiva del modelo.

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


La primera tabla separa actualizar el programa de reemplazar el modelo. Publicar código no cambia automáticamente el orden de riesgo: se exige una decisión humana. Para auditar una propuesta se conservan programa, modelo y política. La segunda tabla indica las consultas locales.

**Fuera de CI:** credenciales/roles cloud, ingesta real, restauración del Registry, disponibilidad externa, escala de concurrencia, SLA y efecto de tutorías. Se verificaron localmente ingesta completa, nueve servicios saludables, código incorporado a ejecutores y copia del Registry (825 runs / 20.790 archivos). Ninguna prueba de fixture acredita desempeño prospectivo.


<!-- SALTO DE PÁGINA -->


# 8. Simulación, monitoreo y deriva

Se simulan ocho despachos de 2014J: cuatro grupos de ediciones completas en semanas 2 y 4. El retraso de cero a tres días supone una cola; los datos permanecen congelados al corte. **No son ocho semestres independientes.** Antes de conocer el resultado final se revisan datos, sin calcular desempeño ni entrenar con esas etiquetas.

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


La tabla separa datos originales del escenario alterado en L06/L07: se reordenan vectores completos y se añaden 120 créditos, conservando identificadores, resultados y cupos. Es una prueba artificial, no un cambio observado en estudiantes. Hay 36.646 predicciones, 32 revisiones y 28 alertas: 12 en control y 16 en el escenario alterado.


| Señal | Ventana y destinatario | Respuesta |
|---|---|---|
| PSI >0,25 | Un lote; equipo de datos | Revisar extracción, cobertura y composición; no promover ni retirar por PSI solo. |
| AP bajo referencia | Dos lotes maduros del mismo corte; modelo/coordinación | Revisar resultado y solicitar un candidato; la aprobación queda separada. |


**Cómo actuar:** PSI mide cuánto cambia la distribución de los datos; una alerta pide investigar, no retirar automáticamente el modelo. Una AP baja en dos lotes comparables, con resultados finales disponibles, permite solicitar un candidato. Su umbral es una regla operativa basada en la variación histórica, no una garantía estadística. Una sola petición de L07 tardó 4.920,7 ms: no acredita un nivel de servicio; errores históricos no atribuibles quedan desconocidos, no en cero.

Investigar origen, mezcla de módulos y prevalencia orienta la respuesta; la alerta no identifica por sí sola la causa.


<!-- SALTO DE PÁGINA -->


# 9. Reentrenamiento y decisión humana

Cuando estuvieron disponibles los resultados finales de L07 alterado (día simulado 283), se solicitó revisar el modelo. El entrenamiento del candidato usó 16.838 filas históricas y 7.538 recientes: **24.376 en total**. Se excluyeron las 1.475 personas de L08 para comparar sin compartir estudiantes con ese entrenamiento. Esa reserva evita solapamiento directo, pero sigue perteneciendo a 2014J, ya conocido.


| Comparador L08 | Cupos | TP | FP | Cobertura |
|---|---|---|---|---|
| Estático | 147 | 54 | 93 | 14,88 % |
| Modelo vigente v1 | 147 | 77 | 70 | 21,21 % |
| Candidato v2 | 147 | 81 | 66 | 22,31 % |


**Lectura de la tabla:** con los mismos 147 cupos, el candidato detecta 81 Fail frente a 77 del vigente: cuatro adicionales y cuatro falsas alertas menos. La regla previa exige superar la variación histórica (1,6598 puntos de cobertura), equivalente a siete casos más. Solo mejora 1,1019 puntos: no cumple. Se mantuvieron preparación e hiperparámetros, sin nueva búsqueda.

## Pausa real y rechazo registrado

Kestra 6lcaE9ak8kGv4myx06ZMMw se detuvo en PAUSED. Wilmer Puerta confirmó rechazar por no alcanzar la métrica de reemplazo; la reanudación quedó registrada el 20-nov-2026 a 01:35 UTC (19-nov en Ecuador). Terminó SUCCESS y conservó el alias champion en versión 1. Run del candidato: **e0ca46ddc9a84d7eaeffa750633ee2ce**. No se movieron scores históricos ni se observa un período posterior con un modelo promovido.


| Evento persistido | Evidencia |
|---|---|
| SOLICITADO | Disparador maduro y ciclo identificados. |
| COMPARADO | Modelo vigente, candidato y estático con idénticos cupos. |
| DECISION_SOLICITADA | Propuesta rechazar; pausa de aprobación real. |
| DECIDIDO | RECHAZADO, responsable y motivo; alias operativo conservado. |


La tabla de eventos deja constancia de quién solicitó, comparó y decidió. Rechazar conserva la versión 1 y evita asumir el costo de un cambio cuya mejora no alcanza el margen acordado. El candidato queda registrado para auditoría; no se elimina su resultado ni se presenta como una promoción. La decisión humana y su motivo forman parte de la evidencia.

## Recarga/rollback e interruptor: alcance de la evidencia


| Prueba aislada | Resultado y límite |
|---|---|
| Recarga 1 → 2 → 1 | 120 predicciones sintéticas; misma imagen y contenedor. Versiones con los mismos pesos en un nombre de prueba. Demuestra mecánica; no mejora predictiva ni promoción del candidato rechazado. |
| Respaldo 0 → 1 → 0 | 160 predicciones sintéticas en SQLite propio. Cola administrativa con score técnico constante, cupos 1+3, validación 422 e historial conservados. Activar/desactivar requiere recrear el proceso. |


El fallback usa el Dummy most_frequent histórico; riesgo_fail=0 es una compatibilidad técnica y **no una estimación individual**. Se informa puntuacion_individual=false, respaldo y revisión humana. Las dos pruebas quedaron fuera de Snowflake y del presupuesto de negocio; las instancias se retiraron.


<!-- SALTO DE PÁGINA -->


# 10. Ética, acceso y retirada

La revisión de acceso utiliza los datos originales y resultados finales disponibles. N indica que no consta discapacidad declarada; no demuestra ausencia de necesidades. La cobertura y la tasa de falsas alarmas usan la población inicial, incluidas las propuestas de semana 2. La tabla compara a quién se logra priorizar y qué costo de revisión puede recaer en cada grupo.


| Semana 4, control | Base | Fail | Cobertura | FPR |
|---|---|---|---|---|
| N: sin declaración | 8.374 | 1.731 | 21,89 % | 6,95 % |
| Y: declaración | 857 | 216 | 18,98 % | 5,93 % |
| L06, N | 3.291 | 687 | 23,14 % | - |
| L06, Y | 346 | 87 | 14,94 % | - |


La cobertura del grupo Y queda 2,91 puntos por debajo del grupo N en el total y **8,20 puntos en L06**: hay que revisar acceso, composición y necesidades antes de aplicar esa onda. FPR significa proporción de propuestas entre quienes no terminan en Fail; no es la proporción de falsas alertas dentro de la lista. La diferencia observada requiere revisión, pero no demuestra por sí sola discriminación causal.


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


La tabla inferior muestra cómo se distribuyen las decisiones entre quienes siguen elegibles al día 28. Una AP mayor en Y no garantiza igual acceso. Sus denominadores difieren de los de cobertura/FPR de la tabla superior; no deben interpretarse como la misma tasa.

La tabla central fija cuándo corregir datos, activar respaldo o proponer suspender el ranking y quién revisa. El piloto debe registrar propuesta, contacto, aceptación y atención, para localizar dónde se pierde acceso. La revisión de L06 debe cerrarse antes de ampliar el uso institucional.

FP: tiempo/cupo para Universidad y tutores, contacto y posible estigma para el estudiante; puede tratarse de Withdrawn que también necesite apoyo. FN: apoyo oportuno no ofrecido a quien termina en Fail. Los tutores revisan contexto y contactos; el estudiante conserva vías habituales y puede pedir revisión. El módulo institucional de atención, consentimiento y apelaciones no está implementado.


<!-- SALTO DE PÁGINA -->


# 11. Resultado de negocio por lote

Al terminar las dos rondas, añadir actividad digital permite proponer apoyo a **420 casos Fail frente a 314, con los mismos 920 cupos**. La cobertura pasa de 16,13 % a 21,57 %: +5,44 puntos o +33,76 % relativo. Las falsas alertas bajan de 606 a 500. Son 106 matrículas adicionales netas (257 ganadas menos 151 perdidas), no necesariamente 106 personas.

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

**Cómo leer gráfico y tabla:** TP cuenta propuestas que terminan en Fail; FP, las que tienen otro resultado. Cada fila compara el mismo grupo, corte y cupos. Un grupo grande puede tener más TP solo por su capacidad; no demuestra un mejor modelo. La cobertura mide detección respecto de todos sus Fail. Estos datos conocidos orientan un piloto, sin garantizar desempeño futuro.

La cola administrativa logra 187 TP con 920 cupos. No actuar tiene cero propuestas tempranas. La política reactiva también anticipa cero: asigna 920 casos una vez conocido Fail al cierre+14 simulado, por construcción. Su precisión posterior no es una predicción comparable al horizonte temprano. El longitudinal propone para 893 personas distintas; matrícula y persona se reportan por separado.


<!-- SALTO DE PÁGINA -->


# 12. Presupuesto, límites y siguiente decisión


| Escenario ilustrativo | Cupos tempranos | TP / FP | Saldo reactivo futuro |
|---|---|---|---|
| Prevención independiente K | 920 | 420 / 500 | 920 |
| Solo adelanto 30 % | 274 | 152 / 122 | 646 |
| Prevención K + adelanto | 1.194 | 530 / 664 | 646 |


La tabla compara tres decisiones presupuestarias, no tres mejoras del mismo tamaño. Se supone una bolsa reactiva futura de 920 cupos; adelantar 30 % por edición permite 274 y deja 646 para después. La bolsa reactiva vigente se protege. Si no existe presupuesto preventivo independiente, ese adelanto no financia las 920 propuestas del análisis principal. Los costos por atención, horas y demanda reales son desconocidos.

Añadir el adelanto a una prevención ya financiada aumenta la detección de 420 a 530 Fail: 110 adicionales, a cambio de mover 274 cupos futuros. Con asistencia completa y costo unitario igual, ni una eficacia de 100 % compensaría esos 274 cupos solo con los 110 casos adicionales (274/110=2,49). Si el apoyo no tiene efecto, no baja la necesidad futura. Las 288 sensibilidades exploran supuestos; no son ahorro ni efecto causal observado.

## Recomendación: ajustar y validar en un piloto supervisado

Mantener el modelo vigente y la revisión humana; no promover el candidato rechazado. Revisar el acceso de L06 antes de uso institucional, acordar unidad/capacidad y calendario reales, y medir aceptación, atención, costos e impacto con nuevas cohortes. El resultado de focalización a igual capacidad no obliga a ampliar presupuesto ni justifica por sí solo adelantar 30 % o 50 %. El piloto debe poder operar respaldo y detener nuevas propuestas según las señales acordadas.

El piloto debe fijar capacidad, responsables y qué resultado justificaría continuar, ajustar o detener la intervención. Registrar propuestas, contactos, aceptación y atenciones permitirá estimar costos y diseñar una evaluación posterior del efecto del apoyo.

## Limitaciones y pendientes de entrega

**2014J ya se había consultado y no es una prueba final independiente.** Las cifras retrospectivas pueden estar influidas por ese conocimiento. Repetir la ejecución, purgar personas o reservar L08 no elimina la limitación. El siguiente contraste debe fijar reglas y modelos antes de conocer una cohorte futura. Tampoco se han medido efecto tutorial, costo real o capacidad institucional. Los siete notebooks están verificados; faltan el video y el pitch histórico en PDF.

**Demo:** guion de 6:35 min en docs/guion_video.md. La grabación y su enlace accesible siguen pendientes. Antes de entregar, grabar, comprobar el acceso e insertar la URL; no se publica un enlace ficticio.


| Componente | Estado / cierre requerido |
|---|---|
| Notebooks 01-07 | Siete ejecutados con kernel nuevo, salidas guardadas y auditoría PSet1 conciliada. |
| Video / pitch histórico | Grabar demo accesible hasta 7 min; insertar URL; cerrar PDF del pitch histórico. |
| Entrega | Revisar coherencia entre memo, presentación, cinco CSV y repositorio. |


**Repositorio:** github.com/wilmerpuerta/data-science-end-to-end, rama main, psets/proyecto/oulad/proyecto_final. **Anexos:** PSet4_anexos_Puerta_Wilmer.pdf reúne los tres memos históricos y docs/cambios.md. Datos: OULAD, The Open University, CC BY 4.0, DOI 10.1038/sdata.2017.171. Evidencias: cinco CSV de docs/, snapshots y artefactos privados; los números de este memo no requieren nuevas llamadas a un LLM.
