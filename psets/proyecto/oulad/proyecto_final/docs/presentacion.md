# Presentación ejecutiva - PSet 04

## 1. Apoyo académico preventivo

Priorizar tutorías durante el período, con los mismos cupos

detecciones netas adicionales de Fail<br/>con 920 propuestas de tutoría

Proyecto final de Ciencia de Datos | Wilmer Puerta

Resultado histórico: 420 frente a 314 matrículas. No representa reprobaciones evitadas ni un piloto institucional.

## 2. Problema y decisión actual

Los cupos limitados obligan a decidir **a quién contactar primero**.

La respuesta reactiva conoce el resultado al cierre.<br/>La propuesta preventiva revisa el riesgo en semanas 2 y 4.

La unidad es la matrícula-asignatura. El tutor confirma la necesidad y la atención; la predicción solo propone.

Caso universitario de decisión con datos OULAD. La capacidad y el calendario reales todavía requieren acuerdo institucional.

## 3. Detección y tutorías tempranas

920 cupos compartidos entre ambas rondas.<br/>Una propuesta anterior conserva su reserva.

Reparto experimental 25/75; no se ha seleccionado como política institucional. No contar dos veces una propuesta acumulada.

Tabla: [["Momento", "Propuestas nuevas", "Decisión sugerida"], ["Semana 2", "226", "Revisar y contactar con mayor anticipación"], ["Semana 4", "694", "Actualizar prioridades y usar el saldo"]]

## 4. Operación del servicio

Un servicio reúne los registros, propone prioridades y conserva la decisión para su revisión.

El seguimiento puede proponer revisar el modelo. Su reemplazo y la asignación final requieren responsables humanos.

## 5. Valor con los mismos cupos

**+33,76 %** de cobertura relativa de Fail: se supera la meta del 10 % en el benchmark.

Los casos no-Fail propuestos bajan de 606 a 500.

Misma base de 1.947 Fail, mismos 920 cupos. Los 106 casos son matrículas; no necesariamente personas distintas ni ahorro.

Gráfico: {"categorias": ["Variables estáticas", "Estáticas + actividad"], "valores": [314, 420]}

## 6. Desempeño por lote

La mejora global no garantiza mejorar en todos los lotes.<br/>L03 empata; las propuestas requieren revisión por lote.

Cada punto muestra cupos acumulados de su onda/corte. No sumar semanas 2 y 4. Se preservó el modelo vigente en todos los lotes.

## 7. Oportunidad de intervención

Propuesta de piloto: contrastar oportunidad, aceptación y error con cohortes nuevas.

Alternativas retrospectivas a 920 cupos. La comparación no demuestra una política óptima ni el efecto causal de la tutoría.

Tabla: [["Calendario", "Fail detectados", "Lectura de oportunidad"], ["Solo semana 2", "415", "Mayor anticipación"], ["Dos rondas", "420", "226 propuestas se adelantan 14 días"], ["Solo semana 4", "426", "Más observación; todas las propuestas esperan"]]

## 8. Escenario presupuestario

cupos que podrían adelantarse

cupos reactivos futuros que quedarían

Supuesto: adelantar 30 % de una bolsa futura de 920, con redondeo por edición. La bolsa reactiva vigente se protege.

Es un escenario de cupos, no dinero aprobado. No hay evidencia de ahorro; medir costos y efecto antes de proponer una transferencia.

## 9. Riesgos de acceso

En L06, la cobertura de quienes declaran discapacidad es **8,20 puntos menor**.

Revisar accesibilidad, necesidades y composición de módulos antes de usar esa priorización automáticamente.

Control original. Asociación descriptiva; no prueba causalidad. No declarar discapacidad tampoco significa ausencia de necesidades.

Tabla: [["Grupo en L06", "Fail priorizados / Fail observados", "Cobertura"], ["Sin declaración", "159 / 687", "23,14 %"], ["Con declaración", "13 / 87", "14,94 %"]]

## 10. Revisión del reemplazo

Se obtuvieron **4** detecciones adicionales; la regla exigía al menos **7**, con los mismos 147 cupos.

Decisión humana: rechazar el reemplazo y conservar el modelo vigente.

Evaluación reservada L08 después de etiquetas maduras. Se probó recarga/rollback técnico aislado; no se atribuye mejora a ese ejercicio.

Gráfico: {"categorias": ["Modelo vigente", "Candidato nuevo"], "valores": [77, 81]}

## 11. Supervisión y continuidad

La cola administrativa mantiene la revisión y los cupos; no estima un riesgo individual.

Los límites son experimentales y requieren acuerdo. Quienes no reciben propuesta conservan vías habituales de apoyo y revisión.

Tabla: [["Señal que vigilar", "Respuesta", "Responsable"], ["Menor detección con igual capacidad", "Revisar y evaluar ajuste o retirada", "Modelo + coordinación"], ["Brecha persistente de acceso", "Revisar necesidades y suspender ranking si corresponde", "Coordinación académica"], ["Datos o modelo no disponibles", "Bloquear entradas inválidas o usar cola administrativa", "Datos + operación"]]

## 12. Recomendación y siguiente decisión

**Ajustar y validar con un piloto supervisado**

Mantener el modelo vigente y revisar el acceso de L06.<br/>Acordar capacidad, calendario y responsables con la Universidad.

Medir contacto, aceptación, costos y resultados con nuevas cohortes antes de escalar o trasladar presupuesto.

La mejora predictiva a igual cupo está observada. El impacto de las tutorías sigue por demostrar.

Prompting fue factible; una alternativa con LLM externo requiere una evaluación institucional posterior de costo-beneficio y privacidad.
