"""Ejecuta Spark sin exponer opciones cloud; recoge solo el informe agregado."""
from pathlib import Path
import argparse,json,re,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'pset-02'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['check-connection','test-features','build-obt'])
    a=p.parse_args();run=uuid.uuid4().hex
    artifacts=BASE/'.local/spark';artifacts.mkdir(parents=True,exist_ok=True)
    out=BASE/'output/spark';out.mkdir(parents=True,exist_ok=True)
    for name in ['.env.infra','.env.cloud']:
        if not (BASE/name).is_file():p.error('Preparar infraestructura y configuración privada primero.')
    cmd=['docker','compose','--project-directory',str(BASE),'--env-file',str(BASE/'.env.infra'),
         '--env-file',str(BASE/'.env.cloud'),'-f',str(BASE/'docker-compose.yml'),'-f',str(BASE/'docker-compose.cloud.yml'),
         'run','--rm','--no-deps','--entrypoint','/opt/spark/bin/spark-submit','spark',
         '--master','local[2]','--driver-memory','1g','--jars',
         '/opt/spark/oulad-jars/spark-snowflake_2.12-3.2.3-spark_3.5.jar,/opt/spark/oulad-jars/snowflake-jdbc-4.4.1.jar,/opt/spark/oulad-jars/parquet-avro-1.13.1.jar',
         '--conf','spark.ui.enabled=false','--conf','spark.sql.shuffle.partitions=16',
         '--conf','spark.sql.adaptive.enabled=true','--conf','spark.eventLog.enabled=false',
         '--conf','spark.redaction.regex=(?i)secret|password|token|access.?key|pem_private_key|sfurl|account',
         '/workspace/spark/test_features.py' if a.action=='test-features' else '/workspace/spark/build_obt.py',
         '--run-id',run]
    if a.action!='test-features':cmd+=['--action',a.action]
    print(json.dumps({'status':'running','action':a.action,'run_id':run}),flush=True)
    log=artifacts/(run+'.log')
    with log.open('w') as f:
        log.chmod(0o600)
        result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
    report_path=out/(run+'.json')
    if not report_path.exists():
        report={'status':'failed','action':a.action,'run_id':run,'returncode':result.returncode,
                'category':'runtime_without_report'}
    else:
        report=json.loads(report_path.read_text())
        assert report['run_id']==run and report['action']==a.action
    target={'check-connection':'spark-conexion.json','test-features':'spark-pruebas.json','build-obt':'obt-verificacion.json'}[a.action]
    (BASE/'docs'/target).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['output_columns','content_sha256_by_cutoff','per_cutoff']},ensure_ascii=False),flush=True)
    print('Informe: pset-02/docs/'+target,flush=True)
    return 0 if report['status']=='ok' and result.returncode==0 else 1
if __name__=='__main__':sys.exit(main())
