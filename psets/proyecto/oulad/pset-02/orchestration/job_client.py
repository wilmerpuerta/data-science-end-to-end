"""Cliente Kestra: inicia/reutiliza un trabajo fijo y espera su estado agregado."""
import argparse,json,re,time,urllib.request,urllib.error
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['dbt','spark'],required=True)
p.add_argument('--execution-id',required=True);a=p.parse_args()
assert re.fullmatch('[A-Za-z0-9_-]{1,100}',a.execution_id)
base='http://'+a.kind+'-runner:8090'
def request(path,data=None):
    req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),
                               headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response:return json.loads(response.read())
try:
    state=request('/jobs',{'execution_id':a.execution_id})
    print(json.dumps({k:state[k] for k in ['component','job_id','attempt','state']}),flush=True)
    deadline=time.monotonic()+1300
    while time.monotonic()<deadline:
        state=request('/jobs/'+a.execution_id)
        if state['state'] in ['SUCCESS','FAILED']:
            print(json.dumps({k:state[k] for k in ['component','job_id','attempt','state']}),flush=True)
            raise SystemExit(0 if state['state']=='SUCCESS' else 1)
        time.sleep(3)
    raise SystemExit('Espera agotada: consultar estado antes de crear otra ejecución.')
except (urllib.error.URLError,TimeoutError):raise SystemExit('Ejecutor interno no disponible; no se muestran respuestas privadas.')
