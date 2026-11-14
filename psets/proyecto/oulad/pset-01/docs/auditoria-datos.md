# Auditoría descriptiva de datos

Ejecutada el 12-nov-2026 desde los cinco CSV originales de datasets/. No modifica entradas, no entrena modelos y no ejecuta el pipeline. SHA-256, bytes, fecha local y conteos están en datasets/manifest.json. Fecha de descarga y versión específica del paquete no aportadas; la modificación local no acredita fecha de publicación.

## Poblaciones y denominadores

| Población | N | Fail | Withdrawn | Aprobación | K total | Sin actividad registrada |
|---|---:|---:|---:|---:|---:|---:|
| Original | 32593 | 7052 (21.64 %) | 10156 | 15385 | — | — |
| Registro hasta día 0 | 32314 | 6980 (21.60 %) | 10068 | 15266 | — | — |
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

La unión studentInfo–studentRegistration conserva una fila por matrícula, con validación one_to_one. Las relaciones de actividad se contrastaron con matrícula y recurso usando sus claves completas. La auditoría de duplicados diarios por chunks no demuestra unicidad global: ese test sigue pendiente y no se aplicó deduplicación. No se alteraron datos.

Fechas negativas pueden representar registro o interacción previa al inicio y no son por sí mismas inválidas. Pendientes: cotejar intervalos por duración de edición y disponibilidad de recursos; validar inconsistencias entre retiro y etiqueta; comprobar calendario real, maduración de etiquetas y pares temporales utilizables; confirmar comparabilidad y completitud de cobertura. Valores válidos no demuestran exactitud externa. No hay métricas predictivas ni evidencia de efecto de tutorías.

## Reproducción

Desde la raíz: `.venv/bin/python pset-01/scripts/auditar_datos.py`. Ruta alternativa: añadir `--data-dir /ruta/autorizada`. La ruta por defecto se deriva del script, no del directorio actual. El script falla ante archivos o claves principales incompatibles. Consultar requirements.txt para versiones usadas.
