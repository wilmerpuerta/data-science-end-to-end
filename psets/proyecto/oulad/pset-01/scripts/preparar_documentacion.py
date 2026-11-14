from generar_contenidos import ROOT,write
import json
def main():
 a=json.loads((ROOT/'pset-01/docs/auditoria-resultados.json').read_text()); p=a['populations']
 lines=['# Auditoría descriptiva de datos','', 'Ejecutada el 12-nov-2026 desde los cinco CSV originales de datasets/. No modifica entradas, no entrena modelos y no ejecuta el pipeline. SHA-256, bytes, fecha local y conteos están en datasets/manifest.json. Fecha de descarga y versión específica del paquete no aportadas; la modificación local no acredita fecha de publicación.','', '## Poblaciones y denominadores','', '| Población | N | Fail | Withdrawn | Aprobación | K total | Sin actividad registrada |','|---|---:|---:|---:|---:|---:|---:|']
 for k,c in [('Original',p['original']),('Registro hasta día 0',p['initial'])]+[(f'Día {d}',c) for d,c in p['cuts'].items()]:
  lines.append(f"| {k} | {c['N']} | {c['Fail']} ({100*c['Fail']/c['N']:.2f} %) | {c['Withdrawn']} | {c['Approved']} | {c.get('K_sum_by_edition','—')} | {c.get('without_recorded_activity','—')} |")
 lines+=['',f"{p['unique_students']} personas únicas en la tabla original. Se excluyen de la población inicial {p['late_registration']} registros posteriores al día 0 y {p['missing_registration_date']} fechas de registro ausentes. No se imputaron estas últimas como registro temprano. En cada corte se excluye retiro con fecha <= corte; se mantienen retiros futuros. K total es la suma de floor(0.10 × N) por edición, no floor sobre el agregado.",'','Los conteos por módulo y edición, para original, inicial y cada corte, se conservan en poblaciones-por-edicion.csv. Numeradores: clases de final_result, agrupando Pass y Distinction; denominadores: filas elegibles según regla. Las matrículas sin eventos <= corte se preservan y no se equiparan automáticamente a inactividad: la cobertura real de registro debe comprobarse. Se incluye actividad de fechas negativas como observada antes del corte.','', '## Claves, relaciones y calidad','']
 for k,v in a['checks'].items(): lines.append(f'- {k}: `{json.dumps(v,ensure_ascii=False)}`.')
 lines+=['','## Completitud por columna','']
 for k,v in a['missing_values'].items(): lines.append(f'- {k}: `{json.dumps(v,ensure_ascii=False)}`.')
 lines+=['','## Interpretación y pendientes','', 'La unión studentInfo–studentRegistration conserva una fila por matrícula, con validación one_to_one. Las relaciones de actividad se contrastaron con matrícula y recurso usando sus claves completas. La auditoría de duplicados diarios por chunks no demuestra unicidad global: ese test sigue pendiente y no se aplicó deduplicación. No se alteraron datos.','', 'Fechas negativas pueden representar registro o interacción previa al inicio y no son por sí mismas inválidas. Pendientes: cotejar intervalos por duración de edición y disponibilidad de recursos; validar inconsistencias entre retiro y etiqueta; comprobar calendario real, maduración de etiquetas y pares temporales utilizables; confirmar comparabilidad y completitud de cobertura. Valores válidos no demuestran exactitud externa. No hay métricas predictivas ni evidencia de efecto de tutorías.','', '## Reproducción','', 'Desde la raíz: `.venv/bin/python pset-01/scripts/auditar_datos.py`. Ruta alternativa: añadir `--data-dir /ruta/autorizada`. La ruta por defecto se deriva del script, no del directorio actual. El script falla ante archivos o claves principales incompatibles. Consultar requirements.txt para versiones usadas.']
 write('pset-01/docs/auditoria-datos.md','\n'.join(lines))
 write('datasets/README.md','''# Datos compartidos: OULAD

Fuente oficial: The Open University, https://research.stem.open.ac.uk/ouanalyse/dataset/. Publicación: Kuzilek, Hlosta y Zdrahal (2017), https://doi.org/10.1038/sdata.2017.171. Histórico 2013–2014, licencia CC BY 4.0; mantener atribución. No se afirma una actualización reciente del conjunto histórico.

Colocar aquí los originales sin modificar: studentInfo.csv (matrícula, antecedentes y resultado), studentRegistration.csv (registro/retiro), courses.csv (edición y duración), vle.csv (recursos) y studentVle.csv (interacciones diarias). assessments.csv y studentAssessment.csv están presentes, pero no forman parte del entrenamiento principal ni de los cinco archivos auditados. No se copian datos de otros proyectos.

Los CSV están excluidos de Git. Para reproducir desde un clon, obtener legalmente el paquete OULAD desde la fuente oficial, extraer estos cinco nombres y comprobar identidad con manifest.json antes de ejecutar. La versión concreta de descarga no fue facilitada: los hashes identifican esta copia y no prueban por sí solos autenticidad respecto al proveedor. Si difieren, registrar nueva versión y reconciliar el análisis; no afirmar reproducción idéntica.

Verificar un archivo con `shasum -a 256 datasets/studentInfo.csv` desde raíz y contrastar con el manifiesto; repetir para los cinco. La auditoría recalcula todos los hashes y conteos mediante `python pset-01/scripts/auditar_datos.py` en un entorno con las dependencias declaradas. manifest.json contiene origen, licencia, histórico/publicación, fecha de auditoría UTC, nombre, SHA-256, bytes, filas y modificación local. La fecha original de descarga permanece desconocida.

PSet 1 solo audita descriptivamente. PSet 2 consumirá ../datasets con montaje de solo lectura cuando se implemente. Cada etapa guarda derivados en su propio árbol. [Auditoría y límites](../pset-01/docs/auditoria-datos.md).
''')
 write('pset-02/.env.example','''# Ejemplos ficticios. No hay servicios ni credenciales configurados.
# Ruta resuelta desde pset-02/ por el futuro Compose.
OULAD_DATA_DIR=../datasets
SNOWFLAKE_ACCOUNT=organizacion-cuenta-ejemplo
SNOWFLAKE_USER=USUARIO_EJEMPLO
SNOWFLAKE_PASSWORD=CAMBIAR_SOLO_EN_ENV_LOCAL
SNOWFLAKE_ROLE=ROL_PSETS_EJEMPLO
SNOWFLAKE_WAREHOUSE=WH_PSETS_EJEMPLO
SNOWFLAKE_DATABASE=DB_PSETS_EJEMPLO
SNOWFLAKE_SCHEMA=RAW
# Diseño preliminar: usuario/contraseña solo para desarrollo autorizado.
# Confirmar política de cuenta y migrar variables si se elige clave privada.
''')
 write('pset-02/docs/plan-implementacion.md','''# Plan de implementación pendiente

Todas las decisiones de esta página son diseño. No se ejecutaron contenedores, cargas, dbt, Spark ni recursos Snowflake. El documento final previsto será PSet2_memo_Puerta_Wilmer.pdf, máximo seis páginas sin anexos, cuando existan evidencias de implementación.

## Arquitectura prevista

```mermaid
flowchart LR
  F[CSV OULAD de solo lectura] --> K[Kestra]
  K --> R[Snowflake Raw]
  R --> B[dbt Bronze / Staging]
  B --> S[dbt Silver]
  S --> G[dbt Gold estrella]
  G --> P[Spark OBT matrícula-corte]
  P --> O[Snowflake OBT]
```

Se propone dbt Core en Docker para versionar transformaciones junto a Kestra y Spark. Confirmar compatibilidad del adaptador Snowflake, conectores JVM, versiones de Java y Python al implementar. No existen versiones de infraestructura fijadas ni locks resueltos todavía. No utilizar latest como prueba de reproducibilidad.

## Secuencia y criterios concretos

1. Registrar Docker Engine/Compose, arquitectura del equipo y recursos disponibles; medir CPU, memoria y disco con los 10.655.280 registros de actividad antes de fijar mínimos. Fijar imágenes por versión/digest y probar salud de Kestra y Spark, persistencia y reinicio. Crear docker-compose.yml solo con servicios implementados y verificados.
2. Resolver OULAD_DATA_DIR=../datasets desde pset-02/. Montar explícitamente solo lectura, comprobar hashes dentro del contenedor y prohibir escritura sobre originales. Configurar secretos locales sin imprimirlos. Definir rol mínimo, warehouse, base y esquemas en Snowflake con instrucciones de creación, privilegios y dependencias cloud verificadas. Docker no reproduce Snowflake.
3. Carga inicial manualmente disparada por ejecución autenticada; futuras ejecuciones quincenales solo comprueban cambios de manifiesto. OULAD es estático: misma huella produce no-op o reemplazo determinista, no nuevos datos inventados. Programar trigger y zona horaria documentados al implementar.
4. Kestra valida archivos, registra run_id, checksum, filas, partición módulo–edición y estado. Diseñar tres reintentos con espera exponencial para fallos transitorios; errores de esquema/calidad fallan sin publicación. Backfill por archivo/edición con checkpoints y reconciliación, reanudando solo particiones fallidas. Logs sin secretos.
5. Raw conserva carga fiel, metadatos y linaje. Usar staging temporal y publicación transaccional o MERGE por claves acordadas. Reejecutar misma huella/partición debe conservar conteos y unicidad. Una nueva huella se registra como versión, nunca se mezcla silenciosamente.
6. dbt source() para Raw y ref() para dependencias. Bronze/Staging tipa y marca anomalías, Silver aplica limpieza justificada y Gold construye estrella. Tests not_null, unique compuesta, relationships, clases, fechas contextuales y cardinalidad. Registrar tabla problema–evidencia–acción–justificación con métricas reales, evitando copiar los ejemplos 120 y 4.3 %.
7. Spark construye OBT desde población elegible antes de unir agregados de actividad, usando left joins. Comparar claves y filas antes/después, preservar ceros y distinguir cobertura desconocida. Escribir OBT en Snowflake por matrícula–corte con control de cargas.
8. Desde clon limpio: obtener datos identificados, verificar hashes, crear entorno/credenciales y recursos cloud documentados, levantar servicios fijados, comprobar salud, ejecutar Raw, dbt y Spark en orden, verificar tablas y evidencias. Repetir carga para demostrar idempotencia, simular fallo y backfill, y guardar logs sanitizados y resultados de tests.

## Calidad y publicación

Completitud: proporción no nula de campos requeridos, por fuente y edición. Validez: conformidad de tipos, dominios y rangos contextuales. Consistencia: relaciones entre fuentes, unicidad, conteos y coherencia temporal. Precisión/exactitud externa requiere cotejo con realidad o proveedor y no se demuestra copiando fielmente un CSV. No deduplicar sin evidencia de grano y regla justificable. Las anomalías aún no resueltas se publican como limitaciones.

## Batch, costo y operación

Batch basta para revisión quincenal y un histórico estático. Streaming se justificaría con fuente institucional continua y necesidad demostrada de reacción de baja latencia, antes de rediseñar contratos y operación; no se implementará ahora. En ejecución futura medir consumo y costo Snowflake, fijar auto-suspend y auto-resume, limitar warehouse, detener servicios y limpiar recursos temporales conservando evidencia. No se afirma gratuidad ni consumo comprobado.
''')
 write('pset-02/docs/contrato-datos.md','''# Contrato preliminar de datos v1

Estado: diseño para implementación posterior. La auditoría local de PSet 1 aporta conteos, no tablas ELT construidas.

## Grano, población y tiempo

Matrícula: (id_student, code_module, code_presentation). Edición: (code_module, code_presentation). Recurso: (id_site, code_module, code_presentation). Evento fuente: matrícula + id_site + date, sujeto a comprobar unicidad global antes de consolidar. OBT: matrícula + cutoff_day en {14,28,42,56}, hasta cuatro filas por matrícula. Día 0 es inicio oficial y el corte incluye el final del día. Registro <= 0 y no nulo define población inicial; registro ausente se excluye con conteo. Elegibilidad excluye retiro <= corte; no consulta retiro futuro para formar predictores.

Construir población elegible antes de agregar/unir actividad y preservar matrículas sin clics mediante left joins. Predictores usan solo información <= corte. El target final, retiradas futuras y resultados finales van a una tabla separada para evaluación retrospectiva. Una exportación de características utilizará lista permitida explícita y test de ausencia de target/fecha futura. Sin notas de assessments en la comparación principal.

Ventanas comparables: días 1–14, 15–28, 29–42, 43–56. Día 0 y actividad negativa se conservan como antecedentes de actividad separados, sin mezclarlos con quincenas de 14 días. Acumulados pueden incluirlos con nombre explícito. Recencia usa última interacción <= corte; nunca activos con cobertura acreditada cuentan desde día 0; cobertura desconocida se marca y exige política común fijada antes de prueba. Primer corte sin cambio entre dos quincenas completas. Validar fechas y recursos disponibles por edición antes de imponer rangos. La documentación de semanas de recursos no prueba cobertura exhaustiva de logs.

## Estrella Gold propuesta

| Tabla | Grano y uso |
|---|---|
| dim_student | Una persona anonimizada; atributos cambiantes no se sobreescriben globalmente |
| dim_edition | Un módulo–edición, duración y calendario validado |
| dim_resource | Un recurso por módulo–edición |
| dim_relative_day | Día relativo, con admisión documentada de valores negativos |
| fact_enrollment | Una matrícula, antecedentes al inicio y estado de registro |
| fact_activity_daily | Matrícula–recurso–día, clics agregados según auditoría de duplicados |
| outcome_enrollment | Una matrícula y resultado final, uso retrospectivo separado |
| obt_features | Matrícula–corte, una fila elegible y features disponibles |

```mermaid
erDiagram
 dim_student ||--o{ fact_enrollment : persona
 dim_edition ||--o{ fact_enrollment : edicion
 fact_enrollment ||--o{ fact_activity_daily : matricula
 dim_resource ||--o{ fact_activity_daily : recurso
 dim_relative_day ||--o{ fact_activity_daily : dia
 fact_enrollment ||--o{ obt_features : corte
 fact_enrollment ||--o| outcome_enrollment : resultado
```

La estrella sirve para análisis reutilizable de actividad y dimensiones; la OBT para consumo del modelo por corte. Agregar hechos de actividad antes de unir matrícula, evitando multiplicar eventos o sumar antecedentes repetidos. No sumar clics acumulados entre cortes como si fueran eventos distintos. Conservar linaje de carga y versión de contrato.

## Transformaciones y pruebas futuras

ELT calcula reglas deterministas y agregaciones por corte. Imputación aprendida, escalado, selección o codificación ajustada a distribución se aprenden solo con entrenamiento. Prueba temporal: etiquetas maduras antes de predicción simulada, alumnos separados, cortes de matrícula en una sola partición. Seleccionar pares de ediciones después de validar calendario; no se declara válida todavía una partición específica.

Tests: unicidad y no nulos de claves; relaciones completas; suma de eventos y clics Raw–Silver–Gold reconciliada con exclusiones; clases válidas; N elegible calculado independientemente igual a filas OBT por corte; anti-join de claves antes/después; ausencia de multiplicación en joins; matrículas sin actividad preservadas; perturbación de eventos futuros no cambia features pasadas; idempotencia de una partición. Cuantificar reglas fallidas y documentar tratamiento sin correcciones silenciosas.

Completitud mide presencia respecto a campos esperados, validez conformidad a dominios/rangos y consistencia coherencia entre tablas/reglas. Exactitud respecto a la realidad externa permanece sin demostrar sin evidencia adicional. Los nulos de retiro pueden representar continuidad, no faltante genérico.
''')
 write('pset-02/README.md','''# PSet 2: pipeline de datos del proyecto OULAD

Autor: Wilmer Puerta. Continuidad de la propuesta de focalización preventiva del [PSet 1](../pset-01/README.md).

| Estado | Alcance |
|---|---|
| Preparado | [Enunciado](enunciado.md), [rúbrica](rubrica.md), [plan](docs/plan-implementacion.md), [contrato](docs/contrato-datos.md), [.env.example](.env.example) y carpetas de trabajo |
| Pendiente de implementación | Compose, Kestra, dbt, Spark, Snowflake, diagramas de implementación y memo técnico |
| Verificado en ejecución | Ningún componente del pipeline. Solo auditoría descriptiva local de PSet 1 |

Flujo requerido: Fuente → Kestra → Raw → dbt/Bronze → dbt/Silver → dbt/Gold → Spark/OBT, persistencia en Snowflake. El diseño propone dbt Core en Docker, con al menos Kestra y Spark en Compose; verificar compatibilidad y fijar versiones/digests al instalar. No hay Compose vacío ni etiquetas latest o locks inventados.

Datos: [../datasets](../datasets/README.md). OULAD_DATA_DIR=../datasets se resolverá desde pset-02 y se montará solo lectura. No hay rutas personales. Docker/Compose y recursos mínimos se medirán al implementar, incluidos conectores, Java, memoria y disco. Snowflake requiere cuenta, permisos, warehouse y configuración cloud aparte de Docker. Variables ficticias en .env.example; credenciales solo en .env local excluido de Git.

Arranque previsto, aún sin comandos operativos verificados: obtener datos y comprobar hashes; configurar credenciales y crear recursos documentados; levantar Compose; comprobar salud; disparar Kestra y reconciliar Raw; ejecutar dbt y sus tests; construir OBT con Spark; verificar tablas, grano, cardinalidad, idempotencia y backfill. El [plan](docs/plan-implementacion.md) fija criterios y dependencias para convertir esta secuencia en comandos reales cuando exista código.

Trigger previsto: carga inicial y comprobación quincenal de huellas, sin atribuir nuevos datos a un histórico estático. Reintentos transitorios y backfill por módulo–edición con run_id, logs sanitizados y checksum. Batch satisface revisión quincenal; streaming requeriría fuente continua y una necesidad validada de baja latencia. No se implementa streaming.

Reproducción desde clon limpio incluirá datos identificados, infraestructura local fijada, creación de recursos y privilegios cloud, ejecución ordenada y evidencia de tests. Docker por sí solo no reproduce Snowflake. Costos sin medir: prever auto-suspend, límites y limpieza controlada. Documento técnico futuro: máximo seis páginas sin anexos, PSet2_memo_Puerta_Wilmer.pdf. No se genera ahora un memo que describa una implementación inexistente.
''')
 write('.gitignore','''# Datos crudos y derivados; conservar metadatos
datasets/*
!datasets/README.md
!datasets/manifest.json
.env
.env.*
!.env.example
**/.env
**/.env.*
!**/.env.example
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.DS_Store
.cache/
node_modules/
tmp/
backups/
*.log
*.tmp
# PDF, PPTX, PPT y notebook finales sí se versionan.
''')
 print('Documentación y continuidad preparadas')
if __name__=='__main__': main()
