"""Despliega o ejecuta el flujo integral; muestra solo estados y evidencia curada."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,base64,json,re,subprocess,sys,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'pset-02'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--deploy',action='store_true')
    p.add_argument('--file',choices=['all','studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv'],default='all')
    p.add_argument('--force-reload',action='store_true');p.add_argument('--resume-execution')
    probes=p.add_mutually_exclusive_group();probes.add_argument('--retry-probe',action='store_true');probes.add_argument('--fail-after-raw',action='store_true')
    a=p.parse_args()
    settings=dict(line.split('=',1) for line in (BASE/'.env.infra').read_text().splitlines() if line and not line.startswith('#'))
    auth=base64.b64encode(('admin@psets.local:'+settings['PSET2_KESTRA_PASSWORD']).encode()).decode()
    port=int(settings.get('PSET2_KESTRA_PORT','8080'));assert 1024<=port<=65535
    base=f'http://127.0.0.1:{port}/api/v1/main'
    def request(path,method='GET',data=None,ctype='application/x-yaml'):
        req=urllib.request.Request(base+path,method=method,data=data,headers={'Authorization':'Basic '+auth,'Content-Type':ctype})
        try:
            with urllib.request.urlopen(req,timeout=30) as response:return json.loads(response.read())
        except urllib.error.HTTPError as e:
            private=BASE/'.local/orchestration';private.mkdir(parents=True,exist_ok=True)
            (private/'api-error.json').write_bytes(e.read());raise
    if a.deploy:
        subprocess.run([sys.executable,str(BASE/'scripts/ejecutar_raw.py'),'--deploy'],check=True)
        content=(BASE/'kestra/oulad_pipeline.yml').read_bytes()
        try:request('/flows/pset2.oulad/oulad_pipeline')
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
            result=request('/flows','POST',content)
        else:result=request('/flows/pset2.oulad/oulad_pipeline','PUT',content)
        assert result['id']=='oulad_pipeline'
        print('Flujo integral pset2.oulad/oulad_pipeline desplegado; ambos calendarios permanecen desactivados.');return 0
    if a.resume_execution:
        assert re.fullmatch('[A-Za-z0-9_-]{1,100}',a.resume_execution);identifier=a.resume_execution
    else:
        fields={'source_file':a.file,'force_reload':str(a.force_reload).lower(),'retry_probe':str(a.retry_probe).lower(),'fail_after_raw':str(a.fail_after_raw).lower()}
        boundary='PSET2PipelineInputs'
        body=''.join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k,v in fields.items())+f'--{boundary}--\r\n'
        identifier=request('/executions/pset2.oulad/oulad_pipeline','POST',body.encode(),'multipart/form-data; boundary='+boundary)['id']
    print('Kestra pipeline execution_id='+identifier,flush=True)
    deadline=time.monotonic()+4500;previous=None
    while time.monotonic()<deadline:
        run=request('/executions/'+identifier);state=run['state']['current']
        tasks=[{'task_id':r['taskId'],'state':r['state']['current'],'attempts':len(r.get('attempts',[])),
                'started_at':r['state'].get('startDate'),'finished_at':r['state'].get('endDate')} for r in run.get('taskRunList',[])]
        fingerprint=[(t['task_id'],t['state'],t['attempts']) for t in tasks]
        if fingerprint!=previous:print(json.dumps({'state':state,'tasks':tasks}),flush=True);previous=fingerprint
        if state in ['SUCCESS','FAILED','WARNING','KILLED','CANCELLED']:
            inputs=run.get('inputs',{}) or {}
            report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'execution_id':identifier,'state':state,
                    'flow':'pset2.oulad/oulad_pipeline','tasks':tasks,
                    'inputs':{k:inputs.get(k) is True for k in ['force_reload','retry_probe','fail_after_raw']}}
            if inputs.get('source_file') in ['all','studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv']:report['inputs']['source_file']=inputs['source_file']
            child=(run.get('outputs',{}).get('raw',{}) or {}).get('executionId')
            if not child:
                raw_task=next((t for t in run.get('taskRunList',[]) if t['taskId']=='raw'),{})
                child=(raw_task.get('outputs') or {}).get('executionId')
            if child and re.fullmatch('[A-Za-z0-9_-]{1,100}',child):report['raw_execution_id']=child
            folder=BASE/'output/pipeline'/identifier;folder.mkdir(parents=True,exist_ok=True)
            (folder/'execution.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps(report,ensure_ascii=False),flush=True)
            if state=='SUCCESS':assert json.loads((folder/'verification.json').read_text())['status']=='ok'
            return 0 if state=='SUCCESS' else 1
        time.sleep(3)
    raise SystemExit('Espera agotada; el flujo puede seguir activo. Consultar con --resume-execution, sin crear otro.')
if __name__=='__main__':
    try:sys.exit(main())
    except urllib.error.HTTPError as e:raise SystemExit('Kestra HTTP '+str(e.code)+'. Diagnóstico local privado; no se imprime el cuerpo.')
    except urllib.error.URLError:raise SystemExit('Kestra no disponible. Comprobar infraestructura local.')
