# Plan de trabajo del PSet 04

Estado: API batch y fixtures verificadas, 35 pruebas completas y verificación en Docker. La integración es parcial: dbt/Spark y memos presentes; flujos, Snowflake operativo y simulación pendientes.

## 0. Cerrar el protocolo operativo

Meta principal acordada: al menos +10 % relativo en cobertura de Fail frente al estático a igual cupo. El 30 % es un escenario presupuestario. El prototipo usa matrícula-asignatura y referencia del 10 % por edición; validar su traducción institucional a capacidad, fuente presupuestaria y saldo futuro; evaluar los puntos funcionales de semanas 2 y 4, su reparto y el margen para intervenir. Incorporar la solicitud propuesta del 30 % de cupos reactivos futuros y distinguirla de un porcentaje monetario o de estudiantes. Revisar fechas reales disponibles y qué inferencias temporales solo pueden simularse. Congelar comparadores, métricas, umbrales y escenarios antes de evaluar los lotes finales.

Aceptación: protocolo versionado que distingue acuerdos, supuestos y datos observados; presupuesto contabilizado una vez; reglas de elegibilidad y disponibilidad de etiquetas verificables.

## 1. Consolidar el proyecto final

Construir `proyecto_final/` con ingesta, dbt y Spark del PSet 02; preparación, notebooks y contratos del PSet 03; y los nuevos servicios. Preparar un Compose único y rutas configurables. Registrar observaciones y cambios de decisiones en `docs/cambios.md`. Conservar las entregas previas en el historial.

Aceptación: estructura real y portable, dependencias fijadas, configuración de ejemplo y mapa de trazabilidad. Comprobar respaldos antes de cualquier cambio de volúmenes; no reemplazar los servicios históricos ni sus evidencias durante la preparación.

## 2. Preparar el modelo operativo y las fixtures

Preparar y validar las versiones compatibles con cada corte que produzca asignaciones. Definir cómo se carga y registra la versión adecuada por corte en el servicio. Registrar su relación con el champion anterior y los experimentos tempranos. Exportar con `mlflow.sklearn.save_model` una fixture para CI y guardar una muestra fija que permita una comparación reproducible con una referencia explícita. Si la muestra difiere del conjunto de evaluación original, no afirmar que debe obtener la métrica del conjunto completo.

Aceptación: versión y firma registradas; corte y disponibilidad de features válidos; fixture y muestra con hashes; tolerancia justificada; métricas históricas conservadas. Separar datos de entrenamiento, validación y simulación según su disponibilidad temporal.

## 3. API, política de cupos y CI

Implementar `/salud`, `/modelo` y `/predecir`; esquema Pydantic conforme a firma, rangos y categorías; decisiones por lote completo; identificadores, política versionada e idempotencia. Cargar por alias, registrar latencias y predicciones y preparar respaldo explícito.

Probar entrada válida y 422 por campo faltante, tipo y categoría; reproducción de fixture; al menos dos comportamientos de dominio; capacidad, desempates, ausencia de fuga e idempotencia; fallo de carga y respaldo. No exigir monotonicidad de riesgo al HGB si no fue impuesta ni demostrada: seleccionar invariantes de negocio defendibles.

Aceptación: pytest e imagen en verde sin MLflow ni Snowflake en CI; pruebas de integración locales separadas. Los workflows efectivos estarán en la raíz real del repositorio GitHub. Resolver `main` para CD preservando el historial actual en `master`.

## 4. Producción simulada y etiquetas diferidas

Construir al menos ocho lotes sucesivos y un reloj de simulación. Cada observación conserva su fecha de predicción y de disponibilidad de target. Usar datos posteriores o el test permitido por la rúbrica, informando su exposición previa. Si no hay ocho períodos naturales, documentar el reparto temporal y sus límites; no presentar particiones arbitrarias como semestres independientes.

Implementar `produccion_lotes.yml`, persistir PREDICCIONES y reconciliar versiones y duplicados. Las etiquetas no entran a la predicción y solo se unen al alcanzar su disponibilidad.

Aceptación: ocho lotes reproducibles, historial íntegro de presupuestos y cupos; solo datos temporalmente disponibles en cada tarea.

## 5. Monitoreo, deriva, alertas y tablero

Implementar `monitoreo.yml`, PSI con referencia de entrenamiento y umbrales justificados, KS numérica y chi-cuadrado categórica como respaldo. Monitorear p50/p95, 4xx/5xx, volumen, decisiones, distribución de scores, faltantes, rangos y categorías desconocidas. Evaluar AP y negocio cuando llegue el target, con referencia CV compatible con el corte y la unidad.

Versionar un lote con alteración inducida documentada; mantener originales separados. Distinguir cambios de entradas y caída del desempeño; registrar falsas alarmas si aparecen. El tablero mostrará lotes, etiquetas disponibles, alertas, versiones y reentrenamientos. Las alertas en logs de Kestra son una opción admitida; correo o Slack no son necesarios.

Aceptación: MONITOREO y alertas exportables; detección del lote alterado; resultados de lotes control y limitaciones explicados.

## 6. Reentrenamiento, promoción, rollback y CD

Implementar `reentrenamiento.yml`: disparador por desempeño persistente o calendario, datos ya etiquetados, ventana justificada, misma preparación e hiperparámetros del champion y tag `fase=reentrenamiento`. Reservar el lote etiquetado de comparación fuera del entrenamiento tanto del champion como del challenger.

Aplicar la regla predeclarada de negocio y variación entre folds. La aprobación humana en una tarea en pausa es un requisito de la rúbrica y debe demostrarse, aun cuando los comandos de preparación se ejecuten autónomamente. Registrar aprobación o rechazo; no forzar una mejora ni una promoción. Demostrar rollback y actualización de `/modelo` sin reconstruir la imagen.

Publicar la imagen de código en GHCR por merge a `main`, con tag del commit; configurar Compose para consumirla. Distinguir publicación de código y cambio de alias de modelo.

Aceptación: alerta, reentrenamiento, challenger, evaluación y decisión trazables; pausa humana real; rechazo documentado cuando corresponda; demostración controlada de cambio y rollback.

## 7. Ética, respaldo y resultado de negocio

Evaluar al menos un subgrupo, explicar quién asume FP/FN, definir tres condiciones observables de ajuste o retirada e implementar y demostrar el interruptor de respaldo. Revisar la supervisión humana.

Comparar la focalización con igual capacidad, medir FP y precisión al cupo efectivo y construir escenarios presupuestarios entre períodos, incluyendo efectividad cero y el saldo futuro tras el adelanto propuesto del 30 %. No extrapolar FP de forma lineal ni tratar el 30 % como garantía de bajo error. Informar presupuestos, atenciones, personas únicas y capacidad remanente por separado. No convertir Fail detectados en Fail evitados, ahorro observado o tutorías realizadas sin evidencia.

Aceptación: evidencia de subgrupos, retirada y respaldo; tablas y gráficos por lote frente a comparadores válidos, con reentrenamientos marcados y supuestos económicos explícitos.

## 8. Entrega y demostración

Ejecutar Restart/Run All de los notebooks finales. Exportar los cinco CSV de evidencia y la trazabilidad hasta Gold, snapshot, run y versión. Preparar documento técnico de hasta 12 páginas más anexos, presentación ejecutiva de 10-12 diapositivas y demo de hasta siete minutos con enlace accesible desde el memo.

Aceptación: reproducción desde fuente hasta reentrenamiento; CI/CD e imagen publicados; video con ingesta, API válida/422, rollback, deriva, pausa humana e interruptor; auditoría literal de la rúbrica antes del cierre.
