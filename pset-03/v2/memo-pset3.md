# Anticipar apoyo académico

Experimentación, selección y evidencia para priorizar tutorías. **El criterio del negocio:** maximizar la cobertura de matrículas con Fail, con el mismo cupo del 10 % por edición. Detectar riesgo no demuestra que una tutoría evite el resultado.

## 1. EDA: hallazgos que cambian el experimento

Desarrollo al día 56: **16,331 matrículas / 15,482 estudiantes**; OBT original: 35 columnas. Fail: 30.11 %. El EDA usa desarrollo y conserva las filas atípicas. Spearman se justifica por colas largas y relaciones monotónicas; categorías nominales no se ordenan artificialmente.

| Hallazgo | Evidencia | Consecuencia |

| Desbalance y objetivo | Approved 9.219; Fail 4.918; Withdrawn 2.194. Razón mayor/menor 4,20. | AP de Fail y cobertura a cupo fijo; accuracy no decide. |

| Clics con cola larga | Mediana 53; p99 686,1; máximo 7.028. IQR: 1.158; |Z| >= 3: 264. | Conservar extremos y ensayar log1p dentro de la ablación. |

| Ausencia y NULL estructural | 432 sin registros al corte: 75,69 % Fail vs 28,88 % con registros. Razón quincenal indefinida: 2.516. | Separar ausencia de cero; imputación e indicadores en cada train-fold. No inferir causalidad. |

Fuentes: docs/eda/*.csv y 01_eda.ipynb. IQR y Z-score son diagnósticos, no reglas de eliminación.


<!-- PAGE -->


# Features y validación

## 2. Dos derivadas disponibles al corte

| Feature | Motivo y disponibilidad | Tratamiento |

| log1p_clicks_current_14d | Cola larga observada; solo clics de los últimos 14 días hasta el corte. | log1p determinista, sin aprender del futuro. |

| clicks_per_active_day_14d | Intensidad entre quienes tienen días activos en la ventana actual. | Clics / días si días > 0; NULL si no. Imputación e indicador aprendidos en train-fold. |

Ambas viven en **src/pipeline.py**. La allowlist descarta IDs, target, folds y campos futuros. Medianas, escalado y one-hot se ajustan solo con entrenamiento; las categorías nuevas se ignoran de forma controlada. Se verifican ventanas y actividad posterior al corte.

| Ablación lineal fija | AP CV | Cobertura CV | Delta cobertura |

| Estáticas | 0.4232 | 16.05 % | -6.774 pp |

| Longitudinal original | 0.5690 | 22.82 % | +0.000 pp |

| Solo log1p | 0.5690 | 22.92 % | +0.103 pp |

| Solo intensidad | 0.5688 | 22.94 % | +0.124 pp |

| Ambas derivadas | 0.5687 | 22.92 % | +0.104 pp |

La ganancia de ambas es solo +0,104 puntos porcentuales de cobertura y no supera la dispersión entre folds: **no se demuestra mejora estable de las derivadas**. Se informa el resultado negativo; el ensayo principal conserva la representación predeclarada, sin escoger features usando prueba.

## 3. Preparación, partición y métricas

| Partición al día 56 | Matrículas | Estudiantes |

| Entrenamiento / CV | 16.331 | 15.482 |

| Prueba 2014J | 8.758 | 8.442 |

| Purgadas por estudiante compartido | 1.205 | 1.145 |

**Cinco folds persistidos por estudiante**, estratificados y con semilla 42: no comparten alumnos. Todos los candidatos usan el mismo snapshot, preparación, validación completa y métricas. El diagnóstico de train usa las mismas 1.000 filas estratificadas por fold para todos; no se presenta como train completo.

**Técnica:** AP de Fail; Brier y log-loss complementan calibración. **Negocio:** media CV de TP / Fail con K=floor(0,10 N) por edición y fold. Se desempata por dispersión, AP, Brier, costo y run_id según protocolo; no por resultados de prueba.

**2014J ya fue observado en v1.** La reconstrucción es un benchmark retrospectivo reutilizado. Se congela la decisión antes de una única evaluación final conjunta de esta versión; no se afirma una prueba inédita ni se ajusta con su resultado.

Snapshot: 0a75615bd8ff... | split: 231cd638f375... | protocolo predictivo: 07111fdf724a...<br/>Hashes completos, enmiendas operativas y archivos: docs/protocolo-congelado.json y docs/enmienda-*.json.


<!-- PAGE -->


# Diseño y comparación de candidatos

## 4. Experimento y 5. resultados por defecto

Dos baselines preceden a seis familias: Dummy más frecuente y proceso reactivo al cierre. El control estático es una comparación separada. Presupuesto principal: **2 + 6 + 90 + 1 = 99 ejecuciones**; con folds y análisis auxiliares, el experimento registra 382 runs (379 FINISHED y 3 FAILED, conservados para auditoría).

| Familia | AP train* | AP CV ± DE | Brecha | Cobertura CV ± DE | Fit CV s | LR |

| Dummy | 0.301 | 0.301 ± 0.012 | 0.000 | 9.15 ± 1.50 % | 1.31 | N/A |

| Logística | 0.584 | 0.569 ± 0.024 | 0.015 | 22.92 ± 0.80 % | 2.76 | N/A |

| RandomForest | 1.000 | 0.561 ± 0.030 | 0.439 | 22.57 ± 1.12 % | 15.63 | N/A |

| HGB | 0.727 | 0.578 ± 0.027 | 0.149 | 22.81 ± 0.82 % | 5.16 | 0,1 |

| MLP | 0.777 | 0.504 ± 0.028 | 0.273 | 20.09 ± 1.27 % | 328.08 | 0,001 |

| GaussianNB | 0.543 | 0.538 ± 0.027 | 0.006 | 22.78 ± 1.07 % | 0.88 | N/A |

| GPT prompting | 0.393 | 0.382 ± 0.039 | 0.010 | 14.87 ± 1.88 % | 1.16 | N/A |

* Train: muestra fija de hasta 1.000 filas por train-fold. CV: todos los casos, media ± DE (no IC). Defaults de scikit-learn salvo semilla; GPT usa prompting predeclarado. LR = tasa de aprendizaje cuando aplica.

RandomForest y MLP muestran brechas AP grandes (0,439 y 0,273); MLP agotó 200 iteraciones. GaussianNB tiene brecha pequeña, pero log-loss CV 2,741: una brecha reducida no garantiza buenas probabilidades.

Cobertura de Fail al mismo cupo. La política reactiva tiene cobertura preventiva cero; su atención posterior no equivale a anticipación.

## LLM fundacional generativo mediante prompting

GPT-6 Luna se probó con **18 ejemplos (6 por clase) y proporciones del train-fold**, sin etiquetas de las consultas. Recibe la misma matriz preparada, con nombres y valores dispersos a seis cifras significativas; devuelve probabilidades verificadas por consulta. No entrena sus pesos con todas las filas. Su contexto limitado y probabilidades autodeclaradas son parte del ensayo, no una garantía de calibración.

AP CV 0,382 y cobertura 14,87 %: supera Dummy, pero no está entre los tres primeros por negocio y no pasa al tuning. Inferencia CV registrada: 349,8 s, frente a 0,18-0,53 s en las familias tabulares; fit del GPT construye contexto y no refleja ese costo. Hubo recuperación de caché y ocho peticiones concurrentes: estos tiempos no equivalen a un servicio productivo en frío.

Consumo global conservador: **USD 1.1168** / USD 10, incluidos pilotos e intentos fallidos; 720 llamadas con uso registrado. El gasto de esta muestra no estima el costo anual de la Universidad.


<!-- PAGE -->


# Tuning y trazabilidad

## 6. Tres familias x treinta configuraciones

Las tres primeras por cobertura CV default fueron logística, HGB y GaussianNB. RandomizedSearchCV usa los mismos cinco folds, 30 configuraciones únicas preextraídas por familia y refit. Cada configuración se registra como hija de una corrida padre. Se conservan defaults como elegibles.

| Familia | Espacio predeclarado | Escala |

| Logística | C 0,001-100; pesos None/balanced; iteraciones 300/600/1.000; tol 1e-5-1e-3. | C y tol log. |

| HGB | LR 0,02-0,2; 60/100/160 iteraciones; hojas 7/15/31/63; profundidad None/3/5/8; min hoja 10-80; L2 1e-4-10; early stopping booleano. | LR y L2 log. |

| GaussianNB | var_smoothing 1e-12-1e-3. | Logarítmica. |

| Familia | Default | Ajustado | Delta pp | DE ref. pp | Mejora estable |

| Logística | 22.92 % | 23.24 % | +0.313 | 0.801 | No |

| HGB | 22.81 % | 23.40 % | +0.591 | 0.934 | No |

| GaussianNB | 22.78 % | 22.82 % | +0.042 | 1.068 | No |

Ningún delta supera la mayor DE entre default y ajustado: **no se declara mejora demostrada**. Se usa la mayor media como elección operativa provisional, manteniendo visible la incertidumbre. Los controles estáticos de las dos familias finalistas tienen 31 configuraciones cada uno (30 sorteos iguales + default), ajustadas independientemente en CV.

## Tracking: evidencia exportada y captura real

Servidor Docker con backend SQLite y artefactos persistentes; experimento oulad-apoyo-academico-v2. Los runs finalizados con estimador guardan parámetros/semilla, origen/fecha/hash, métricas train/CV/DE/tiempos, fase/familia/commit real, Pipeline, firma y ejemplo. Los padres lógicos y fallos se distinguen de configuraciones válidas.

Captura nativa de la interfaz local, sin edición: izquierda HGB dc2fa9bb8bee...; derecha logística bb2b40097599.... Las filas muestran AP y cobertura CV, con su desviación.

Código versionado antes de los ajustes. Se conservan dos intentos técnicos incompletos separados; las enmiendas registran tarifas de caché, salida por claves, lectura de final_answer y recuperación acotada de rechazos sin cobro. No se reescriben los commits históricos ni las probabilidades.


<!-- PAGE -->


# Decisión y evaluación final

## 7. Champion por valor esperado en CV

**HGB: 23.40 % ± 0.93 pp**; logística: 23.24 % ± 0.56 pp. La diferencia de 0.162 pp es menor que la dispersión de referencia (0.934 pp). HGB maximiza la media predeclarada; **no hay superioridad estable ni económica demostrada**.

| Modelo / política | TP | FP | FN | Cobertura | AP |

| Dummy | 174 | 698 | 1773 | 8.94 % | 0.2223 |

| HGB estático | 309 | 563 | 1638 | 15.87 % | 0.3105 |

| HGB longitudinal | 465 | 407 | 1482 | 23.88 % | 0.4265 |

| Logística longitudinal | 477 | 395 | 1470 | 24.50 % | 0.4388 |

| Reactiva preventiva | 0 | N/A | N/A | 0,00 % | N/A |

**Prueba:** 8.758 matrículas, 8.442 estudiantes, 1.947 Fail y K=872. HGB captura 465 Fail frente a 309 de su control estático: **+156 / +50,49 %**, sin atribuir efecto causal a tutorías. La reactiva puede atender 872 Fail conocidos después del cierre, con cupo acotado, y cero cobertura preventiva.

Logística obtiene 477 TP y AP 0,4388 en prueba, frente a 465 TP y AP 0,4265 de HGB. **No se reelige con prueba**: queda como challenger competitivo. La decisión se fijó por CV y su escasa separación exige una validación prospectiva antes de prometer ventaja.

Fail captados con el mismo K=872; el resultado observado en prueba no sustituye el criterio de selección.

## Costo, explicación y registro reproducible

Refit: HGB 1,80 s vs logística 0,32 s. Primer pase de 1.000 filas: 0,244 s vs 0,042 s; medianas de cinco repeticiones: 0,046 s vs 0,019 s (dos hilos). Los escenarios de costo FN/FP = 1, 2, 5 y 10 son relativos: no se inventa una tarifa institucional. El umbral es el score del último cupo por edición, con desempate por clave, no 0,5 universal.

Explicación: permutación en 200 casos de desarrollo (2 repeticiones) destaca clics recientes/acumulados y carga académica. En un caso de alto riesgo de desarrollo, sustituir el grupo de actividad por un perfil observado central cambia P(Fail) de 0.854 a 0.369. Es contraste descriptivo local, no SHAP aditivo ni intervención causal.

**Registry:** oulad-apoyo-academico-v2-modelo, champion v1 / challenger v2.<br/>Fuente champion: dc2fa9bb8bee4944bd00611a6ac5c34f.<br/>Evaluación final: fcd23ae22d6c46ffb41c1e4f23e1c02d.<br/>Proceso limpio carga models:/...@champion y reproduce exactamente AP y negocio, sin nuevas llamadas API.


<!-- PAGE -->


# Anticipación y siguiente decisión

## Utilidad para anticipar tutorías

Se evalúan ambas familias finalistas en cohortes propias de semanas 2/4/6 y día 56, con parámetros fijados, cinco folds por estudiante y purga de todos los alumnos presentes en 2014J. El cuadro resume HGB; el anexo conserva ambas familias y los controles E/E+I/L. El denominador de políticas es el Fail de la cohorte inicial (4.914).

| Política | Cohorte elegible | TP / K=1.691 | TP con margen al día 56 | Al día 70 |

| Semana 2 | 17,246 | 915 | 915 | 915 |

| Semana 4 | 16,838 | 1011 | 1011 | 1011 |

| Semana 6 | 16,529 | 1088 | 0 | 1088 |

| Escalonada 40/30/30 | 17,246 | 1017 | 677 | 1017 |

Margen ilustrativo: 7 días de coordinación + 14 de apoyo. Con plazo día 56, semana 4 deja margen y captura 1.011 Fail; semana 6 llega tarde bajo ese supuesto. Semana 2 captura 915 frente a 755 del estático pareado (+160), permitiendo apoyo más temprano. **No son fracasos evitados**: son casos potencialmente atendibles en una simulación.

Un solo presupuesto nace del día 14, por edición/fold; no se repiten matrículas. La escalonada usa 645/501/545 cupos, total 1.691, y selecciona 1.633 personas únicas. Contar matrículas no equivale a contar estudiantes. Los plazos y la unidad de asignación deben acordarse con la Universidad.

## Sin registros: asociación y aporte incremental

En semana 2, Fail es 52,67 % sin registros al corte y 26,78 % con ellos: RR 1,97 (IC 95 % 1,85-2,08), phi 0,143. La diferencia estandarizada por edición es 26,27 pp (98,05 % de población cubierta). AP de HGB: E 0,3965; E+indicador 0,4247; longitudinal 0,4570. Hay asociación y señal incremental en este desarrollo; ni confusión residual ni causalidad quedan resueltas. No se usa "nunca tendrá actividad", que no es observable al corte.

## 8. Limitaciones y conclusión sobre prompting

**Prompting sí es factible y se ensayó.** Su costo operativo puede ser relevante a escala: la adopción de un LLM externo queda como una **decisión de negocio posterior**, para evaluar consumo, latencia, integración, mantenimiento y valor incremental mediante un análisis de **costo-beneficio con la Universidad**. El ensayo costó cerca de USD 1,12 y no prueba un gasto elevado en esta muestra; tampoco justifica su adopción, dado el menor desempeño del GPT probado.

Límites: 2014J es un benchmark ya observado; CV y decisiones reutilizan desarrollo. La maduración de etiquetas no tiene fecha de publicación conocida; el margen curso-terminado/corte sería -12, +2, +16 y +30 días en cortes 14/28/42/56, insuficiente para certificar un despliegue prospectivo temprano. Las probabilidades del proveedor no son deterministas ni se conoce su preentrenamiento sobre OULAD; la reproducción usa respuestas archivadas.

La evidencia termina en predicción y simulación: se requiere cohorte futura y piloto de intervención para medir beneficios causales, costos reales de tutoría y equidad. Las restricciones operativas no se usan para justificar la omisión del LLM. Código, seis notebooks con salidas, CSV, contratos y verificación acompañan la entrega.
