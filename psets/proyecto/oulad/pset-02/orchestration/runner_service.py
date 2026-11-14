"""Ejecutor HTTP interno: solo dbt build-gold o Spark build-obt, sin comandos libres."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import hashlib,json,os,re,signal,subprocess,sys,threading,time

KIND=sys.argv[1]
assert KIND in ['dbt','spark']
ARTIFACTS=Path('/workspace/artifacts');JOBS=ARTIFACTS/'runner-jobs';PUBLIC=Path('/workspace/pipeline')
JOBS.mkdir(parents=True,exist_ok=True);PUBLIC.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock();POOL=ThreadPoolExecutor(max_workers=1)
def utc():return datetime.now(timezone.utc).isoformat()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
for path in JOBS.glob('*.json'):
    state=json.loads(path.read_text())
    if state['state'] in ['RUNNING','QUEUED']:
        state.update(state='FAILED',finished_at_utc=utc(),category='worker_restarted');save(path,state)

def command(args,log,timeout):
    with log.open('w') as output:
        log.chmod(0o600)
        proc=subprocess.Popen(args,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        try:return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            return 124

def dbt_job(job):
    deadline=time.monotonic()+900
    code=command([sys.executable,'/workspace/dbt/bootstrap.py','build-gold'],JOBS/(job['job_id']+'.log'),900)
    result={'status':'ok' if code==0 else 'failed','returncode':code}
    if code:return result
    data=json.loads((ARTIFACTS/'target/run_results.json').read_text())
    nodes=[{k:r[k] for k in ['unique_id','status','execution_time','failures']} for r in data['results']]
    assert nodes and all(r['status'] in ['success','pass'] for r in nodes)
    result.update(results=nodes,models_succeeded=sum(r['status']=='success' for r in nodes),
                  tests_passed=sum(r['status']=='pass' for r in nodes),elapsed_seconds=round(data['elapsed_time'],2),
                  build_checked_at_utc=utc(),quality={},quality_checked_at_utc={})
    for layer,action in [('bronze','quality-export'),('silver','quality-export-silver'),('gold','quality-export-gold')]:
        log=JOBS/(job['job_id']+'-'+layer+'.log')
        code=command([sys.executable,'/workspace/dbt/bootstrap.py',action],log,max(1,int(deadline-time.monotonic())))
        if code:return {'status':'failed','returncode':code,'phase':'quality_'+layer}
        metrics=json.loads(log.read_text().strip())
        assert isinstance(metrics,list) and all(set(m)=={'dataset','metric','value','denominator'} for m in metrics)
        result['quality'][layer]=metrics
        result['quality_checked_at_utc'][layer]=utc()
    return result

def spark_job(job):
    args=['/opt/spark/bin/spark-submit','--master','local[2]','--driver-memory','1g','--jars',
          '/opt/spark/oulad-jars/spark-snowflake_2.12-3.2.3-spark_3.5.jar,/opt/spark/oulad-jars/snowflake-jdbc-4.4.1.jar,/opt/spark/oulad-jars/parquet-avro-1.13.1.jar',
          '--conf','spark.ui.enabled=false','--conf','spark.eventLog.enabled=false',
          '--conf','spark.sql.shuffle.partitions=16','--conf','spark.sql.adaptive.enabled=true',
          '--conf','spark.redaction.regex=(?i)secret|password|token|access.?key|pem_private_key|sfurl|account',
          '/workspace/spark/build_obt.py','--action','build-obt','--run-id',job['job_id']]
    code=command(args,JOBS/(job['job_id']+'.log'),1200)
    path=Path('/workspace/output')/(job['job_id']+'.json')
    if not path.exists():return {'status':'failed','returncode':code,'category':'runtime_without_report'}
    source=json.loads(path.read_text())
    allowed=['checked_at_utc','finished_at_utc','action','run_id','status','published','spark_version','scala_version',
             'spark_connector','jdbc','session_context_verified','autopushdown','gold_source_sha256_verified',
             'activity_rows_extracted','rows','unique_keys','per_cutoff','content_sha256_by_cutoff','output_columns',
             'temporal_tests_passed','readback_all_columns_equal','population_key_sets_equal','target_and_withdrawal_excluded',
             'source_manifest_sha256','destination','elapsed_seconds','category','phase','error_class','errno']
    result={k:source[k] for k in allowed if k in source};result['returncode']=code
    if code:result['status']='failed'
    return result

def run_job(job,state_path):
    with LOCK:job.update(state='RUNNING',started_at_utc=utc());save(state_path,job)
    try:report=dbt_job(job) if KIND=='dbt' else spark_job(job)
    except Exception as e:report={'status':'failed','error_class':type(e).__name__}
    with LOCK:
        job.update(state='SUCCESS' if report['status']=='ok' else 'FAILED',finished_at_utc=utc())
        report.update(component=KIND,execution_id=job['execution_id'],attempt=job['attempt'],job_id=job['job_id'],
                      started_at_utc=job['started_at_utc'],finished_at_utc=job['finished_at_utc'])
        folder=PUBLIC/job['execution_id'];save(folder/(KIND+'_attempt_'+str(job['attempt'])+'.json'),report)
        save(folder/(KIND+'.json'),report);save(state_path,job)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send(self,status,data):
        body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/health':return self.send(200,{'status':'ok','component':KIND})
        match=re.fullmatch('/jobs/([A-Za-z0-9_-]{1,100})',self.path)
        if not match:return self.send(404,{'error':'unknown_route'})
        with LOCK:
            path=JOBS/(match[1]+'.json')
            return self.send(200,json.loads(path.read_text())) if path.exists() else self.send(404,{'error':'unknown_job'})
    def do_POST(self):
        if self.path!='/jobs':return self.send(404,{'error':'unknown_route'})
        try:
            length=int(self.headers.get('Content-Length','0'));assert 0<length<=1024
            data=json.loads(self.rfile.read(length));assert set(data)=={'execution_id'}
            identifier=data['execution_id'];assert isinstance(identifier,str) and re.fullmatch('[A-Za-z0-9_-]{1,100}',identifier)
        except Exception:return self.send(400,{'error':'invalid_request'})
        with LOCK:
            path=JOBS/(identifier+'.json');previous=json.loads(path.read_text()) if path.exists() else None
            if previous and previous['state'] in ['QUEUED','RUNNING','SUCCESS']:return self.send(200,previous)
            attempt=previous['attempt']+1 if previous else 1
            job={'execution_id':identifier,'component':KIND,'attempt':attempt,'state':'QUEUED',
                 'job_id':hashlib.sha256((identifier+KIND+str(attempt)).encode()).hexdigest()[:32],'created_at_utc':utc()}
            save(path,job);POOL.submit(run_job,job.copy(),path);self.send(202,job)

if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8090),Handler).serve_forever()
