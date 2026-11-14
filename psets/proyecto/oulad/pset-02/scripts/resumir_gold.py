"""Genera resultados Gold y contrasta población con la auditoría del PSet 1."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]

def render():
    build=json.loads((BASE/'docs/dbt-build-gold.json').read_text())
    quality=json.loads((BASE/'docs/calidad-gold.json').read_text())
    silver=json.loads((BASE/'docs/calidad-silver.json').read_text())
    assert build['status']==quality['status']==silver['status']=='ok'
    assert build['checked_at_utc'] < quality['checked_at_utc']
    assert all(r['status'] in ['success','pass'] for r in build['results'])
    m={(r['dataset'],r['metric']):r['value'] for r in quality['metrics']}
    sm={(r['dataset'],r['metric']):r['value'] for r in silver['metrics']}
    assert len(m)==len(quality['metrics'])
    for k,sk in [(('fact_activity_daily','rows'),('activity_daily','rows')),
                 (('fact_activity_daily','clicks'),('activity_daily','clicks')),
                 (('fact_activity_daily','source_rows'),('activity_daily','source_rows')),
                 (('fact_enrollment','rows'),('enrollments','rows')),
                 (('fact_enrollment','without_activity'),('enrollments','without_activity'))]:
        assert m[k]==sm[sk],(k,sk)
    assert m['dimensional_join','rows']==m['fact_activity_daily','rows']
    assert m['dimensional_join','clicks']==m['fact_activity_daily','clicks']
    assert sum(m['outcome_enrollment',c] for c in ['Fail','Withdrawn','Approved'])==m['fact_enrollment','rows']
    population=json.loads((BASE.parent/'pset-01/docs/auditoria-resultados.json').read_text())['populations']
    assert m['fact_enrollment','registered_at_start']==population['initial']['N']
    for day in [14,28,42,56]:
        assert m[f'eligibility_day_{day}','expected_enrollments']==population['cuts'][str(day)]['N']
    old=json.loads((BASE/'docs/dbt-build-silver.json').read_text())
    old_ids={r['unique_id'] for r in old['results']}
    gold_tests=sum(r['unique_id'].startswith('test.') and r['unique_id'] not in old_ids for r in build['results'])
    repeat_path=BASE/'docs/repeticion-gold.json'
    repeat=json.loads(repeat_path.read_text()) if repeat_path.exists() else {}
    repeat_matches=repeat.get('status')=='ok' and repeat.get('second_build_checked_at_utc')==build['checked_at_utc']
    def n(x):return f'{x:,}'.replace(',','.')
    def v(d,k='rows'):return n(m[d,k])
    lines=['# Resultados de Gold', '',
        'Generado por `python3 pset-02/scripts/resumir_gold.py`; las cifras proceden de informes agregados.', '',
        f"Build: {build['checked_at_utc']}; exportación: {quality['checked_at_utc']} (UTC).", '',
        f"**{build['tests_passed']} tests aprobados, cero fallos**: {gold_tests} de Gold y {build['tests_passed']-gold_tests} de Bronze/Silver. Se construyeron diez tablas Gold y se validaron/reconstruyeron las capas anteriores. Tiempo dbt: {build['elapsed_seconds']:.2f} s, sin arranque ni exportación.", '',
        '| Tabla Gold | Filas | Grano |', '|---|---:|---|']
    tables=[('dim_student','Persona'),('dim_edition','Módulo–edición'),('dim_resource','Recurso por módulo–edición'),
            ('dim_enrollment','Matrícula'),('dim_relative_day','Día relativo'),('fact_enrollment','Matrícula'),
            ('fact_activity_daily','Matrícula–recurso–día'),('enrollment_withdrawal','Matrícula'),('outcome_enrollment','Matrícula')]
    for name,grain in tables:lines.append(f'| {name.upper()} | {v(name)} | {grain} |')
    lines += [f"| DQ_GOLD_PROFILE | {len(m)} | Dataset–métrica |", '',
        f"La actividad representa {v('fact_activity_daily','source_rows')} filas originales y conserva **{v('fact_activity_daily','clicks')} clics**. El join con las cinco dimensiones devuelve {v('dimensional_join')} filas y los mismos {v('dimensional_join','clicks')} clics. Los tests comprobaron conservación también por edición y claves completas.", '',
        f"FACT_ENROLLMENT conserva {v('fact_enrollment')} matrículas, incluidas **{v('fact_enrollment','without_activity')} sin actividad**. DIM_STUDENT contiene {v('dim_student')} personas, sin mezclar sus atributos entre matrículas. Los antecedentes variables se mantienen en DIM_ENROLLMENT.", '',
        f"DIM_RELATIVE_DAY contiene {v('dim_relative_day')} días continuos, de {v('dim_relative_day','min_day')} a {v('dim_relative_day','max_day')}, y los {v('dim_relative_day','cutoffs')} cortes de observación. No es un calendario real ni evidencia de cobertura de logs.", '',
        '## Población de referencia para la futura OBT', '',
        'Registro conocido <= 0 y sin retiro registrado <= corte. El cálculo no consulta etiquetas y se contrastó con la auditoría independiente del PSet 1.', '',
        '| Corte | Elegibles Gold | PSet 1 | Coinciden |', '|---|---:|---:|---|']
    for day in [14,28,42,56]:
        actual=m[f'eligibility_day_{day}','expected_enrollments'];expected=population['cuts'][str(day)]['N']
        lines.append(f'| {day} | {n(actual)} | {n(expected)} | Sí |')
    lines += ['',
        'Estos conteos son referencias agregadas. La OBT matrícula–corte se implementó después con Spark y pruebas de perturbación: [guía](obt-spark.md), [resultados](obt-resultados.md).', '',
        f"Resultados retrospectivos separados: Fail={v('outcome_enrollment','Fail')}, Withdrawn={v('outcome_enrollment','Withdrawn')}, Approved={v('outcome_enrollment','Approved')}. Las listas permitidas de columnas protegen hechos y antecedentes de añadir resultados o retiro; el rol del pipeline puede acceder a todas las tablas.", '',
        '## Decisiones y límites', '',
        '| Decisión | Evidencia / efecto | Límite |', '|---|---|---|',
        '| Dos hechos con granos distintos | Matrículas y actividad diaria se reconcilian por separado | Agregar actividad antes de combinar hechos; no sumar matrículas o créditos repetidos por eventos. |',
        '| Atributos por matrícula | DIM_STUDENT identifica; DIM_ENROLLMENT conserva contexto | No se inventa un historial de vigencia ni se elige la matrícula más reciente para todas las personas. |',
        '| Retiro y resultados separados | Elegibilidad usa fechas registradas; evaluación usa OUTCOME_ENROLLMENT | Persisten 93 Withdrawn sin fecha de retiro y la incertidumbre histórica documentada en Silver. |',
        '| Suma de todas las contribuciones | Clics y filas fuente conservados desde Silver | Persisten dudas sobre filas idénticas; Gold no cambia la política ni la sensibilidad de 3,19 %. |',
        '| Sin actividad preservada | La población no parte de los clics | Ausencia de registros no prueba cero actividad real ni cobertura completa. |', '']
    if repeat_matches:
        lines += [f"**Repetición comprobada:** dos builds aprobaron {repeat['tests_passed_per_build']} tests cada uno y mantuvieron las mismas {repeat['compared_metric_count']} métricas agregadas. Se verifican esos invariantes y las reglas de claves; no es una comparación física de todos los bytes.",'',
                  '[Evidencia de repetición correspondiente](repeticion-gold.json).','']
    else:lines += ['**Repetición pendiente para este build:** ejecutar checkpoint/build/export/verify según la guía.','']
    lines += ['Evidencia: [build](dbt-build-gold.json), [métricas](calidad-gold.json), [guía y diagrama](gold.md), [SQL de revisión](../snowflake/07_verificar_gold.sql).', '',
              'Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Publicación GitHub pendiente. La orquestación está verificada según orquestacion-integral.md. Spark y OBT están verificados según obt-spark.md. No hay entrenamiento ni costo monetario cuantificado.', '']
    return '\n'.join(lines)

if __name__=='__main__':
    out=BASE/'docs/gold-resultados.md';out.write_text(render());print('Generado '+str(out.relative_to(BASE)))
