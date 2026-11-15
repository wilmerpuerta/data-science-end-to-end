# Apoyo académico a tiempo

Wilmer Puerta · PSet 1 · Memo breve · 15 de noviembre de 2026

## 1. Problema de negocio y métrica de éxito

Una universidad hipotética con cupos limitados necesita decidir a quién revisar antes del cierre. El proceso de referencia simulado espera a conocer la reprobación; no se atribuye como práctica comprobada a una institución. OULAD registra **7.052 Fail de 32.593 matrículas: 21,64 %**, histórico de 2013-2014, no tasa actual ni evidencia de deserción. La unidad es matrícula estudiante-módulo-edición; se informarán personas únicas [1, E1].

**Objetivo:** cubrir más futuras reprobaciones con los mismos cupos y medir anticipación potencial. Cobertura preventiva (%) = 100 × TP seleccionados antes del cierre / Fail elegibles; TP son seleccionados que finalmente reprueban. Se informan casos por 100 revisiones, omisiones y carga. Registro conocido hasta día 0 y exclusión solo de retiros ya ocurridos definen elegibilidad; retiro futuro no es predictor.

Se estimarán probabilidades de Fail, Withdrawn y aprobación (Pass + Distinction), ordenando por P(Fail) en días 14, 28, 42 y 56. El caso principal fija la cohorte del día 56 y K = floor(0.10 × N) por edición; sensibilidad 5 % y 20 %. Umbral: última puntuación dentro de K, con desempate independiente del resultado. Se priorizan omisiones por oportunidad perdida; las falsas alertas consumen cupos. Capacidad y costos relativos requieren validación.

Meta provisional (hipótesis): **+10 % relativo de TP longitudinal frente a TP estático**, a igual N y K: 100 × (TP longitudinal - TP estático) / TP estático. Con TP estático = 0, informar diferencia absoluta. Anticipación potencial = (duración - día de primera selección) / 7. Al día 56 quedan **25,4-30,4 semanas**: margen disponible, no desempeño obtenido ni fecha observada de tutoría o comunicación de notas. El beneficio esperado es mejor focalización; no reprobaciones evitadas [E2].

## 2. Viabilidad técnica, evaluación y MVP

Cinco CSV locales con acceso confirmado, SHA y auditoría: studentInfo (antecedentes/etiqueta), studentRegistration (registro/retiro), courses (duración), vle (recursos) y studentVle (10.655.280 aportes diarios). Se conserva atribución CC BY 4.0. No hay datos de capacidad real, costos o tutorías. Las notas de evaluaciones se excluyen [1, E1].

Se compararán regresión logística multinomial y Random Forest, estático frente al mismo algoritmo con actividad hasta el corte: clics, días activos, recencia y cambio quincenal. Se preservan matrículas sin registros; recencia desconocida y primer cambio quedan NULL. La prueba usará ediciones posteriores compatibles, etiquetas maduras y estudiantes separados y cortes de matrícula juntos; transformaciones y ajustes solo en entrenamiento/validación. PR-AUC para Fail, calibración e incertidumbre respaldarán las métricas de negocio. Cobertura externa y disponibilidad histórica de atributos siguen pendientes.

**MVP previsto:** selector de edición/corte/capacidad, listas, evolución, modelo y transformaciones versionados, reporte de tres políticas e instrucciones reproducibles. Debe validar entradas, aislar el ajuste de la inferencia y mostrar etiquetas solo al evaluar. Monitoreará versión, faltantes, distribución y carga; cambios generan revisión, no reentrenamiento automático. PSet 2 ya preparó OBT de **108.277 filas y 35 columnas**, con **168 pruebas dbt** aprobadas. Modelos, simulación y demostración predictiva siguen pendientes; completar el MVP no garantiza +10 % [E3].

## 3. Viabilidad de negocio y evaluación de tutorías

La comparación usa la misma cohorte del día 56 y K por edición: **26.294 elegibles, 6.972 Fail y 2.619 cupos** en el histórico. La cota perfecta es 37,6 %, no rendimiento; se recalcularán denominadores en prueba. **Reactiva:** hasta K Fail conocidos tras el cierre, con desempate prefijado; cobertura preventiva cero, posterior informada aparte. **Estática:** top K con antecedentes iniciales. **Longitudinal:** top K con esos antecedentes más actividad al corte. El estático podría operar antes; el corte común aísla el aporte digital.

En cuatro listas, fijar presupuesto total B común: cada revisión repetida consume cupo y cada matrícula cuenta una vez en cobertura acumulada. La reactiva no recibe capacidad ilimitada; los resultados históricos permanecen fijos. El coordinador valida cupos; el tutor revisa contexto y decide apoyo; el sistema solo ordena, sin contacto ni sanciones. Sin institución se validan predicción, cobertura, anticipación y carga simuladas, no adopción, capacidad real, ahorro ni eficacia educativa. Se solicita patrocinio para la prueba de concepto y referentes académicos; se reportarán resultados negativos.

**Protocolo posterior de tutorías, fuera del MVP:** entre elegibles en riesgo bajo una regla previa, asignación aleatoria por estudiante a oferta de acompañamiento (contacto, tutoría y seguimiento definidos) o atención habitual, estratificada por módulo/riesgo y coherente en matrículas múltiples; conservar apoyo habitual en ambos grupos. Comparar aprobación al cierre (Pass + Distinction), diferencia absoluta e intervalo de confianza, por intención de tratar. Registrar Fail/Withdrawn, participación, otras ayudas, contaminación, tiempos y costos; calcular muestra según tasa inicial, efecto mínimo, potencia, pérdidas y agrupamiento cuando corresponda. Evalúa ofrecer ese programa, no efectos individuales ni superioridad causal de la selección longitudinal. Requiere institución, aprobación formal y datos nuevos; su ejecución queda fuera del MVP.

## 4. Riesgos y límites institucionales

**R1, técnico/negocio, alta:** supone aporte longitudinal transferible; contrastar por algoritmo/edición con incertidumbre y conservar baseline si falla. **R2, técnico, crítica:** supone información disponible y cobertura comparable; auditar fechas, particiones y claves, marcar registros ausentes y reconstruir evaluaciones afectadas. **R3, negocio/adopción, alta:** supone capacidad y apoyo útiles; simular cupos/repeticiones, evaluar aceptación e impacto después y ajustar frecuencia, sin ahorro supuesto. **R4, adopción, alta:** supone errores y alertas aceptables; revisar subgrupos y lenguaje, ajustar reglas y preservar juicio humano.

El MVP usa exclusivamente OULAD. D2L y WiFi de USFQ quedan fuera para una fase posterior con aprobación formal y revisión institucional LOPDP. WiFi vinculable puede revelar ubicación. No se infiere intencionalidad, deserción institucional ni impacto causal; tampoco se integran tutorías reales, streaming o modelos complejos de secuencias.

Referencias: [1] Kuzilek, Hlosta y Zdrahal, Scientific Data 4:170171, 2017, doi:10.1038/sdata.2017.171; documentación OULAD: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/. Evidencia: [E1] datasets/manifest.json y pset-01/docs/auditoria-resultados.json; [E2] pset-01/docs/metricas-negocio.json; [E3] pset-02/docs/reproduccion-limpia.json. Protocolo íntegro: proyecto-completo-pset1.md.
