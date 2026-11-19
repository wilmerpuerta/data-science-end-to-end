"""Ejecuta dbt en Docker; publica únicamente evidencia agregada sin credenciales."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'pset-02'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['debug','parse','build-bronze','test-bronze','quality-export',
                                   'build-silver','test-silver','quality-export-silver',
                                   'build-gold','test-gold','quality-export-gold'])
    a=p.parse_args();artifacts=BASE/'.local/dbt';artifacts.mkdir(parents=True,exist_ok=True)
    for f in ['.env.infra','.env.cloud']:
        if not (BASE/f).is_file():p.error('Preparar infraestructura y configuración privada primero.')
    cmd=['docker','compose','--project-directory',str(BASE),'--env-file',str(BASE/'.env.infra'),
         '--env-file',str(BASE/'.env.cloud'),'-f',str(BASE/'docker-compose.yml'),
         '-f',str(BASE/'docker-compose.cloud.yml'),'run','--rm','--no-deps','--entrypoint','python',
         'dbt','/workspace/dbt/bootstrap.py',a.action]
    result=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT)
    # Salida completa privada. Nunca se copia automáticamente a docs ni al chat.
    log=artifacts/(a.action+'.txt');log.write_text(result.stdout+'\n'+result.stderr);log.chmod(0o600)
    checked=datetime.now(timezone.utc).isoformat()
    report={'checked_at_utc':checked,'action':a.action,'status':'ok' if result.returncode==0 else 'failed',
            'returncode':result.returncode,'dbt_core':'1.10.13','dbt_snowflake':'1.10.2'}
    quality_names={'quality-export':'calidad-bronze.json','quality-export-silver':'calidad-silver.json',
                   'quality-export-gold':'calidad-gold.json'}
    out=BASE/'docs'/quality_names.get(a.action,'dbt-'+a.action+'.json')
    if result.returncode:
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report));return result.returncode
    if a.action in quality_names:
        metrics=json.loads(result.stdout.strip())
        if not isinstance(metrics,list) or not all(set(m)=={'dataset','metric','value','denominator'} for m in metrics):
            raise ValueError('Unexpected quality report')
        report['metrics']=metrics
    elif a.action in ['build-bronze','test-bronze','build-silver','test-silver','build-gold','test-gold']:
        data=json.loads((artifacts/'target/run_results.json').read_text())
        report['elapsed_seconds']=round(data['elapsed_time'],2)
        report['results']=[{k:r[k] for k in ['unique_id','status','execution_time','failures']} for r in data['results']]
        if not all(r['status'] in ['success','pass'] for r in report['results']):raise ValueError('Unexpected node result')
        report['models_succeeded']=sum(r['status']=='success' for r in report['results'])
        report['tests_passed']=sum(r['status']=='pass' for r in report['results'])
        scopes={'build-silver':'Bronze y Silver','build-gold':'Bronze, Silver y Gold'}
        report['scope']=scopes.get(a.action,a.action)
    else:
        report['scope']='Conexión dbt verificada' if a.action=='debug' else 'Proyecto parseado sin consultas de datos'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['results','metrics']},ensure_ascii=False))
    print('Informe: '+str(out.relative_to(ROOT)))
    return 0

if __name__=='__main__':sys.exit(main())
