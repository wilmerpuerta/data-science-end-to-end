# Resultados de calidad y Bronze

Archivo generado por `python3 pset-02/scripts/resumir_bronze.py`; no editar cifras manualmente.

Build: 2026-11-13T00:16:26.157136+00:00. Exportación de métricas: 2026-11-13T15:02:36.319390+00:00. Ambos en UTC.

Resultado: cinco vistas Staging y una tabla agregada construidas; **45 tests aprobados, cero fallos**. Duración dbt: 26.66 s, excluye arranque del contenedor y exportación. Raw no se modificó.

| Fuente / vista | Filas conservadas |
|---|---:|
| studentInfo | 32.593 |
| studentRegistration | 32.593 |
| courses | 22 |
| vle | 6.364 |
| studentVle | 10.655.280 |

Las 32.593 matrículas corresponden a 28.785 personas distintas. Total de clics: **39.605.099**. Las claves de matrícula y recurso son únicas en sus tablas maestras; no hay huérfanos en las relaciones probadas ni errores de conversión.

| Problema o condición | Evidencia | Acción en esta etapa | Justificación / siguiente decisión |
|---|---|---|---|
| IMD vacío | 1.111 / 32.593 (3,41 %) | NULL en Bronze, sin imputación | Es un atributo desconocido; una imputación aprendida se ajustará solo con entrenamiento. |
| Registro sin fecha | 45 / 32.593 (0,14 %) | Conservar matrícula y marcar ausencia | El contrato posterior exige registro conocido <= 0 para población inicial; la exclusión se contará al construir elegibilidad. |
| Registro posterior al inicio | 234 / 32.593 (0,72 %) | Conservar fecha | No es error de tipo; queda fuera de población inicial por la regla del proyecto. |
| Sin fecha de retiro registrada | 22.521 / 32.593 (69,10 %) | Conservar NULL | No equivale a un faltante genérico ni prueba que nunca hubo retiro. No inventar una fecha. |
| Resultado Withdrawn sin fecha de retiro | 93 / 32.593 (0,29 %) | Señalar inconsistencia; no inferir fecha con la etiqueta | Limita la reconstrucción de elegibilidad histórica. Tratamiento y sensibilidad deben documentarse; no usar resultado futuro como predictor. |
| Otro resultado con fecha de retiro | 9 / 32.593 (0,03 %) | Conservar ambos datos y señalar conflicto | No podemos corregir el registro institucional desde estos CSV. |
| Semanas del recurso ausentes | week_from: 5.243 / 6.364 (82,39 %); week_to: 5.243 / 6.364 (82,39 %) | Mantener NULL | No usar estas semanas como prueba de cobertura ni sustituir por semana cero. |
| Clave matrícula–recurso–día repetida | 2.195.960 / 10.655.280 (20,61 %) filas adicionales respecto de claves distintas | Conservar todas las filas | La futura agregación diaria debe reconciliar clics; repetición no demuestra por sí sola error de captura. |
| Valores de evento idénticos, incluido sum_click | 787.170 / 10.655.280 (7,39 %) filas adicionales respecto de valores distintos | Sin deduplicación automática | No hay identificador del evento original ni evidencia para afirmar cuál copia sobra. |
| Actividad anterior al inicio | 688.988 / 10.655.280 (6,47 %); días -25 a 269 en el conjunto | Conservar días negativos | Se tratará como antecedente separado de ventanas quincenales. |

Se observaron cero clics negativos, cero filas con sum_click=0, cero retiros anteriores al registro conocido, cero intervalos de semanas invertidos y cero duraciones no positivas. Ausencia de estos problemas no acredita exactitud externa.

La auditoría global encuentra **2.195.960** filas adicionales por clave diaria. El PSet 1 comunicó una cota inferior de 2.195.910 dentro de bloques; los 50 casos adicionales proceden de comprobar el archivo completo. Se conserva el informe histórico del PSet 1 como evidencia de su alcance.

Los tests validan reglas declaradas, no que todos los problemas de negocio estén resueltos. Las anomalías anteriores se conservan explícitamente en Bronze; la consolidación y las banderas Silver se documentan en [silver.md](silver.md). Gold se documenta en [gold.md](gold.md). La OBT se documenta en [obt-spark.md](obt-spark.md). La orquestación se documenta en [orquestacion-integral.md](orquestacion-integral.md). No hay entrenamiento.

Fuentes reproducibles: [build dbt](dbt-build-bronze.json), [métricas agregadas](calidad-bronze.json), [guía y comandos](calidad-bronze.md).
