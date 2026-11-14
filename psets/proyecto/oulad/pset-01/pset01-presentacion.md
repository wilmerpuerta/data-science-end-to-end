# Pitch revisado: seis diapositivas

Wilmer Puerta · 12-nov-2026. Fuente visible exacta del PPTX. Los bloques de notas y fuentes no son texto visible. Paleta: negro/rojo, azul cielo y blanco.

## Diapositiva 1

### Contenido visible exacto

Apoyo académico a tiempo

Identificar mejor a quién apoyar, con la misma capacidad preventiva.

Wilmer Puerta

Señales  →  Prioridad  →  Revisión del tutor

Prueba de concepto con OULAD · Universidad hipotética

### Visual propuesto

Flujo horizontal editable de señales a revisión del tutor.

### Notas del presentador

No existe socio institucional comprometido. El sistema propone una prioridad y el tutor siempre revisa contexto y decide. No hay contactos reales ni sanciones automáticas.

### Fuentes

Propuesta del proyecto y documentación oficial de OULAD, doi:10.1038/sdata.2017.171.

## Diapositiva 2

### Contenido visible exacto

El riesgo cambia durante el módulo

Una lista fija puede omitir trayectorias que empeoran.

21,64 %

7.052 Fail de 32.593 matrículas originales

Retiros: 10.156 (31,16 %) · Aprobación: 15.385 (47,20 %)

Revisión temprana: día 14  →  28  →  42  →  56

Fuente: auditoría local OULAD, 12-nov-2026. No es una tasa institucional actual.

### Visual propuesto

Cifra central y línea de cuatro cortes, todo editable.

### Notas del presentador

Denominador original: 32.593 matrículas, 28.785 personas únicas. Población inicialmente registrada hasta día 0: 32.314. Al día 56: 26.294 elegibles, 6.972 Fail y 4.056 Withdrawn; se excluyen retiros ya ocurridos y registros tardíos o sin fecha. La cifra central cuantifica el histórico completo, no una universidad actual. La trayectoria de riesgo es una hipótesis a evaluar, no una curva ya estimada.

### Fuentes

datasets/manifest.json; docs/auditoria-datos.md; docs/poblaciones-por-edicion.csv.

## Diapositiva 3

### Contenido visible exacto

Una prioridad de revisión que se actualiza

El tutor decide el apoyo a partir de una lista quincenal.

Observar actividad  →  Estimar P(Fail)

Ordenar K cupos  →  Tutor revisa y decide

Presupuesto preventivo simulado: 10 % por edición y corte

K = floor(0.10 × N) · Sensibilidad: 5 % y 20 %

Comparador operativo: recencia frente a priorización con modelos

### Visual propuesto

Dos pasos de flujo con textos nativos editables.

### Notas del presentador

Cortes 14, 28, 42 y 56. Ordenar por P(Fail), umbral último caso admitido, desempate estable por clave sin etiqueta. Recencia descendente desde última interacción <= corte. Nunca activos con cobertura comprobada: contar desde inicio; desconocidos: marcar insuficiencia y fijar política común antes de evaluar. La regla usa tiempo y es adicional. Comparación principal: estático/longitudinal, mismo algoritmo, N y K. Los clics no demuestran intención. Repeticiones consumen cupos y TP acumulados cuentan una vez por matrícula.

### Fuentes

Decisiones metodológicas del proyecto; auditoría local de elegibilidad.

## Diapositiva 4

### Contenido visible exacto

Viabilidad, evaluación y producto concreto

Datos disponibles y una comparación retrospectiva delimitada.

OULAD auditado: 5 archivos · 10.655.280 registros de actividad

Regresión logística multinomial y Random Forest

Estático frente a longitudinal · Ediciones posteriores compatibles

Estudiantes separados · Igual capacidad · PR-AUC y TP@K

MVP previsto: preparación, puntuaciones por corte, listas, evolución y reporte

### Visual propuesto

Secuencia de datos, validación y producto descrita con objetos editables.

### Notas del presentador

El target distingue Fail, Withdrawn y Pass/Distinction. Etiquetas maduras antes de predicción simulada; transformaciones aprendidas solo con entrenamiento. Familias estática/longitudinal comparadas por algoritmo; sin notas de evaluaciones. PR-AUC para Fail, calibración e incertidumbre. La auditoría no demuestra todavía viabilidad de particiones temporales. No se entrenaron modelos ni se construyó el MVP. PSet 2 preparará Kestra, dbt, Spark y Snowflake.

### Fuentes

Kuzilek et al., 2017, doi:10.1038/sdata.2017.171; auditoría local y contrato preliminar de datos.

## Diapositiva 5

### Contenido visible exacto

Beneficio medible y condiciones de éxito

Meta provisional: +10 % relativo de detecciones al día 56, a igual K.

40  →  44

Futuras reprobaciones identificadas con 100 revisiones

Ejemplo ilustrativo, no resultado obtenido ni reprobaciones evitadas

R1 Mejora incierta: comparar con incertidumbre
R2 Calidad y fuga: auditar fechas y cobertura
R3 Capacidad y efecto: simular carga y evaluar piloto
R4 Equidad y confianza: revisar errores y mantener juicio humano

Piloto posterior: aprobación entre grupos asignados a oferta de apoyo o atención habitual

### Visual propuesto

Ejemplo numérico y cuatro riesgos compactos, editables.

### Notas del presentador

Gravedades R1 alta, R2 crítica, R3 alta, R4 alta. R1 supone aporte transferible; R2 información disponible y comparable; R3 capacidad viable y apoyo útil; R4 errores aceptables entre grupos. El ejemplo equivale a +4 puntos de precisión (40 % a 44 %) y +10 % relativo en TP. No es rendimiento medido de recencia. Si TP estático=0 informar diferencia absoluta. Los ocho riesgos ampliados se agrupan R1={1,4}, R2={2,3,8}, R3={5,6}, R4={7}. El piloto estimaría oferta de un programa, no efectos individuales ni superioridad causal de selección longitudinal.

### Fuentes

Meta y ejemplo hipotéticos del proyecto; protocolo de impacto posterior. No hay retorno financiero estimado.

## Diapositiva 6

### Contenido visible exacto

Respaldar una prueba de concepto y una decisión informada

Avanzar al piloto solo con evidencia favorable y condiciones acordadas.

Se necesita un responsable académico y un referente de tutorías

Validar el presupuesto preventivo y la capacidad de revisión

Auditar y cuantificar  →  Comparar y demostrar  →  Decidir sobre piloto

Criterios: mejora e incertidumbre, calidad, carga y equidad

Piloto posterior: oferta aleatoria de apoyo vs atención habitual
Medir aprobación, retiro, participación y costos

### Visual propuesto

Hitos y criterio de avance en una composición editorial editable.

### Notas del presentador

La auditoría descriptiva ya está realizada, con cobertura y temporalidad aún por validar. No hay plazo inventado ni compromiso de reducción de Fail. Piloto: aleatorización por persona con estratificación pertinente, asignación coherente de múltiples matrículas; controlar contaminación o ajustar por agrupamiento. Intención de tratar, diferencia absoluta de aprobación e intervalo de confianza. Informar también Fail, Withdrawn, oferta, contacto, participación, otras ayudas, tiempos y costos. Calcular muestra según tasa inicial, efecto mínimo, potencia y pérdidas. Aprobación = Pass + Distinction. Mantener apoyo habitual. El piloto requiere institución y autorizaciones futuras.

### Fuentes

Diseño del proyecto. OU Analyse: https://research.stem.open.ac.uk/ouanalyse/ respalda plausibilidad operativa, no causalidad. Klenke et al., arXiv:2102.08803, efecto positivo impreciso en otro contexto.
