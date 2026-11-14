"""Genera resultados Silver en Markdown desde evidencia pública de ejecución."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]

def render():
    build=json.loads((BASE/'docs/dbt-build-silver.json').read_text())
    quality=json.loads((BASE/'docs/calidad-silver.json').read_text())
    repeat_path=BASE/'docs/repeticion-silver.json'
    repeat=json.loads(repeat_path.read_text()) if repeat_path.exists() else {}
    assert build['status']==quality['status']=='ok'
    assert build['checked_at_utc'] < quality['checked_at_utc']
    repeat_matches=(repeat.get('status')=='ok' and
                    repeat.get('second_build_checked_at_utc')==build['checked_at_utc'])
    results=build['results'];assert all(r['status'] in ['success','pass'] for r in results)
    bronze_report=json.loads((BASE/'docs/dbt-build-bronze.json').read_text())
    bronze_ids={r['unique_id'] for r in bronze_report['results']}
    silver_tests=sum(r['unique_id'].startswith('test.') and r['status']=='pass' and
                     r['unique_id'] not in bronze_ids for r in results)
    m={(x['dataset'],x['metric']):x for x in quality['metrics']}
    def v(d,k):return m[d,k]['value']
    def n(x):return f'{x:,}'.replace(',','.')
    def s(d,k):return n(v(d,k))
    assert v('activity_daily','source_rows')-v('activity_daily','rows')==v('activity_daily','natural_key_excess')
    assert sum(v('outcomes',c) for c in ['Fail','Withdrawn','Approved'])==v('enrollments','rows')
    assert sum(v('registration',c) for c in ['registered_at_start','missing_registration','late_registration'])==v('enrollments','rows')
    bronze=json.loads((BASE/'docs/calidad-bronze.json').read_text())
    bm={(r['dataset'],r['metric']):r['value'] for r in bronze['metrics']}
    assert v('activity_daily','clicks')==bm['student_vle','total_clicks']
    assert v('activity_daily','source_rows')==bm['student_vle','rows']
    loss=v('activity_daily','clicks')-v('sensitivity','clicks_if_exact_deduplicated')
    percentage=f"{100*loss/v('activity_daily','clicks'):.2f}".replace('.',',')
    repeat_text=(f"**Repetición comprobada:** dos builds distintos aprobaron {repeat['tests_passed_per_build']} pruebas cada uno y produjeron las mismas {repeat['compared_metric_count']} métricas agregadas. La comprobación cubre conteos, clics y condiciones de calidad junto con los tests de claves; no es una comparación física de todos los bytes almacenados."
                 if repeat_matches else
                 '**Repetición pendiente para este build:** seguir el procedimiento checkpoint/build/export/verify de la guía. Una evidencia anterior no se aplica automáticamente a una ejecución nueva.')
    lines=['# Resultados de Silver', '',
        'Generado por `python3 pset-02/scripts/resumir_silver.py`; las cifras proceden de los JSON enlazados.', '',
        f"Build: {build['checked_at_utc']}; exportación: {quality['checked_at_utc']} (UTC).", '',
        f"**{build['tests_passed']} tests aprobados, cero fallos**: {silver_tests} de Silver y {build['tests_passed']-silver_tests} de Bronze. Se construyeron siete tablas Silver y se renovaron cinco vistas y una tabla de calidad Bronze. Tiempo dbt del último build: {build['elapsed_seconds']:.2f} s, sin arranque/exportación.", '',
        '| Tabla Silver | Filas |', '|---|---:|']
    for table,d in [('SLV_EDITIONS','editions'),('SLV_RESOURCES','resources'),('SLV_ENROLLMENTS','enrollments'),('SLV_REGISTRATION','registration'),('SLV_OUTCOMES','outcomes'),('SLV_ACTIVITY_DAILY','activity_daily')]:
        lines.append(f'| {table} | {s(d,"rows")} |')
    lines += ['',f"La consolidación representa las **{s('activity_daily','source_rows')} filas fuente** mediante **{s('activity_daily','rows')} claves diarias únicas**, conservando **{s('activity_daily','clicks')} clics**. La diferencia de {s('activity_daily','natural_key_excess')} filas queda explicada por multiplicidad; los tests reconciliaron claves completas, filas representadas y clics por edición.", '',
        '| Problema o condición | Evidencia | Acción | Justificación |', '|---|---|---|---|',
        f"| Varias contribuciones por clave diaria | {s('activity_daily','multiple_source_groups')} grupos con más de una fila fuente | Sumar clics, conservar multiplicidad y linaje | Grano diario único sin pérdida de contribuciones registradas; no acredita ausencia de duplicación semántica. |",
        f"| Filas fuente idénticas | {s('activity_daily','exact_value_excess')} filas adicionales | Mantenerlas en la suma principal; cuantificar sensibilidad | Eliminarlas produciría {s('sensitivity','clicks_if_exact_deduplicated')} clics: {n(loss)} menos ({percentage} %). No hay evidencia externa para seleccionar esa corrección. |",
        f"| Matrículas sin actividad en todo el archivo | {s('enrollments','without_activity')} | Preservarlas en antecedentes | La OBT deberá partir de matrículas elegibles y usar left joins; ausencia de logs no garantiza cobertura. |",
        f"| IMD ausente | {s('enrollments','missing_imd')} | NULL e IS_IMD_MISSING | No aprender imputaciones globalmente durante ELT. |",
        f"| Semanas de recurso desconocidas | {s('resources','unknown_schedule')} | NULL e IS_SCHEDULE_UNKNOWN | No inventar semanas ni deducir cobertura completa. |",
        f"| Registro desconocido / tardío | {s('registration','missing_registration')} / {s('registration','late_registration')} | Conservar; clasificar explícitamente | Se excluyen de población inicial más adelante conforme al contrato, con conteo. |",
        f"| Conflictos entre resultado y retiro | Withdrawn sin fecha: {s('outcomes','withdrawn_without_date')}; otro resultado con fecha: {s('outcomes','other_outcome_with_date')} | Banderas solo en SLV_OUTCOMES | No convertir etiqueta futura en fecha de retiro ni predictor. |",
        f"| Actividad anterior al inicio | {s('activity_daily','prestart_groups')} grupos, {s('activity_daily','prestart_clicks')} clics | Conservar días negativos | Antecedentes separados de ventanas quincenales. |", '',
        f"**Registro inicial:** {s('registration','registered_at_start')} matrículas tienen registro conocido <= 0, consistente con el PSet 1. De ellas, {s('enrollments','registered_at_start_without_activity')} no tienen actividad en el archivo y {s('registration','withdrawn_by_start')} tienen retiro conocido <= 0. Todavía no es una tabla de elegibles por corte; no sumar ni restar subgrupos como si fueran disjuntos.", '',
        f"**Etiquetas retrospectivas:** Fail={s('outcomes','Fail')}, Withdrawn={s('outcomes','Withdrawn')}, Approved={s('outcomes','Approved')}. Se conservan las clases originales y sus conteos por edición; no se incluyen en SLV_ENROLLMENTS.", '',
        repeat_text, '',
        'Gold se implementó después: [guía y diagrama](gold.md), [resultados](gold-resultados.md). Spark y OBT se implementaron después: [guía](obt-spark.md), [resultados](obt-resultados.md). La orquestación se verificó después: [guía](orquestacion-integral.md), [resultados](pipeline-resultados.md). La reproducción desde exportación limpia se verificó: [resultados](reproduccion-resultados.md). La incertidumbre sobre repetición semántica y retiro sin fecha permanece documentada.', '',
        'Evidencia: [build](dbt-build-silver.json), [calidad](calidad-silver.json), [guía de ejecución y decisiones](silver.md), [SQL de revisión](../snowflake/06_verificar_silver.sql).', '']
    if repeat_matches:lines[-1:-1]=['[Informe de repetición correspondiente](repeticion-silver.json).','']
    return '\n'.join(lines)

if __name__=='__main__':
    out=BASE/'docs/silver-resultados.md';out.write_text(render());print('Generado '+str(out.relative_to(BASE)))
