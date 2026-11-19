"""Deriva evidencia Raw de informes sanitizados de ejecuciones reales."""
from pathlib import Path
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[2]
def main():
    reports=[];executions=[]
    for path in (ROOT/'pset-02/output/raw').glob('*.json'):
        value=json.loads(path.read_text());value['_path']=str(path.relative_to(ROOT/'pset-02'))
        (executions if path.name.startswith('execution_') else reports).append(value)
    complete=[r for r in reports if r.get('status')=='ok' and r.get('mode')=='load' and r.get('source_partition')=='all' and len(r.get('files',[]))==5]
    if not complete:raise SystemExit('No hay una carga completa comprobada.')
    initial=min(complete,key=lambda r:r['finished_at_utc'])
    noops=[r for r in complete if all(f['status']=='NOOP' for f in r['files'])]
    if not noops:raise SystemExit('Falta prueba completa de idempotencia.')
    latest=max(noops,key=lambda r:r['finished_at_utc'])
    manifest=json.loads((ROOT/'datasets/manifest.json').read_text())['files']
    for f in latest['files']:
        assert f['rows']==f['unique_source_rows']==manifest[f['file']]['rows'] and f['other_checksums']==0
    probes=[e for e in executions if e.get('state')=='SUCCESS' and e.get('inputs',{}).get('retry_probe') and max(e['task_attempt_counts'] or [0])>=2]
    backfills=[e for e in executions if e.get('state')=='SUCCESS' and e.get('inputs',{}).get('force_reload')]
    if not probes or not backfills:raise SystemExit('Falta evidencia de retry/backfill.')
    probe=probes[-1];backfill=backfills[-1]
    probe_reports=[r for r in reports if r.get('run_id')==probe['execution_id']]
    assert any(r.get('category')=='injected_transient_failure' for r in probe_reports)
    assert any(r.get('status')=='ok' for r in probe_reports)
    backfill_reports=[r for r in reports if r.get('run_id')==backfill['execution_id'] and r.get('status')=='ok']
    assert any(f['status']=='LOADED' and f['rows']==22 for r in backfill_reports for f in r['files'])
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'ok',
            'scope':'Evidencia de la etapa Raw. El avance posterior dbt/Spark se registra en sus informes específicos.',
            'initial_load_execution':initial['run_id'],'idempotence_execution':latest['run_id'],
            'tables':latest['files'],'total_source_rows':sum(f['rows'] for f in latest['files']),
            'source_value_checks':latest['source_value_checks'],
            'retry_probe':{'execution_id':probe['execution_id'],'controlled_failure':True,
                           'attempt_counts':probe['task_attempt_counts'],'final_state':probe['state']},
            'backfill':{'execution_id':backfill['execution_id'],'partition':'courses.csv','rows':22,'final_state':backfill['state']},
            'schedule':{'cron':'0 9 1,15 * *','timezone':'America/Guayaquil','enabled':False,
                        'scope':'Configurado y validado por Kestra; aún sin prueba de disparo temporal.'},
            'evidence':[initial['_path'],latest['_path'],probe['_path'],backfill['_path']],
            'limitations':['Un escritor mediante concurrencia=1; no ejecutar cargadores paralelos por fuera del flujo.',
                           'Backfill por fichero/checksum completo; no por módulo-edición en esta versión.',
                           'Retries acotados del proceso; errores permanentes también agotan los intentos, sin publicar datos inválidos.',
                           'No se cuantificó consumo monetario; el warehouse del proyecto se utilizó para COPY y verificaciones.']}
    target=ROOT/'pset-02/docs/ingesta-raw-verificacion.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f"Raw verificado: {result['total_source_rows']} filas; cinco NOOP; retry y backfill comprobados.")
if __name__=='__main__':main()
