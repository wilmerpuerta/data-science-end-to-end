# Pitch revisado: seis diapositivas

Wilmer Puerta · Revisión del 15-nov-2026. Fuente visible exacta del PPTX. Notas y fuentes se conservan aparte. Se mantiene el diseño editorial y los objetos nativos editables.

## Diapositiva 1

### Contenido visible exacto

Apoyo académico antes del cierre

La decisión de negocio es a quién revisar con los mismos cupos.

21,64 %

7.052 Fail de 32.593 matrículas OULAD

Reprobación histórica de un módulo

Wilmer Puerta
Universidad hipotética, sin institución participante

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

Cifra auditada, no una tasa actual de la USFQ. Hay 28.785 personas únicas: matrícula y persona no son intercambiables. Fail no prueba deserción institucional. Escenario de negocio: revisión posterior a conocer una reprobación. El beneficio de tutorías sigue siendo hipótesis. Revisión de los tres gaps del PSet 1: 15-nov-2026.

### Fuentes

datasets/manifest.json; pset-01/docs/auditoria-resultados.json; OULAD, doi:10.1038/sdata.2017.171.

## Diapositiva 2

### Contenido visible exacto

Cobertura y anticipación con capacidad limitada

Meta por validar: +10 % relativo de casos cubiertos frente al estático.

Día 56: 26.294 elegibles y 6.972 futuros Fail

2.619 cupos de revisión

Cobertura: Fail incluidos antes del cierre / Fail elegibles

25,4-30,4 semanas disponibles hasta el cierre

Margen potencial de la copia histórica. Rendimiento aún por evaluar.

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

K = floor(0.10 × N) por edición desde la cohorte elegible al día 56; suma 2.619, no floor del agregado. Misma población y K entre modelos. Cobertura preventiva (%) = 100 × TP antes del cierre / Fail elegibles. La meta +10 % relativa equivale a 100 × (TP longitudinal - TP estático) / TP estático; con baseline cero informar diferencia absoluta. Anticipación potencial = (duración de la edición - día de primera selección) / 7. Duraciones de 234-269 días, sin fecha de tutoría o de comunicación de notas. No son casos detectados todavía ni reprobaciones evitadas. La cota ideal con estos cupos es 37,6 %. Recalcular cifras en la prueba reservada.

### Fuentes

pset-01/docs/metricas-negocio.json; pset-01/docs/poblaciones-por-edicion.csv; datasets/courses.csv.

## Diapositiva 3

### Contenido visible exacto

Tres políticas de seguimiento académico

Misma cohorte y mismo K por edición en la comparación principal.

Reactiva

Espera a Fail conocido y revisa después del cierre

Estática

Usa antecedentes iniciales y selecciona K al día 56

Longitudinal

Añade actividad hasta el mismo corte y selecciona K

Se comparan casos cubiertos, anticipación y carga de revisión

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

La reactiva usa el resultado solo cuando ya se conoce, selecciona hasta K Fail con desempate prefijado y tiene anticipación preventiva cero por definición del escenario. Puede cubrir reprobaciones después: no atribuirle cobertura total nula. Estático y longitudinal se evalúan al mismo día 56 para aislar el aporte digital; un score estático podría utilizarse antes en otra comparación. No se modifica el resultado histórico ni se simula una tutoría eficaz. Sensibilidades 5 % y 20 %. Para cuatro cortes, presupuesto total B igual, cada repetición consume cupos y cada matrícula cuenta una vez en cobertura acumulada; informar personas únicas. Recencia queda como sensibilidad adicional.

### Fuentes

Protocolo de tres políticas en propuesta-pset1.md y proyecto-completo-pset1.md, revisión del 15-nov-2026.

## Diapositiva 4

### Contenido visible exacto

Viabilidad técnica y evaluación

La preparación de datos funciona. La mejora predictiva sigue por comprobar.

5 CSV auditados y 10.655.280 aportes de actividad

Pipeline disponible: OBT de 108.277 filas y 35 columnas

Regresión logística multinomial y Random Forest

Prueba temporal con ediciones compatibles y estudiantes separados

Evaluación: cobertura y semanas, PR-AUC y calibración

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

Kestra, Snowflake, dbt y Spark ya prepararon la OBT; 168 pruebas dbt aprobaron y la reproducción limpia mantuvo cuatro huellas. Esa evidencia no mide calidad predictiva. Se comparará cada algoritmo con antecedentes estáticos y con actividad longitudinal: clics, días activos, recencia y cambio quincenal. Predictores solo hasta días 14, 28, 42 y 56. Etiquetas maduras antes del corte simulado; parámetros y transformaciones solo en entrenamiento/validación. Reservar estudiantes y ediciones posteriores compatibles; verificar disponibilidad histórica de atributos y fechas antes de entrenar. No notas de evaluaciones. Métricas por edición con incertidumbre agrupada por estudiante cuando sea viable. Ningún modelo entrenado todavía.

### Fuentes

pset-02/docs/reproduccion-limpia.json; pset-02/docs/obt-verificacion.json; pset-01/docs/auditoria-resultados.json.

## Diapositiva 5

### Contenido visible exacto

Alcance del MVP académico

Una demostración reproducible para decidir si conviene un piloto institucional.

Selector de edición, corte y capacidad

Listas priorizadas y evolución del riesgo

Reporte de las tres políticas, cobertura, anticipación y carga

Modelo y transformaciones versionados, con instrucciones de ejecución

OULAD exclusivamente. D2L y WiFi institucionales quedan fuera.

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

Estado: preparación y controles de datos implementados; entrenamiento, evaluación y simulación pendientes. El MVP debe reproducir inferencia, validar entradas, respetar cortes, separar la prueba final y comparar con igual presupuesto. Se mantienen fijos los resultados académicos observados. Hipótesis posterior: ofrecer tutorías puede mejorar aprobación; no se requiere demostrarla para cerrar el MVP. Participación, costos, capacidad real, tutorías, sanciones, deserción, intencionalidad y transferencia institucional quedan fuera. D2L/WiFi en una fase posterior con aprobación formal y revisión LOPDP: legitimación, finalidad, minimización y evaluación de impacto cuando corresponda; WiFi vinculable puede revelar ubicación.

### Fuentes

Memo original de cinco páginas, secciones de viabilidad y MVP; propuesta revisada; SPDP, oficio SPDP-IGRD-2026-514-O: https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-igrd-2026-514-o/.

## Diapositiva 6

### Contenido visible exacto

Apoyo solicitado y criterio de avance

Respaldar la prueba de concepto y validar la utilidad del proceso con referentes académicos.

Validar los cupos y la utilidad de las listas

Entregable: comparación reproducible con incertidumbre

R1 Aporte incierto: comparar y admitir resultados negativos
R2 Calidad y fuga: verificar fechas y cobertura
R3 Capacidad y adopción: simular carga y validar utilidad
R4 Equidad y confianza: revisar errores y preservar juicio humano

El patrocinio apoya la evaluación. El beneficio educativo es una hipótesis posterior.

### Visual propuesto

Composición editorial con textos y cifras nativos editables; fondo, tipografía y paleta del pitch previo.

### Notas del presentador

El apoyo solicitado es una prueba de concepto y referentes para validar el proceso y capacidad hipotéticos, no presupuesto monetario inventado ni compromiso institucional. Gravedad: R1 alta, R2 crítica, R3 alta, R4 alta. Meta provisional +10 % relativo al día 56 a igual K; avanzar según resultados e incertidumbre, calidad, carga y equidad. Si el longitudinal no mejora, reportarlo y conservar baseline o acotar alcance. Efecto académico de tutorías y retorno financiero no demostrados. El protocolo causal detallado es un antecedente opcional para una fase posterior, fuera del MVP.

### Fuentes

Decisiones del proyecto, revisión del 15-nov-2026. Riesgos y límites en Canvas y propuesta.
