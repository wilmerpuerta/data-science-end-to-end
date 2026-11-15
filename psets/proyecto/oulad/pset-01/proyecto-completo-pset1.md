# Proyecto completo del PSet 1

Wilmer Puerta · Revisión del 15 de noviembre de 2026

Estado: revisión de tres observaciones docentes. Auditoría y preparación de datos verificadas; modelos, simulación de políticas e intervenciones pendientes.

# 1. Ideas de Proyectos

## 1.1. Predicción temprana del riesgo de reprobación y seguimiento de la actividad digital para priorizar el acompañamiento académico: estudio con OULAD.

## 1.2. Detección de segmentos compatibles con fibrilación auricular para priorizar la revisión en programas de monitoreo cardiovascular.

## 1.3. Predicción del crecimiento anual de ingresos por cliente para priorizar oportunidades comerciales en telecomunicaciones.

## **1.1. Predicción temprana del riesgo de reprobación y seguimiento de la actividad digital para priorizar el acompañamiento académico: estudio con OULAD.**

### **1.1.1. Idea:**

Desarrollar un prototipo de alerta temprana con OULAD [1] para evaluar si las características longitudinales de interacción digital mejoran la identificación de estudiantes que posteriormente reprueban un módulo, frente al uso exclusivo de características estáticas. El contexto será una universidad hipotética con capacidad limitada de acompañamiento académico.

El prototipo actualizará el riesgo en las semanas 2, 4, 6 y 8 y mostrará su evolución para apoyar la priorización de tutorías. Estas semanas corresponden a la ventana de observación temprana seleccionada.

### **1.1.2. Problema:**

**Negocio.** Se simula un seguimiento que espera a la reprobación para revisar al estudiante. La decisión es a quién revisar antes del cierre con los mismos cupos. Se medirán casos cubiertos, cobertura preventiva y semanas de anticipación potencial. Es un proceso hipotético, sin atribuirlo como práctica comprobada a la USFQ o a la mayoría de universidades.

**Ciencia de datos.** Se compararán regresión logística multinomial y Random Forest con antecedentes estáticos frente a los mismos algoritmos enriquecidos con interacción digital. La hipótesis admite mejora pequeña o nula. Los registros digitales no acreditan intención, motivación ni una causa de la dificultad.

### **1.1.3. Predicción:**

Para cada estudiante-módulo-edición activo en el corte, se estimará la probabilidad del resultado final: reprobación (`Fail`), retiro (`Withdrawn`) o aprobación (`Pass`/`Distinction`). La prioridad será el riesgo de reprobación. Se utilizarán únicamente datos disponibles hasta cada corte; el retiro del módulo se distinguirá del abandono institucional.

Se evaluarán PR-AUC, precisión y recobrado para reprobación, entrenando con ediciones anteriores y probando con posteriores. La meta provisional es detectar un 10% más de casos, en términos relativos, frente al modelo estático en la semana 8, con igual capacidad de atención. Los cortes anteriores mostrarán anticipación; la mejora deberá comprobarse.

### **1.1.4. Datos:**

OULAD es un dataset público anonimizado, con acceso y descarga confirmados por el equipo. Se utilizarán `studentInfo.csv` para antecedentes y resultado final; `studentVle.csv` para interacciones diarias; y `vle.csv`, `courses.csv` y `studentRegistration.csv` para contextualizar recursos, duración y elegibilidad. Se construirán indicadores quincenales de actividad, inactividad y tendencia a partir de los campos documentados en [2].

La auditoría descriptiva local documenta volumen, faltantes, uniones y estudiantes únicos; queda pendiente validar cobertura semántica y particiones temporales. Se excluirá información futura y se preservará la atribución requerida por CC BY 4.0. La capacidad tutorial será simulada, pues no existen costos ni resultados de intervenciones confirmados. La descripción de los datos y su licencia se documentan en [1], [2].

### **1.1.5. Acción:**

Se compararán tres políticas con el mismo K por edición: reactiva tras conocer Fail, estática con antecedentes iniciales y longitudinal con esos antecedentes más actividad hasta el corte. La evaluación principal fija la cohorte del día 56 y K = floor(0.10 × N). El coordinador valida cupos y el tutor revisa contexto antes de decidir apoyo.

La simulación conserva los resultados académicos observados. Cada revisión repetida consume capacidad y cada matrícula cuenta una vez en cobertura acumulada; se informan personas únicas. Tutorías realizadas, efecto sobre aprobación, costos, deserción y transferencia institucional quedan para una fase posterior. El MVP usa exclusivamente OULAD y excluye D2L y WiFi institucionales.

### **1.1.6. Riesgos:**

- **Técnico - Mejora insuficiente (alta).** Las variables longitudinales podrían no superar al baseline. Se contrastarán resultados bajo condiciones equivalentes y con incertidumbre; si no aportan valor, se conservará el enfoque estático y se reportará el resultado.

- **Técnico - Fuga de información (crítica).** Datos futuros o estudiantes repetidos podrían inflar el desempeño. Se auditarán fechas y particiones; si se detectan problemas, se reconstruirá la evaluación antes de concluir.

- **Técnico - Interpretación incorrecta de la actividad (alta).** Menos clics podrían reflejar cambios del calendario o registros incompletos. Se revisarán cobertura y contexto del módulo; las señales ambiguas se ajustarán o excluirán.

- **Negocio - Capacidad tutorial poco realista (alta).** Las listas podrían exceder los recursos disponibles. Se analizarán presupuestos y contactos repetidos; una adopción futura requerirá validar la capacidad con tutores y ajustar la frecuencia de atención.

- **Negocio - Intervenciones sin impacto (alta).** Detectar riesgo podría no mejorar el resultado académico. Un piloto posterior comparará intervenciones y resultados; hasta entonces, las conclusiones se limitarán a predicción y focalización potencial.

- **Adopción - Alertas injustificadas o sobrecarga (alta).** Los errores podrían afectar la confianza o perjudicar a ciertos grupos. Se revisarán errores por subgrupos y carga de alertas; se ajustará la priorización manteniendo revisión humana y acceso habitual al apoyo.

## **1.2. Detección de segmentos compatibles con fibrilación auricular para priorizar la revisión en programas de monitoreo cardiovascular.**

### **1.2.1. Idea:**

Proponer un sistema de apoyo que identifique segmentos de señal cardíaca compatibles con fibrilación auricular y los priorice para revisión profesional. Su aplicación prevista sería un programa de monitoreo de pacientes con enfermedad cardiovascular crónica, coordinado por una aseguradora o un prestador de salud.

El proyecto se enfocará en la detección de una alteración presente en el registro. La prevención de complicaciones será un beneficio potencial que requerirá evaluación posterior. El entorno de desarrollo, las herramientas y la incorporación de una simulación IoT se definirán durante el desarrollo de la propuesta.

### **1.2.2. Problema:**

**Negocio.** En un programa hipotético de monitoreo cardiovascular, revisar grandes volúmenes de registros puede superar la capacidad disponible y demorar la identificación de segmentos relevantes. La organización necesita focalizar la revisión profesional para reconocer posibles episodios de fibrilación auricular y decidir oportunamente qué casos requieren valoración adicional.

**Ciencia de datos.** Se plantea clasificar segmentos de señal cardíaca según su compatibilidad con fibrilación auricular, utilizando anotaciones reales como referencia. Se evaluará si esa clasificación mejora la selección de registros para revisión frente a una estrategia de referencia por definir. La detección automatizada apoyará el juicio profesional sin establecer por sí sola un diagnóstico.

### **1.2.3. Predicción:**

La unidad de análisis será un segmento de señal cardíaca asociado a un paciente. La salida será una puntuación de compatibilidad con fibrilación auricular presente en ese segmento. La fuente candidata dispone de anotaciones de ritmo que permitirían construir el resultado objetivo [3], [4], sujeto a verificar su contenido y calidad.

Durante el desarrollo se definirán ventanas, características, algoritmos, métricas, baseline y evaluación con pacientes distintos entre entrenamiento y prueba. El criterio de negocio será identificar más segmentos relevantes con capacidad de revisión comparable. La meta cuantitativa se establecerá tras inspeccionar los datos; no se compromete anticipación de urgencias ni ahorro económico demostrado.

### **1.2.4. Datos:**

Se ha identificado Icentia11k como fuente pública candidata. Su documentación describe señales ECG de un monitor portátil y anotaciones de ritmos, incluida fibrilación auricular [3], [4]. **El equipo aún no dispone de los datos descargados ni ha inspeccionado señales o anotaciones.** La adquisición y auditoría quedan para la etapa de desarrollo.

Se verificará cobertura, calidad, condiciones de uso y representatividad para pacientes con enfermedad cardiovascular crónica. No se dispone de costos ni resultados de intervenciones. Se explorará después la simulación de transmisión o datos de dispositivos IoT; cualquier componente sintético se identificará y no sustituirá la evaluación con señales y etiquetas reales.

### **1.2.5. Acción:**

El sistema propondría una lista priorizada de segmentos para que un profesional revise la señal y determine si corresponde una valoración adicional. El umbral y la capacidad de revisión se definirán posteriormente. La organización conservaría sus procedimientos habituales de atención y el profesional mantendría la decisión clínica.

La utilidad se evaluaría por la identificación de segmentos relevantes, los casos omitidos y la carga de revisión frente al baseline acordado. Las alertas repetidas deberán contabilizarse. La reducción de tiempos, costos o complicaciones requeriría mediciones adicionales y una evaluación de las intervenciones, fuera de lo demostrable únicamente con clasificación retrospectiva.

### **1.2.6. Riesgos:**

- **Técnico - Datos insuficientes o inadecuados (alta).** La fuente podría no aportar señales y etiquetas utilizables. Se inspeccionará una muestra y su cobertura durante el desarrollo; si falla, se acotará el conjunto o se buscará otra fuente antes de entrenar.

- **Técnico - Evaluación optimista (alta).** Segmentos del mismo paciente en entrenamiento y prueba podrían inflar el desempeño. Se verificará la separación por paciente al diseñar la evaluación; cualquier solapamiento indebido exigirá rehacerla.

- **Técnico - Simulación IoT poco representativa (alta).** Datos sintéticos, ruido o pérdidas simuladas podrían no reproducir dispositivos reales. Se contrastarán con señales observadas durante el desarrollo; la simulación quedará limitada a pruebas técnicas si no puede validarse su realismo.

- **Negocio - Exceso de alertas o casos omitidos (alta).** El sistema podría sobrecargar la revisión o pasar por alto segmentos relevantes. Se evaluarán errores y carga frente al baseline; se ajustará la priorización o se descartará su utilidad si no mejora el proceso.

- **Negocio - Detección sin beneficio posterior (alta).** Priorizar registros podría no reducir complicaciones ni costos. Un piloto posterior deberá evaluar acciones y resultados; mientras tanto, las conclusiones se limitarán a desempeño y focalización potencial.

- **Adopción - Población poco representativa (alta).** Los pacientes del dataset podrían diferir del programa previsto. Se revisarán características y documentación disponibles; si no se acredita representatividad, se limitará la conclusión a la población observada y se requerirá validación externa.

## **1.3. Predicción del crecimiento anual de ingresos por cliente para priorizar oportunidades comerciales en telecomunicaciones.**

### **1.3.1. Idea:**

Desarrollar un modelo que estime la probabilidad de crecimiento, estabilidad o disminución de los ingresos efectivos de cada cliente durante el siguiente año calendario. Se utilizará el historial mensual de ingresos por producto o servicio de una empresa de telecomunicaciones para apoyar la asignación de recursos comerciales.

La evolución de ingresos y la composición de servicios permitirán caracterizar oportunidades de expansión. La clasificación por tamaño económico complementará la predicción, con segmentos por definir. El crecimiento incluirá ajustes tarifarios, aumentos en servicios existentes y servicios que comienzan a generar ingresos, conforme al criterio comercial descrito por el equipo.

### **1.3.2. Problema:**

**Negocio.** La empresa necesita distribuir ejecutivos, campañas y atención especializada entre clientes con distinto potencial de crecimiento. El ingreso actual identifica el tamaño de una cuenta, pero no determina su evolución futura. Incorporar esa perspectiva permitiría focalizar los recursos disponibles; el proceso actual de asignación deberá documentarse antes de evaluar su mejora.

**Ciencia de datos.** Se plantea una clasificación de tres resultados futuros utilizando tendencias, variabilidad y composición mensual de ingresos, junto con cantidad de servicios con ingresos y antigüedad observable. Se evaluará si el modelo mejora la identificación de clientes que crecen frente a una regla sencilla basada en tendencia histórica, por definir durante el desarrollo.

### **1.3.3. Predicción:**

Para cada cliente activo al cierre de un año, se estimarán las probabilidades de crecimiento, estabilidad y disminución de sus ingresos acumulados del año siguiente respecto al año de referencia. La banda de estabilidad y el tratamiento de historiales parciales o bases nulas se definirán con análisis de datos y criterio comercial.

La evaluación será temporal, con ventanas comparables: por ejemplo, aprender con información de 2020 y resultados de 2021, evaluar con información de 2021 y resultados de 2022, y después pronosticar 2023. Se medirán F1-macro y precisión y recobrado de crecimiento. Los años son ilustrativos; tres años de historia limitan las transiciones anuales evaluables.

### **1.3.4. Datos:**

El equipo confirma disponer de registros internos de ingresos efectivos por cliente, producto o servicio y mes durante tres años. Se verificará el identificador de cliente, fechas, continuidad, definición de cartera activa y consistencia de categorías. El ingreso total se obtendrá agregando los servicios de cada cliente en cada período.

Queda pendiente auditar volumen, calidad, faltantes, ajustes contables y permisos de uso académico y confidencialidad. Se distinguirán ingreso cero, registro ausente y salida del cliente. No se requieren reclamos ni NPS. La fuente es empresarial interna, informada por el equipo; su identificación documental y restricciones se completarán sin divulgar información confidencial.

### **1.3.5. Acción:**

Al iniciar el año, el responsable comercial utilizaría las probabilidades junto con el tamaño económico y la composición de servicios para priorizar cuentas. Podría asignar ejecutivos senior, ampliar atención o diseñar campañas y ofertas proactivas. La intensidad de la gestión dependerá de la capacidad disponible y del juicio comercial.

La utilidad inicial será identificar más clientes que posteriormente crecen con un presupuesto comercial comparable al baseline; la meta cuantitativa se definirá tras inspeccionar los datos. Se distinguirá crecimiento observado de ingreso incremental causado por la intervención, cuya demostración requeriría un piloto posterior con un grupo de comparación adecuado.

### **1.3.6. Riesgos:**

- **Técnico - Pocas transiciones anuales (alta).** Tres años podrían no cubrir suficientes ciclos para generalizar. Se verificará la cobertura temporal y la estabilidad de resultados; si resulta insuficiente, se ampliará el historial o se limitarán las conclusiones al período evaluado.

- **Técnico - Crecimiento aparente por historial parcial (alta).** Comparar pocos meses de ingresos con un año completo podría inflar el crecimiento. Se analizarán antigüedad y meses observados; los clientes recientes se tratarán por separado o mediante una comparación ajustada y documentada.

- **Técnico - Calidad y fuga de información (alta).** Faltantes, cambios de categorías o variables posteriores al corte podrían distorsionar resultados. Se auditarán registros y fechas; se corregirán las agregaciones y se reconstruirá la evaluación cuando corresponda, manteniendo las salidas reales como parte del resultado.

- **Negocio - Crecimiento sin respuesta a la gestión (alta).** Un cliente podría aumentar ingresos por tarifas u otros factores aun sin intervención. Un piloto posterior evaluará el efecto comercial incremental; hasta entonces, la conclusión se limitará a identificar potencial y focalizar cuentas.

- **Negocio - Priorización poco rentable (alta).** Las cuentas con mayor probabilidad de crecer podrían aportar incrementos pequeños o exigir demasiados recursos. Se analizarán importes, carga y costos cuando estén disponibles; se ajustará la asignación sin equiparar probabilidad de crecimiento con rentabilidad.

- **Negocio - Cambios tarifarios o de mercado (alta).** Nuevas condiciones podrían alterar los patrones históricos. Se revisarán resultados por período y cambios de política comercial; ante degradación, se actualizará el modelo y se recalibrará la estrategia de priorización.

- **Datos y adopción - Restricciones de uso (alta).** La disponibilidad interna podría no implicar autorización académica. Se confirmarán permisos y medidas de anonimización; si no se autoriza el uso, se limitará el alcance a datos permitidos o se reconsiderará la viabilidad.

# **2. Comparación y selección de la idea más viable**

## **2.1. Metodología de comparación**

Se comparan las tres ideas con los seis criterios establecidos, utilizando **Alto (3), Medio (2) y Bajo (1)**. Alto indica una condición favorable y suficientemente sustentada para diseñar el proyecto; Medio refleja una condición plausible con verificaciones relevantes pendientes; Bajo corresponde a una limitación que impide sostener su viabilidad actual. Las calificaciones son juicios de diseño basados en la información disponible, no resultados de experimentación.

Los criterios tienen el mismo peso y se suman sobre un máximo de 18 puntos. En caso de empate se prioriza la menor incertidumbre para construir y evaluar el proyecto, revisando acceso a datos, target, evaluación y alcance. El valor y la acción se califican por su utilidad y concreción potenciales; ninguna idea ha demostrado todavía impacto causal en una organización.

## **2.2. Matriz comparativa y justificación**

| Criterio | Idea 1: acompañamiento académico | Idea 2: fibrilación auricular | Idea 3: crecimiento de ingresos |
|---|---|---|---|
| **Valor de negocio** | **Medio (2).** Mejoraría la focalización de tutorías, pero la institución es hipotética y no se han confirmado capacidad, costos ni necesidades operativas. | **Medio (2).** Podría mejorar la revisión de registros; falta validar la necesidad y el beneficio operativo con un prestador o aseguradora. | **Alto (3).** Se vincula directamente con ingresos y asignación de recursos de una empresa real, bajo un criterio comercial descrito por el equipo. El beneficio incremental sigue pendiente de prueba. |
| **Acceso a datos** | **Alto (3).** OULAD está descargado y su acceso público está confirmado; la auditoría descriptiva local está documentada; resta validación temporal y de cobertura. | **Medio (2).** Icentia11k está identificado y documentado, pero el equipo todavía no lo ha descargado ni inspeccionado. | **Medio (2).** El equipo dispone de tres años de registros, pero falta confirmar autorización de uso académico y condiciones de confidencialidad. |
| **Target** | **Alto (3).** El resultado final está documentado y permite distinguir reprobación, retiro y aprobación [1], [2]. | **Alto (3).** La fuente documenta anotaciones de fibrilación auricular [3], [4]. La construcción de etiquetas por ventana deberá verificarse al inspeccionar los datos. | **Alto (3).** El cambio anual de ingresos es reconstruible con las mediciones históricas disponibles, sujeto a continuidad, banda de estabilidad y tratamiento de historiales parciales. |
| **Acción** | **Medio (2).** Se propone priorizar revisión y contacto tutorial; la capacidad y el proceso institucional son simulados. | **Medio (2).** Se propone priorizar segmentos para revisión profesional; faltan capacidad, umbral y validación del flujo clínico. | **Alto (3).** Existen decisiones concretas de asignación de ejecutivos, campañas y ofertas. Su implementación y presupuesto deberán acordarse con la empresa. |
| **Evaluación** | **Alto (3).** Está definida la comparación estática/longitudinal, los cortes temporales y las métricas con presupuesto comparable. Es evaluable retrospectivamente. | **Medio (2).** Las anotaciones permiten evaluar detección, pero ventanas, baseline y métricas todavía están por definir. | **Medio (2).** Puede contrastarse la predicción con resultados anuales observados; tres años ofrecen pocas transiciones temporales para evaluar estabilidad. |
| **Alcance** | **Alto (3).** Dos clasificadores, cuatro cortes y características agregadas permiten acotar un MVP con preparación de datos, modelo, despliegue demostrativo y monitoreo. | **Medio (2).** El procesamiento de ECG, la selección de segmentos y la posible simulación IoT añaden complejidad todavía no dimensionada. | **Alto (3).** Una clasificación anual con datos tabulares y una salida de priorización comercial permite acotar un MVP; no requiere integrar CRM ni ejecutar campañas reales. |
| **Total / 18** | **16** | **13** | **16** |

La puntuación de target refleja que el resultado existe o puede reconstruirse; no implica que las etiquetas hayan sido auditadas. El alcance Alto de las ideas 1 y 3 presupone un MVP demostrativo, cuyo producto y entorno se definirán en la propuesta. La validación de ahorro, reducción de reprobación o incremento comercial atribuible a intervenciones requeriría pilotos posteriores.

## **2.3. Decisión y justificación de la selección**

**Se selecciona la idea 1: predicción temprana del riesgo de reprobación para priorizar el acompañamiento académico.** La decisión ha sido acordada por el equipo. Aunque las ideas 1 y 3 empatan con 16 de 18 puntos, se aplica el criterio de desempate de menor incertidumbre para construir y evaluar el proyecto: OULAD ya está descargado, el resultado está documentado y la comparación estática/longitudinal está delimitada.

La idea 1 ofrece la combinación más favorable de datos accesibles, un target observable, una acción concreta de revisión tutorial y un alcance acotado. Su valor potencial consiste en focalizar mejor el acompañamiento académico. La evaluación retrospectiva permitirá comparar predicciones y priorización con capacidad equivalente; la auditoría descriptiva se documenta en el apartado de evidencia local; continúa pendiente validar la cobertura semántica.

La selección no presupone que el modelo alcanzará la mejora relativa del 10% ni que las tutorías reducirán efectivamente la reprobación. El proceso institucional será simulado y la meta predictiva deberá comprobarse. Estas limitaciones están identificadas y permiten mantener un alcance evaluable sin depender de un piloto institucional para completar el proyecto académico.

**La idea 3 conserva una aplicación empresarial directa y queda como alternativa para un desarrollo posterior.** Su principal limitación es la profundidad temporal: tres años de ingresos mensuales no equivalen a tres ejemplos anuales completos por cliente, porque cada ejemplo requiere información previa y un año posterior observado. Con ventanas anuales comparables, el esquema planteado permite una transición inicial para entrenamiento y otra para evaluación, lo que limita comprobar estabilidad entre años.

Un mayor número de clientes puede aportar observaciones, pero no reemplaza la diversidad de ciclos temporales. También quedan pendientes la autorización de uso académico y la auditoría de continuidad de los registros. Ampliar la historia fortalecería la evaluación de la idea 3; con los datos actuales podría realizarse una evaluación inicial, reconociendo estas restricciones. Su valor comercial no elimina esa incertidumbre frente a la idea 1.

**La idea 2 permanece como una oportunidad válida, con menor preparación actual:** falta adquirir e inspeccionar las señales y definir el diseño de evaluación. Su menor puntuación refleja esas dependencias y la complejidad por dimensionar, no una menor importancia del problema de salud.

La propuesta detallada de la sección 3 desarrolla la idea 1 seleccionada.

# **3. Propuesta del proyecto seleccionado**

**Título:** Predicción temprana del riesgo de reprobación mediante características longitudinales de actividad digital para priorizar el acompañamiento académico.

Esta sección respalda el memo de cinco páginas y el pitch de seis diapositivas. La revisión del 15-nov-2026 incorpora objetivo de negocio calculable, tres políticas con igual capacidad y alcance explícito del MVP. Los descriptivos y la preparación de datos están verificados; el rendimiento de los modelos y la simulación de políticas siguen pendientes.

## **3.1. Problema de negocio y formulación de ciencia de datos**

### **3.1.1. Situación actual, afectados y oportunidad**

Se plantea una universidad hipotética con capacidad limitada de revisión. El proceso de referencia simulado espera a conocer la reprobación para ofrecer revisión posterior. No se presenta como una práctica confirmada de la USFQ, de The Open University ni de la mayoría de universidades.

En OULAD hay 7.052 Fail de 32.593 matrículas originales, 21,64 %. El dato cuantifica esta copia histórica de 2013-2014, no una tasa institucional actual. Un Fail no acredita deserción posterior. La unidad de intervención simulada es revisión de una matrícula estudiante-módulo-edición; se informan personas únicas para controlar matrículas múltiples.

El valor inmediato para un patrocinador sería disponer de una lista preventiva evaluada con cupos explícitos y oportunidad temporal. La información digital permite observar patrones de interacción; no demuestra compromiso, intención ni necesidades individuales. El tutor conserva la valoración del contexto y las vías habituales de apoyo.

### **3.1.2. Objetivos y pregunta de investigación**

**Objetivo de negocio:** cubrir más futuras reprobaciones con los mismos cupos y cuantificar cuántas semanas antes del cierre puede priorizarse su revisión. Se reportarán casos cubiertos, cobertura preventiva, casos por cada 100 revisiones, omisiones y personas únicas. La hipótesis de que las tutorías mejoren la aprobación pertenece a una fase institucional posterior.

**Objetivo analítico:** evaluar si añadir actividad longitudinal mejora la cobertura frente a antecedentes estáticos, con los mismos algoritmos, población, presupuesto y corte. Regresión logística multinomial y Random Forest constituyen las familias comparables. Se contrastará una mejora provisional de +10 % relativo de TP al día 56, admitiendo resultados negativos.

**Pregunta:** ¿cuántas matrículas que finalmente reprueban incluye cada política con el mismo K y cuántas semanas antes del cierre puede revisarlas? Las tres políticas son reactiva, estática y longitudinal. La primera contrasta el momento de atención; las otras dos aíslan el aporte digital.

### **3.1.3. Unidad, población, target y horizonte**

| Elemento | Definición propuesta |
|---|---|
| **Unidad de predicción** | Una matrícula estudiante-módulo-edición. El mismo estudiante puede tener varias matrículas; su identificador sirve para vinculación y control de evaluación, no como predictor. |
| **Población inicial** | Matrículas registradas hasta el inicio oficial del módulo. Esta delimitación permite comparar con una estimación estática inicial; las inscripciones posteriores se cuantificarán y quedarán fuera del análisis principal. |
| **Elegibilidad por corte** | Matrículas de la población inicial que no se hayan retirado al finalizar el día del corte. Quienes se retiren después permanecerán con su resultado futuro correspondiente. |
| **Target** | Resultado final del mismo módulo: `Fail` → reprobación; `Withdrawn` → retiro; `Pass` o `Distinction` → aprobación. Las categorías proceden del resultado documentado en OULAD [1], [2]. |
| **Salida** | Probabilidades de las tres categorías. La probabilidad de reprobación será la señal principal para ordenar la revisión. Retiro no equivale a aprobación ni demuestra abandono definitivo de la universidad. |
| **Cortes** | Final de los días 14, 28, 42 y 56 desde el inicio. La información disponible hasta ese día se utilizará para una revisión posterior al corte. |
| **Horizonte** | Desde cada corte hasta el cierre del mismo módulo. Las ocho semanas son una ventana temprana, no la duración completa del curso; el horizonte se calculará por edición. |

La fecha futura de retiro y el resultado final se reservarán para construir etiquetas y evaluar resultados. Para determinar elegibilidad solo se comprobará si un retiro ya había ocurrido al corte; no se incorporará su fecha futura al vector de características. Los resultados inexistentes o inválidos se investigarán y no se convertirán automáticamente en reprobación.

### **3.1.4. Comparación de modelos y referencias**

Se compararán regresión logística multinomial y Random Forest, cada uno con antecedentes disponibles al inicio y con los mismos antecedentes más actividad digital hasta el corte. Los modelos longitudinales podrán ajustarse por corte. El score estático no recibe información de actividad; el estado de registro solo delimita elegibilidad, igual para ambas versiones.

La comparación principal puntúa ambos modelos al día 56 sobre la misma cohorte. Esto aísla el aporte de variables, sin afirmar que un modelo estático no pudiera utilizarse antes. El baseline principal de rendimiento es el estático del mismo algoritmo; la política reactiva espera al resultado final y no requiere pronosticarlo. Una regla de recencia queda como sensibilidad adicional, sin sustituir las tres políticas solicitadas por el profesor.

Se fijarán parámetros, desempates y políticas de ausencia de actividad antes de consultar la prueba final. Las notas de evaluaciones quedan fuera para aislar interacción digital. No se atribuye al modelo longitudinal superioridad sobre todos los sistemas de seguimiento académico posibles.

### **3.1.5. Evaluación técnica y éxito operativo**

Las métricas principales de negocio son casos cubiertos, cobertura preventiva y anticipación potencial. Para cada política, TP cuenta matrículas seleccionadas que finalmente son Fail; el resultado final se consulta al evaluar, no al predecir. Cobertura preventiva (%) = 100 × TP seleccionados antes del cierre / Fail elegibles. También se informan precisión@K = TP/K, omisiones y personas únicas. En la reactiva se separa cobertura posterior de cobertura preventiva; esta última es cero por definición del escenario.

La evaluación principal fija la cohorte elegible al día 56 y K = floor(0.10 × N) por edición para las tres políticas. En el histórico completo hay 26.294 elegibles, 6.972 Fail y 2.619 cupos. La suma de min(K, Fail) por edición es 2.619: cota ideal de cobertura 37,6 %. Es un límite de capacidad, no resultado del modelo ni meta de desempeño. Se recalcularán estas cantidades en la prueba reservada. Sensibilidad de capacidad: 5 % y 20 %, fijada antes de comparar.

La meta provisional es +10 % relativo de TP longitudinal frente a TP estático: 100 × (TP longitudinal - TP estático) / TP estático. Si TP estático = 0, el porcentaje es indefinido y se informa diferencia absoluta. Al compartir denominador Fail y presupuesto K, también se compara cobertura. La referencia reactiva puede seleccionar Fail conocidos después del cierre y no debe presentarse artificialmente como incapaz de cubrirlos.

Anticipación potencial = (duración de la edición - día de primera selección) / 7. La copia contiene ediciones de 234-269 días; al día 56 hay un margen de 25,4-30,4 semanas. La anticipación de los TP se resumirá con mediana y rango intercuartílico y con casos cubiertos antes del cierre, usando su primera selección. Un caso no detectado no se elimina de la cobertura para favorecer la métrica temporal. No se conoce fecha real de tutoría o de comunicación del resultado, por lo que el cierre es una referencia aproximada.

PR-AUC para Fail frente al resto, calibración, precisión/recobrado y matriz de confusión respaldan la evaluación técnica. Se fijará la implementación de PR-AUC. Se reportarán resultados por edición y corte, con diferencias absolutas, relativas e incertidumbre mediante remuestreo agrupado por estudiante cuando sea viable. Los cortes anteriores tienen poblaciones distintas; no se atribuyen automáticamente sus diferencias a una mejora del modelo.

### **3.1.6. Umbral, acción y juicio humano**

El umbral será la última puntuación que cabe en K. Se priorizan omisiones por la oportunidad perdida; las falsas alertas consumen cupos, con costos relativos por validar institucionalmente. El tutor revisaría contexto y contactos previos para decidir orientación, tutoría o derivación. El modelo no determina causas ni sanciona.

El resultado inmediato será una lista priorizada acompañada de actividad reciente, variación respecto al corte anterior e identificación de información insuficiente. Estas señales describirán asociaciones y no explicaciones causales. Los estudiantes que no aparezcan en la lista conservarían las vías habituales de apoyo.

## **3.2. Viabilidad técnica y de datos**

### **3.2.1. Fuente, acceso y cobertura**

OULAD es la fuente principal. El equipo confirma descarga y acceso, y la copia local cuenta con auditoría descriptiva y checksums. Su publicación describe siete módulos y 22 ediciones de 2013-2014, 32.593 registros estudiante-módulo-edición y 10.655.280 registros de interacción diaria [1]. Estas cifras describen la publicación. Los conteos locales y las poblaciones elegibles se presentan separadamente en la evidencia local.

| Fuente | Acceso y contenido previsto | Cobertura y restricciones por verificar |
|---|---|---|
| `studentInfo.csv` | Archivo local presente y auditado descriptivamente. Antecedentes y `final_result`, que aporta la etiqueta. | Una fila por matrícula; categorías, duplicados, faltantes y disponibilidad real al inicio. No tratar una variable como inicial solo por estar en esta tabla. |
| `studentVle.csv` | Archivo local presente y auditado descriptivamente. Fecha relativa, recurso y cantidad de clics [2]. | Agregación diaria por estudiante y recurso; volumen por edición, cobertura, ausencia de actividad y registros fuera de rango. |
| `vle.csv` | Archivo local presente y auditado descriptivamente. Características del recurso para contextualizar la actividad. | Consistencia de claves y tipos entre ediciones; no asumir idéntica oferta digital en todos los módulos. |
| `courses.csv` | Archivo local presente y auditado descriptivamente. Módulo, edición y duración. | Una fila por edición; fechas y duración para determinar horizonte y disponibilidad de etiquetas históricas. |
| `studentRegistration.csv` | Archivo local presente y auditado descriptivamente. Registro y retiro. | Una fila por matrícula; utilizar fechas de forma compatible con el corte y revisar inconsistencias. |
| `assessments.csv` y `studentAssessment.csv` | Identificadas en OULAD; no requeridas para el modelo principal. | Uso eventual para contexto; su contenido no se añadirá sin documentar temporalidad y nueva comparación. |
| Capacidad, costos e intervenciones tutoriales | No disponibles ni confirmados. | Se requieren registros institucionales para evaluar impacto real. Los cupos del estudio son supuestos de simulación. |

La publicación y la documentación oficial describen el esquema y su licencia CC BY 4.0 [1], [2]. Se mantendrá la atribución y se trabajará con identificadores anonimizados. La existencia de una fuente pública no elimina la necesidad de revisar calidad y representatividad. No se incorporarán movilidad física, datos privados universitarios ni información externa para identificar estudiantes.

### **3.2.2. Preparación y características**

La auditoría descriptiva ya generó inventario, clases, matrículas, personas únicas, faltantes y comprobaciones de claves. El PSet 2 validó las uniones y conservó población y clics al consolidar actividad. La cobertura semántica y exactitud externa siguen sin acreditarse. Los registros ausentes se distinguen de actividad real cero.

Los antecedentes candidatos incluyen educación previa, intentos, créditos y contexto de matrícula. Aunque estén presentes en OULAD, debe verificarse su disponibilidad histórica al inicio antes de entrenar. Un campo ambiguo se excluye o se declara supuesto comprobable. Los identificadores no se usan para memorizar estudiantes; la incorporación de atributos demográficos exige justificación y revisión de errores por subgrupos.

El PSet 2 ya calculó clics acumulados y quincenales, días activos, recencia, variedad de recursos y cambio entre ventanas, con filtro temporal por corte. El primer corte no tiene comparación entre dos quincenas completas y mantiene NULL; recencia sin registros también queda NULL. La actividad previa al inicio se conserva separada y los contadores cero describen ausencia de registros, no desinterés.

La OBT de preparación no incorpora target ni retiro como predictores. Imputación, escalado, codificación o selección aprendidos se ajustarán únicamente con entrenamiento y se versionarán junto al modelo. El diseño del MVP conserva la misma transformación en inferencia y mantiene la prueba final independiente.

### **3.2.3. Validación temporal y control de información futura**

Se reservarán ediciones posteriores compatibles para prueba y se entrenará con ediciones previas del mismo módulo y período de inicio cuando existan. Una etiqueta de entrenamiento solo será válida si el módulo histórico ya había concluido antes de la predicción simulada. El año de inicio por sí solo no garantiza ese orden: se verificará también la duración y el momento de disponibilidad del resultado.

Dentro del histórico admisible se separará validación para ajustes, agrupando por estudiante y, cuando la cobertura lo permita, respetando el orden de ediciones. La evaluación principal se realizará con estudiantes no utilizados para ajustar el modelo; los repetidos entre entrenamiento y prueba se excluirán de la prueba principal y se contabilizarán. Todos los cortes de una misma matrícula permanecerán en la misma partición.

La auditoría determinará qué pares de ediciones permiten este diseño sin fuga. No se forzará la inclusión de todos los módulos. Si la cobertura es insuficiente, se acotará el estudio y se explicará su población de validez. La escasez de ediciones limita la certeza de generalización incluso si existen muchas filas de actividad.

### **3.2.4. Implementación y factibilidad**

El trabajo se desarrolla en Python desde VS Code con dependencias fijadas. El PSet 2 construyó Kestra, Snowflake, dbt y Spark, con 23 modelos, 168 pruebas dbt aprobadas y OBT_FEATURES de 108.277 filas y 35 columnas. La reproducción limpia mantuvo las mismas cuatro huellas por corte. Esto acredita preparación, conservación de población y controles temporales; no acredita un clasificador entrenado ni el beneficio de la política.

Se ajustarán y evaluarán regresión logística multinomial y Random Forest con las dos configuraciones. Se medirán tiempos y recursos de entrenamiento e inferencia; la compatibilidad de pares temporales y disponibilidad histórica de todos los atributos sigue por validar. Separar etiquetas maduras, estudiantes y transformaciones aprendidas es condición de la evaluación. Las métricas de negocio descriptivas se derivan con calcular_metricas_negocio.py, sin entrenamiento ni cargas cloud.

## **3.3. Viabilidad de negocio**

### **3.3.1. Cambio del proceso y responsables**

La referencia de negocio se define a partir del proceso descrito en el correo al profesor: esperar al resultado de reprobación y revisar después. Se simulan dos alternativas preventivas: modelo estático y modelo longitudinal. La existencia de OULAD permite reconstruir decisiones, pero no acredita que una universidad concreta aplique ese proceso.

| Política | Información permitida | Selección y momento |
|---|---|---|
| Reactiva | Resultado final conocido después del cierre | Hasta K Fail de la misma cohorte, con desempate estable prefijado; anticipación preventiva cero |
| Estática | Antecedentes disponibles al inicio | Top K por P(Fail) al día 56; sin interacción digital |
| Longitudinal | Los mismos antecedentes y actividad hasta el corte | Top K por P(Fail) al mismo día 56, con igual población y K |

La selección reactiva consulta Fail únicamente después del cierre. No usa ese resultado como predictor temprano ni recibe cupos ilimitados. Se mantienen los resultados académicos históricos en las tres simulaciones. La comparación estática/longitudinal evalúa focalización; la comparación con reactiva evalúa la oportunidad de revisión antes del cierre.

El coordinador académico valida cupos, el tutor revisa contexto y decide apoyo, y el responsable analítico controla calidad y evaluación. El MVP no contacta estudiantes ni ejecuta sanciones. El score es una prioridad para revisión, no una determinación de causas ni de intención del estudiante.

### **3.3.2. Capacidad y simulación de la decisión**

El caso principal usa una lista por política al día 56 o, para la reactiva, tras el cierre, con K fijado por edición desde la cohorte del día 56. Así se comparan 2.619 cupos en el histórico descriptivo, no cuatro presupuestos preventivos contra uno reactivo. El costo por revisión se supone uniforme; no se convierte a horas ni dinero sin datos institucionales.

El análisis complementario de las semanas 2, 4, 6 y 8 fijará previamente un presupuesto total B por edición para cada política y las reglas de reparto o reserva. Los cupos usados en cada corte satisfacen suma de revisiones <= B. Cada repetición consume un cupo y cada matrícula cuenta una vez en cobertura acumulada. No se dará a la política longitudinal capacidad adicional por actualizar cuatro listas. Se informarán personas únicas y reservas no utilizadas.

Las poblaciones y K por corte de la auditoría original son descriptivos y no constituyen automáticamente el presupuesto acumulado de la simulación. Una política reactiva puede gastar su B tras el cierre; su cobertura posterior se reporta aparte. La simulación cambia listas y momentos de selección, manteniendo fijos los resultados observados y sin inventar participación ni efectos de tutorías.

### **3.3.3. Métricas de valor y límites de la evidencia**

| Resultado | Validable retrospectivamente con OULAD | Límite |
|---|---|---|
| Casos cubiertos y cobertura preventiva | TP antes del cierre / Fail de la cohorte | Una selección no acredita contacto o tutoría realizada |
| Rendimiento de cupos | TP por cada 100 revisiones, omisiones y falsos positivos predictivos | La reactiva conoce el resultado y se interpreta por separado |
| Anticipación potencial | Semanas entre primera selección y cierre aproximado | No es fecha de inicio de dificultad ni de comunicación de notas |
| Carga de seguimiento | Cupos, repeticiones, primeras detecciones y personas únicas | No equivale a horas, personal o costo real |
| Mejora de aprobación o reducción de deserción | Fuera del MVP actual | Requiere una intervención y una población institucional posterior |

Sin institución participante se validan preparación, reglas de selección, calidad predictiva, cobertura, anticipación y carga simuladas. No se pueden demostrar aceptación, capacidad operativa real, efecto académico de tutorías, ahorro ni transferencia a la USFQ. La hipótesis de que ofrecer apoyo mejora la aprobación se reserva para una fase posterior y no es requisito para cerrar el PSet 1 ni el MVP académico.

El patrocinio solicitado consiste en respaldar una prueba de concepto reproducible y designar referentes que validen la utilidad del proceso y los cupos hipotéticos. Una evaluación negativa es informativa: se reportará la incertidumbre, conservará el baseline o revisará el alcance antes de recomendar un piloto.

## **3.4. Riesgos y respuestas previstas**

- **R1. Aporte longitudinal insuficiente - Técnico; severidad alta.** **Supuesto:** las nuevas características mejoran la focalización de forma consistente. **Verificación:** comparación emparejada por algoritmo y corte, diferencias absolutas y relativas e incertidumbre por edición. **Respuesta:** reportar el resultado negativo, conservar el baseline cuando corresponda y no justificar complejidad adicional sin evidencia.

- **R2. Información futura en características o entrenamiento - Técnico; severidad crítica.** **Supuesto:** toda entrada y etiqueta histórica usada para ajustar el modelo era conocida en la fecha simulada. **Verificación:** auditoría de cortes, fechas de retiro, finalización de ediciones, particiones y transformaciones. **Respuesta:** corregir el conjunto, reconstruir modelos y retirar conclusiones obtenidas con fuga.

- **R3. Falta de actividad confundida con falta de datos - Técnico; severidad alta.** **Supuesto:** los resúmenes representan actividad registrada comparable. **Verificación:** cobertura por edición y recurso, duplicados, faltantes y cambios de calendario. **Respuesta:** distinguir estados desconocidos, excluir fuentes o ediciones inconsistentes y mostrar información insuficiente en lugar de asignar riesgo sin sustento.

- **R4. Transferencia limitada - Técnico y de negocio; severidad alta.** **Supuesto:** las relaciones se mantienen en ediciones posteriores y poblaciones pertinentes. **Verificación:** evaluación por módulo, período y subgrupos con volumen suficiente. **Respuesta:** restringir el alcance declarado, recalibrar o solicitar validación externa antes de una adopción institucional.

- **R5. Capacidad y carga irreales - Negocio; severidad alta.** **Supuesto:** la revisión propuesta es viable para los tutores. **Verificación:** sensibilidad de capacidad, contactos repetidos y, en una futura adopción, tiempos reales de revisión. **Respuesta:** ajustar frecuencia, listas y reglas de seguimiento; no presentar eficiencia monetaria sin datos de costos.

- **R6. Detección sin efecto del apoyo - Negocio; severidad alta.** **Supuesto:** identificar antes permite una intervención útil y aceptada. **Verificación:** piloto posterior con comparación de políticas, participación y resultados. **Respuesta:** limitar la conclusión a predicción y focalización, y revisar el servicio de acompañamiento antes de ampliar su uso.

- **R7. Errores desiguales o pérdida de confianza - Adopción; severidad alta.** **Supuesto:** las alertas son comprensibles y sus errores no perjudican desproporcionadamente a ciertos grupos. **Verificación:** análisis de falsos positivos y negativos por subgrupos y revisión del lenguaje de la interfaz; consulta a tutores en una etapa posterior. **Respuesta:** ajustar variables o reglas, mantener juicio humano y evitar etiquetas sancionatorias.

- **R8. Procesamiento o cobertura incompatibles con el MVP - Técnico y de alcance; severidad media-alta.** **Supuesto:** los archivos pueden procesarse y existen suficientes ediciones compatibles. **Verificación:** inventario y primera ejecución con medición de recursos. **Respuesta:** limitar módulos con criterios de calidad definidos antes de mirar resultados; preservar la comparación estática/longitudinal y documentar la menor generalización.

## **3.5. Alcance y MVP**

### **3.5.1. Producto propuesto**

MVP previsto: selector de edición, corte y capacidad, modelo y transformaciones versionados, listas priorizadas con señales disponibles, evolución de puntuaciones y reporte comparativo de las tres políticas. El reporte mostrará casos cubiertos, cobertura, rendimiento de cupos, anticipación potencial y carga, distinguiendo resultados observados, supuestos y metas.

La demostración se ejecutará con OULAD en un entorno controlado separado del entrenamiento. El resultado final se mostrará únicamente en una vista de evaluación retrospectiva; no entrará a los predictores. Entradas inválidas impedirán emitir una predicción normal. La forma de interacción puede ser un reporte navegable o aplicación local, sin comprometer una integración institucional. La preparación de datos ya está implementada en PSet 2; entrenamiento, evaluación y simulación continúan pendientes.

### **3.5.2. Etapas y evidencias de terminación**

| Etapa | Trabajo y evidencia verificable |
|---|---|
| **DATOS** | Inventario, diccionario, claves y reglas de elegibilidad; reporte de cobertura, calidad y exclusiones; subconjunto reproducible. |
| **EXPLORACIÓN / FEATURES** | Análisis de clases y actividad por edición; construcción de antecedentes y ventanas; comprobaciones de que cambiar datos futuros no altera características de un corte anterior. |
| **MODELO** | Comparación estática/longitudinal con regresión logística y Random Forest, validación documentada, prueba reservada y reporte de métricas e incertidumbre. |
| **DESPLIEGUE** | Modelo y transformaciones versionados, inferencia desde entradas validadas y demostración ejecutable mediante instrucciones de instalación y uso. |
| **MONITOREO** | Registro de versión, faltantes, volúmenes, distribución de puntuaciones y tamaño de listas; desempeño cuando se incorporen etiquetas observadas. |

El monitoreo se probará mediante reproducción histórica, no mediante conexión a una universidad. Se definirán rangos de referencia con entrenamiento y validación, sin atribuir a variaciones de datos una caída de precisión hasta disponer de resultados. Una entrada inválida impedirá emitir una predicción normal; cambios relevantes generarán una señal para revisión, no un reentrenamiento automático.

### **3.5.3. Criterios de aceptación y exclusiones**

El MVP debe reproducir transformaciones e inferencia, validar entradas y cortes, preservar la prueba final y comparar las tres políticas con las mismas poblaciones y presupuestos. Debe reportar incertidumbre, carga y límites. Alcanzar la meta del +10 % es una hipótesis separada del cumplimiento técnico del MVP.

El MVP utiliza exclusivamente OULAD. Quedan fuera tutorías reales, contacto, sanciones, costos monetarios, predicción de deserción institucional, inferencia de intencionalidad, efectos causales e integración D2L/WiFi de la USFQ. Las notas de evaluaciones tampoco forman parte de la comparación principal. Los modelos de secuencias complejos no son requisito.

La extensión institucional posterior requerirá aprobación formal y revisión del responsable o delegado de protección de datos. Los registros WiFi vinculables pueden revelar ubicación; se deberán justificar legitimación, finalidad, minimización, seguridad y evaluación de impacto cuando corresponda conforme a la LOPDP [8]. La autorización académica por sí sola no resuelve esos requisitos y el uso de D2L también requiere revisión del tratamiento de datos personales.

El memo conserva cuatro secciones en cinco páginas, según el límite actualizado por el usuario el 15-nov-2026; el pitch mantiene seis diapositivas. Este documento y su notebook preservan las tres ideas, matriz, selección, metodología y auditoría originales, con la revisión de los tres gaps y el estado real de implementación.

# Revisión metodológica vigente

- **Objetivo de negocio:** cobertura preventiva y semanas de anticipación potencial, con los mismos cupos. TP y cobertura usan matrículas; informar también personas únicas.
- **Caso principal:** cohorte elegible al día 56, K = floor(0.10 × N) por edición para reactiva, estática y longitudinal. Históricos: N = 26.294, Fail = 6.972 y K = 2.619. Recalcular en la prueba reservada.
- **Meta:** +10 % relativo de TP longitudinal frente a estático, igual K; si el baseline es cero informar diferencia absoluta. No es una promesa de reprobaciones evitadas.
- **Tiempo:** anticipación potencial = (duración de la edición - día de primera selección) / 7. Al día 56 hay margen de 25,4-30,4 semanas; el efecto temporal real se medirá en los TP seleccionados.
- **Políticas:** reactiva espera a Fail conocido; estática usa antecedentes iniciales; longitudinal añade actividad hasta el corte. La reactiva tiene cero cobertura preventiva por escenario, no cero cobertura posterior.
- **Cuatro cortes:** 14, 28, 42 y 56. Fijar presupuesto total B común antes de comparar; las repeticiones consumen cupos y las primeras detecciones cuentan una sola vez.
- **Modelos y validez:** regresión logística multinomial y Random Forest, comparación por algoritmo, ediciones posteriores compatibles, etiquetas maduras y estudiantes separados. Transformaciones aprendidas solo en entrenamiento.
- **Información:** registro y retiro ocurrido delimitan elegibilidad; resultados y retiro futuro no son predictores. No notas de evaluaciones; ausencia de registros no acredita ausencia de actividad.
- **MVP previsto:** selector de edición/corte/capacidad, listas, evolución, comparación y modelos versionados. OULAD exclusivamente; D2L/WiFi institucionales quedan para una fase posterior.
- **Límites:** hipótesis de apoyo útil, costos, participación, capacidad real e impacto se validarán en otra fase. PR-AUC respalda la evaluación técnica; el negocio se expresa en casos, cobertura, anticipación y carga.

### Comparador operativo reproducible

Añadir una política simple de seguimiento: ordenar las matrículas elegibles por días desde la última interacción registrada hasta el corte, de mayor a menor, y asignar los mismos K cupos.

Antes de evaluar, fijar: tratamiento de quienes nunca registraron actividad, disponibilidad de actividad previa al inicio, distinción entre inactividad y cobertura desconocida, y desempate estable. Una opción de diseño es contar desde el inicio para quienes carecen de actividad y tienen cobertura comprobada; los estados desconocidos deben señalizarse y tratarse con una regla explícita común. Auditar esta opción antes de adoptarla.

Esta regla ya usa actividad temporal: es una sensibilidad adicional, sin sustituir las tres políticas principales, y no un proceso institucional observado. No afirmar superioridad sobre OU Analyse. Mantener la comparación estática/longitudinal como prueba principal de la hipótesis.

Métricas: TP@K, precisión@K, recobrado@K, casos omitidos, primeras detecciones y anticipación hasta cierre. Para la comparación del día 56, mismo N y K. Para cuatro listas sucesivas se fija un presupuesto total B común; cada repetición consume un cupo y cada matrícula cuenta una sola vez en TP acumulados. Informar también estudiantes únicos.

### Hipótesis de impacto y protocolo opcional para una fase posterior

- **Pregunta:** ¿ofrecer un programa definido de acompañamiento preventivo mejora la aprobación respecto de la atención habitual?
- **Población:** estudiantes elegibles identificados como en riesgo mediante una regla fijada antes de asignar la intervención; fecha de corte y ámbito de validez documentados.
- **Asignación:** aleatoria por estudiante a oferta de acompañamiento proactivo o atención habitual, con estratificación pertinente por módulo/riesgo. Resolver matrículas múltiples asignando a cada persona de manera coherente. Si se requiere aleatorizar por tutor o grupo para evitar contaminación, ajustar diseño, muestra e inferencia por agrupamiento.
- **Intervención:** contacto, evaluación de necesidades, tutoría y seguimiento con frecuencia y contenidos acordados. Conservar el apoyo habitual en ambos grupos.
- **Resultado principal:** proporción que aprueba al cierre (`Pass` + `Distinction`), con diferencia absoluta en puntos porcentuales e intervalo de confianza entre grupos asignados. Informar también Fail y Withdrawn para no confundir una baja de Fail con mayor retiro.
- **Análisis:** intención de tratar; no comparar solo quienes aceptaron tutoría contra quienes no la aceptaron. Registrar oferta, contacto, participación, otras ayudas y seguimiento. La aleatorización aborda confusión en expectativa; documentar contaminación e intervenciones concurrentes.
- **Muestra:** calcularla posteriormente según tasa inicial, efecto mínimo relevante, potencia, agrupamiento si corresponde y pérdidas esperadas. No inventar tamaño ni potencia.
- **Valor y recursos:** participación, tiempo y costo por estudiante y por aprobación adicional cuando los datos lo permitan; posibles efectos adversos o diferencias entre grupos.
- **Alcance de la inferencia:** este ensayo estimaría el efecto de ofrecer ese programa en esa población. No estima efectos individuales ni prueba automáticamente que la selección longitudinal sea mejor que otra política. Esa segunda pregunta requeriría una evaluación de políticas con presupuesto comparable.
- **Estado:** antecedente de diseño opcional, fuera del MVP. La hipótesis de beneficio de tutorías no debe demostrarse para cerrar este PSet. Cualquier piloto exige institución, aprobación formal, capacidad y datos nuevos; no incluye WiFi por defecto.

## Correspondencia de riesgos

Los ocho riesgos ampliados se agrupan sin cambiar sus supuestos: grupo R1 del memo y pitch = ampliados R1 y R4 (mejora y transferencia); grupo R2 = ampliados R2, R3 y R8 (fuga, cobertura y procesamiento); grupo R3 = ampliados R5 y R6 (capacidad e impacto); grupo R4 = ampliado R7 (equidad y confianza). Gravedades de los grupos: alta, crítica, alta y alta.


## Evidencia local y límites de la auditoría

Auditoría local del 12 de noviembre de 2026: 7.052 Fail (21.64 %). 10.156 Withdrawn (31.16 %) y 15.385 aprobaciones (47.20 %). sobre 32.593 matrículas. En la población inicialmente registrada hasta el día 0, 6.980 Fail (21.60 %). 10.068 Withdrawn (31.16 %) y 15.266 aprobaciones (47.24 %). sobre 32.314 matrículas. Son matrículas, no personas únicas ni una tasa institucional actual.

# Auditoría descriptiva de datos

Ejecutada el 12-nov-2026 desde los cinco CSV originales de datasets/. No modifica entradas, no entrena modelos y no ejecuta el pipeline. SHA-256, bytes, fecha local y conteos están en datasets/manifest.json. Fecha de descarga y versión específica del paquete no aportadas; la modificación local no acredita fecha de publicación.

## Poblaciones y denominadores

| Población | N | Fail | Withdrawn | Aprobación | K total | Sin actividad registrada |
|---|---:|---:|---:|---:|---:|---:|
| Original | 32593 | 7052 (21.64 %) | 10156 | 15385 | - | - |
| Registro hasta día 0 | 32314 | 6980 (21.60 %) | 10068 | 15266 | - | - |
| Día 14 | 27881 | 6972 (25.01 %) | 5643 | 15266 | 2779 | 1582 |
| Día 28 | 27307 | 6972 (25.53 %) | 5069 | 15266 | 2719 | 881 |
| Día 42 | 26795 | 6972 (26.02 %) | 4557 | 15266 | 2672 | 684 |
| Día 56 | 26294 | 6972 (26.52 %) | 4056 | 15266 | 2619 | 576 |

28785 personas únicas en la tabla original. Se excluyen de la población inicial 234 registros posteriores al día 0 y 45 fechas de registro ausentes. No se imputaron estas últimas como registro temprano. En cada corte se excluye retiro con fecha <= corte; se mantienen retiros futuros. K total es la suma de floor(0.10 × N) por edición, no floor sobre el agregado.

Los conteos por módulo y edición, para original, inicial y cada corte, se conservan en poblaciones-por-edicion.csv. Numeradores: clases de final_result, agrupando Pass y Distinction; denominadores: filas elegibles según regla. Las matrículas sin eventos <= corte se preservan y no se equiparan automáticamente a inactividad: la cobertura real de registro debe comprobarse. Se incluye actividad de fechas negativas como observada antes del corte.

## Claves, relaciones y calidad

- studentInfo: `{"rows": 32593, "duplicate_keys": 0, "missing_key_values": 0}`.
- studentRegistration: `{"rows": 32593, "duplicate_keys": 0, "missing_key_values": 0}`.
- courses: `{"rows": 22, "duplicate_keys": 0, "missing_key_values": 0}`.
- vle: `{"rows": 6364, "duplicate_keys": 0, "missing_key_values": 0}`.
- info_registration: `{"rows_after": 32593, "unmatched": 0, "registration_without_info": 0}`.
- studentVle: `{"rows": 10655280, "orphan_enrollment_rows": 0, "orphan_resource_rows": 0, "negative_click_rows": 0, "date_min": -25, "date_max": 269, "duplicate_keys_within_chunks": 2195910, "global_daily_duplicate_check": "pendiente: conteo por chunks no demuestra unicidad global"}`.
- courses_relation: `{"info_without_course": 0}`.

## Completitud por columna

- studentInfo: `{"code_module": 0, "code_presentation": 0, "id_student": 0, "gender": 0, "region": 0, "highest_education": 0, "imd_band": 1111, "age_band": 0, "num_of_prev_attempts": 0, "studied_credits": 0, "disability": 0, "final_result": 0}`.
- studentRegistration: `{"code_module": 0, "code_presentation": 0, "id_student": 0, "date_registration": 45, "date_unregistration": 22521}`.
- courses: `{"code_module": 0, "code_presentation": 0, "module_presentation_length": 0}`.
- vle: `{"id_site": 0, "code_module": 0, "code_presentation": 0, "activity_type": 0, "week_from": 5243, "week_to": 5243}`.
- studentVle: `{"code_module": 0, "code_presentation": 0, "id_student": 0, "id_site": 0, "date": 0, "sum_click": 0}`.

## Interpretación y pendientes

La unión studentInfo-studentRegistration conserva una fila por matrícula, con validación one_to_one. Las relaciones de actividad se contrastaron con matrícula y recurso usando sus claves completas. La auditoría de duplicados diarios por chunks no demuestra unicidad global: ese test sigue pendiente y no se aplicó deduplicación. No se alteraron datos.

Fechas negativas pueden representar registro o interacción previa al inicio y no son por sí mismas inválidas. Pendientes: cotejar intervalos por duración de edición y disponibilidad de recursos; validar inconsistencias entre retiro y etiqueta; comprobar calendario real, maduración de etiquetas y pares temporales utilizables; confirmar comparabilidad y completitud de cobertura. Valores válidos no demuestran exactitud externa. No hay métricas predictivas ni evidencia de efecto de tutorías.

## Reproducción

Desde la raíz: `.venv/bin/python pset-01/scripts/auditar_datos.py`. Ruta alternativa: añadir `--data-dir /ruta/autorizada`. La ruta por defecto se deriva del script, no del directorio actual. El script falla ante archivos o claves principales incompatibles. Consultar requirements.txt para versiones usadas.


## Continuidad con PSet 2

El pipeline Fuente, Kestra, Snowflake Raw, dbt Bronze/Silver/Gold y Spark OBT está implementado y verificado. La OBT contiene 108.277 filas y 35 columnas por matrícula-corte; el build aprobó 168 pruebas dbt. La reproducción limpia reutilizó recursos Snowflake y mantuvo cuatro huellas de contenido. Esa evidencia corresponde a preparación reproducible, no a rendimiento predictivo o efecto de tutorías. Consultar ../pset-02/README.md.

La auditoría descriptiva incluida arriba conserva su instantánea del 12-nov-2026. El PSet 2 comprobó globalmente 2.195.960 filas excedentes de clave diaria y las consolidó preservando 39.605.099 clics; no se altera retroactivamente el reporte original por bloques. Persisten límites de cobertura, exactitud externa y disponibilidad histórica de etiquetas y atributos.

## Guía del pitch

Seis diapositivas: problema cuantificado; capacidad y oportunidad temporal; tres políticas; viabilidad técnica y evaluación; MVP y exclusiones; apoyo solicitado, riesgos y criterio de avance. Las cifras auditadas se separan de la meta +10 % y del margen potencial 25,4-30,4 semanas. La solicitud al patrocinador respalda una prueba de concepto y validación del proceso, sin inventar presupuesto monetario, institución comprometida ni rendimiento alcanzado. Texto visible, notas y fuentes están en pset01-presentacion.md.

## Registro de cambios y sincronización

12-nov-2026: reconstrucción de tres ideas, matriz, propuesta y auditoría descriptiva. 13-nov-2026: preparación y pipeline PSet 2 verificados según sus propios informes. 14-nov-2026: primera publicación del paquete en el fork del curso. 15-nov-2026: revisión local de los tres gaps del PSet 1, métricas de cobertura y anticipación, tres políticas con presupuesto común y MVP explícito en propuesta y pitch.

La revisión recupera viabilidad, evaluación y MVP del memo original. Por indicación del usuario del 15-nov-2026, el memo vigente tiene cinco páginas; el límite histórico se conserva en la rúbrica y el prompt. Colab sigue pendiente de acceso y sincronización. Este documento es la fuente del notebook y PDF; los generadores no deben sobrescribirlo.

# Referencias

[1] J. Kuzilek, M. Hlosta y Z. Zdrahal, “Open University learning analytics dataset,” *Scientific Data*, vol. 4, art. núm. 170171, nov. 2017, doi: [10.1038/sdata.2017.171](https://doi.org/10.1038/sdata.2017.171).

[2] The Open University, “Open University Learning Analytics dataset,” *OU Analyse*. [En línea]. Disponible en: https://research.stem.open.ac.uk/ouanalyse/dataset/. [Consultado: 28-oct-2026].

[3] S. Tan et al., “Icentia11k Single Lead Continuous Raw Electrocardiogram Dataset,” versión 1.0, *PhysioNet*, abr. 2022, doi: [10.13026/kk0v-r952](https://doi.org/10.13026/kk0v-r952).

[4] S. Tan et al., “Icentia11K: An Unsupervised Representation Learning Dataset for Arrhythmia Subtype Discovery,” en *Computing in Cardiology (CinC)*, 2021. [En línea]. Disponible en: https://www.cinc.org/2021/Program/accepted/229_Preprint.pdf. [Consultado: 28-oct-2026].


[5] The Open University, “OU Analyse.” [En línea]. Disponible en: https://research.stem.open.ac.uk/ouanalyse/. [Consultado: 11-nov-2026]. Describe el flujo de alertas como antecedente operativo, sin evidencia causal para este proyecto.

[6] E. P. Bettinger y R. B. Baker, “The Effects of Student Coaching in College: An Evaluation of a Randomized Experiment in Student Advising,” *Educational Evaluation and Policy Analysis*, vol. 36, no. 1, pp. 3-19, 2014. Resumen del estudio publicado por AERA: https://www.aera.net/Newsroom/Recent-AERA-Research/The-Effects-of-Student-Coaching. [Consultado: 11-nov-2026]. Acompañamiento individualizado y persistencia; su efecto no es directamente extrapolable a tutoría académica específica ni a OULAD.

[7] J. Klenke et al., “Effects of Early Warning Emails on Student Performance,” arXiv:2102.08803, versión revisada 2023, doi: 10.48550/arXiv.2102.08803. https://arxiv.org/abs/2102.08803. [Consultado: 11-nov-2026]. Los autores describen un efecto positivo estimado con poca precisión; no establece eficacia universal de las alertas.

[8] Superintendencia de Protección de Datos Personales, oficio SPDP-IGRD-2026-514-O. Legitimación, finalidad, minimización, riesgos y evaluación de impacto. https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-igrd-2026-514-o/. Consultado: 15-nov-2026.
