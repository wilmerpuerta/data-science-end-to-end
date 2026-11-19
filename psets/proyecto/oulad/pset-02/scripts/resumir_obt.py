"""Genera Markdown OBT desde ejecución real, contrato y auditoría independiente."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
def render():
    r=json.loads((BASE/'docs/obt-verificacion.json').read_text())
    contract=json.loads((BASE/'spark/feature-contract.json').read_text())
    audit=json.loads((BASE.parent/'pset-01/docs/auditoria-resultados.json').read_text())['populations']['cuts']
    gold=json.loads((BASE/'docs/calidad-gold.json').read_text())
    gm={(x['dataset'],x['metric']):x['value'] for x in gold['metrics']}
    assert r['status']=='ok' and r['published'] and r['rows']==r['unique_keys']
    assert r['output_columns']==contract['output_columns']
    assert not set(contract['forbidden_columns']) & set(r['output_columns'])
    assert r['temporal_tests_passed']==len(contract['cutoff_days']) and r['readback_all_columns_equal']
    assert r['population_key_sets_equal'] and r['gold_source_sha256_verified']
    cuts={x['cutoff_day']:x for x in r['per_cutoff']}
    assert set(cuts)==set(contract['cutoff_days'])
    assert sum(x['rows'] for x in cuts.values())==r['rows']
    for day,part in cuts.items():
        assert part['rows']==audit[str(day)]['N']==gm[f'eligibility_day_{day}','expected_enrollments']
        assert part['without_recorded_activity']==audit[str(day)]['without_recorded_activity']
        assert part['future_perturbation_unchanged']
    def n(x):return f'{x:,}'.replace(',','.')
    lines=['# Resultados de la OBT con Spark','',
        'Generado por `python3 pset-02/scripts/resumir_obt.py`; no editar cifras manualmente.','',
        f"Inicio de comprobación UTC: {r['checked_at_utc']}. Run: {r['run_id']}. Duración: {r['elapsed_seconds']:.2f} s.",'',
        f"**{r['destination']} publicada: {n(r['rows'])} filas y {len(r['output_columns'])} columnas; {n(r['unique_keys'])} claves matrícula–corte únicas.** Se leyeron {n(r['activity_rows_extracted'])} filas diarias Gold con día <= 56; las cinco versiones de fuente coinciden con el manifiesto.",'',
        '| Corte | Filas OBT | Gold y PSet 1 | Sin actividad registrada al corte | Clics acumulados de elegibles | Clics ventana actual |',
        '|---|---:|---:|---:|---:|---:|']
    for day in contract['cutoff_days']:
        p=cuts[day];lines.append(f"| {day} | {n(p['rows'])} | {n(audit[str(day)]['N'])} | {n(p['without_recorded_activity'])} | {n(p['recorded_clicks'])} | {n(p['window_clicks'])} |")
    lines += ['',
        'Los clics acumulados incluyen preinicio, día cero y días 1..corte. Los totales de diferentes cortes no se suman: contienen historia repetida y poblaciones elegibles distintas. Las ventanas actuales son 1–14, 15–28, 29–42 y 43–56.','',
        '## Verificaciones ejecutadas','',
        '- Contexto real del usuario de servicio comprobado desde Spark; conector 3.2.3-spark_3.5/JDBC 4.4.1 y Spark 3.5.6/Scala 2.12.18/Java 17.',
        '- Siete casos sintéticos aprobados antes de construir con OULAD.',
        '- Población calculada antes de actividad; igualdad completa de claves con referencia SQL independiente por corte; conteos y ausencias coinciden con la auditoría PSet 1.',
        '- Unicidad matrícula–corte, conservación en joins y ausencia de pérdida de matrículas sin actividad.',
        '- Cuatro pruebas reales de perturbación: clics futuros modificados y evento futuro insertado para una matrícula elegible; ninguna feature pasada cambió.',
        '- Recencia no negativa; recencia NULL cuando no hay actividad; primera comparación entre quincenas NULL; contadores temporales reconciliados.',
        '- Lectura de vuelta desde Snowflake igual al DataFrame completo, en ambas direcciones, antes de publicar.',
        '- Lista de columnas permitidas y exclusión de resultado final, target y fecha de retiro.','',
        '## Columnas y uso futuro','',
        f"El contrato separa {len(contract['identifier_columns'])} identificadores, {len(contract['static_predictor_columns'])} predictores estáticos, {len(contract['activity_predictor_columns'])} predictores de actividad y {len(contract['audit_columns'])} campos de auditoría. Los identificadores y auditoría no se convierten automáticamente en variables del modelo.",'',
        '| Rol | Columnas |','|---|---|']
    for role,key in [('Identificadores','identifier_columns'),('Estáticas','static_predictor_columns'),('Actividad','activity_predictor_columns'),('Auditoría','audit_columns')]:
        lines.append('| '+role+' | '+', '.join('`'+c+'`' for c in contract[key])+' |')
    lines += ['',
        'Los ceros de contadores significan cero registros observados; no prueban ausencia real de actividad académica. LOG_COVERAGE_KNOWN permanece false y la recencia ausente se mantiene NULL. No hubo imputación aprendida, escalado, encoding ajustado ni entrenamiento. OUTCOME_ENROLLMENT permanece separado para evaluación retrospectiva.','']
    repeat_path=BASE/'docs/repeticion-obt.json'
    repeat=json.loads(repeat_path.read_text()) if repeat_path.exists() else {}
    if repeat.get('status')=='ok' and repeat.get('second_run_id')==r['run_id']:
        lines += [f"**Repetición comprobada:** dos ejecuciones publicaron {n(repeat['rows_per_run'])} filas cada una, con las mismas cuatro huellas SHA-256 canónicas, columnas, población y métricas. Cada ejecución verificó lectura de vuelta completa y perturbaciones futuras.",'',
                  '[Informe de repetición correspondiente](repeticion-obt.json).','']
    else:lines += ['**Repetición pendiente para esta ejecución:** seguir checkpoint/build-obt/verify de la guía.','']
    lines += ['Evidencia: [ejecución OBT](obt-verificacion.json), [conexión Spark](spark-conexion.json), [casos sintéticos](spark-pruebas.json), [contrato](../spark/feature-contract.json), [guía](obt-spark.md), [SQL de revisión](../snowflake/08_verificar_obt.sql).','',
        'Orquestación integral verificada: [guía](orquestacion-integral.md), [resultados](pipeline-resultados.md). Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Pendientes: costo monetario y publicación GitHub. Persisten limitaciones de cobertura de logs, exactitud externa y retiro sin fecha; no se declara validado un modelo predictivo.','']
    return '\n'.join(lines)
if __name__=='__main__':
    out=BASE/'docs/obt-resultados.md';out.write_text(render());print('Generado '+str(out.relative_to(BASE)))
