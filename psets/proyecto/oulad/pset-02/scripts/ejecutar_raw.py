"""Publica/ejecuta el flujo Raw local; no imprime credenciales ni logs remotos."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,base64,json,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deploy',action='store_true')
    p.add_argument('--check-connection',action='store_true')
    p.add_argument('--file',choices=['all','studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv'],default='all')
    p.add_argument('--force-reload',action='store_true')
    p.add_argument('--retry-probe',action='store_true',help='Prueba controlada de retry, requiere --check-connection.')
    p.add_argument('--resume-execution',help='Consultar una ejecución ya iniciada, sin crear otra.')
    args=p.parse_args()
    if args.retry_probe and not args.check_connection:p.error('--retry-probe requiere --check-connection')
    settings=dict(line.split('=',1) for line in (ROOT/'pset-02/.env.infra').read_text().splitlines() if line and not line.startswith('#'))
    token=base64.b64encode(('admin@psets.local:'+settings['PSET2_KESTRA_PASSWORD']).encode()).decode()
    port=int(settings.get('PSET2_KESTRA_PORT','8080'));assert 1024<=port<=65535
    base=f'http://127.0.0.1:{port}/api/v1/main'
    def request(path,method='GET',data=None,ctype='application/x-yaml'):
        r=urllib.request.Request(base+path,method=method,data=data,headers={'Authorization':'Basic '+token,'Content-Type':ctype})
        with urllib.request.urlopen(r,timeout=30) as response:return json.loads(response.read())
    if args.deploy:
        content=(ROOT/'pset-02/kestra/oulad_raw.yml').read_bytes()
        try:request('/flows/pset2.oulad/oulad_raw')
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
            result=request('/flows','POST',content)
        else:result=request('/flows/pset2.oulad/oulad_raw','PUT',content)
        assert result['id']=='oulad_raw'
        print('Flujo pset2.oulad/oulad_raw desplegado; trigger periódico desactivado.',flush=True)
        return
    if args.resume_execution:
        import re
        if not re.fullmatch(r'[A-Za-z0-9_-]+',args.resume_execution):raise SystemExit('Identificador inválido')
        identifier=args.resume_execution
    else:
        fields={'source_file':args.file,'check_connection':str(args.check_connection).lower(),'force_reload':str(args.force_reload).lower(),'retry_probe':str(args.retry_probe).lower()}
        boundary='PSET2RawInputs'
        body=''.join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k,v in fields.items())+f'--{boundary}--\r\n'
        run=request('/executions/pset2.oulad/oulad_raw','POST',body.encode(),'multipart/form-data; boundary='+boundary)
        identifier=run['id']
    print('Kestra execution_id='+identifier,flush=True)
    deadline=time.monotonic()+1800
    while time.monotonic()<deadline:
        run=request('/executions/'+identifier);state=run['state']['current']
        if state in ['SUCCESS','FAILED','WARNING','KILLED','CANCELLED']:
            report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'execution_id':identifier,'state':state,
                    'task_attempt_counts':[len(t.get('attempts',[])) for t in run.get('taskRunList',[])],
                    'flow':'pset2.oulad/oulad_raw'}
            inputs=run.get('inputs',{}) or {}
            report['inputs']={k:inputs.get(k) is True for k in ['check_connection','force_reload','retry_probe']}
            if inputs.get('source_file') in ['all','studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv']:
                report['inputs']['source_file']=inputs['source_file']
            out=ROOT/'pset-02/output/raw';out.mkdir(parents=True,exist_ok=True)
            (out/('execution_'+identifier+'.json')).write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report),flush=True)
            if state!='SUCCESS':raise SystemExit('Consultar el informe sanitizado del cargador en pset-02/output/raw/. No copiar logs completos.')
            return
        time.sleep(3)
    raise SystemExit('Tiempo de espera agotado; la ejecución puede seguir activa. Reanudar consulta con --resume-execution, sin volver a lanzar la carga.')
if __name__=='__main__':
    try:main()
    except urllib.error.HTTPError as e:raise SystemExit(f'Kestra HTTP {e.code}; no se imprimen cabeceras ni cuerpo de la respuesta.')
    except urllib.error.URLError:raise SystemExit('API local no disponible. Comprobar estado de Kestra.')
